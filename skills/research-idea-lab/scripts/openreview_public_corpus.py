#!/usr/bin/env python3
"""Collect only publicly readable OpenReview review chains."""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SCHEMA_VERSION = "openreview-public-corpus/v1"
DEFAULT_API_BASE = "https://api2.openreview.net"
USER_AGENT = "research-idea-lab/1.0 public-review-corpus"
OPENREVIEW_TERMS_URL = "https://openreview.net/legal/terms"
DEFAULT_SCOPE_FILE = (
    Path(__file__).resolve().parent.parent / "references" / "ai-venue-scope.json"
)
EXIT_CHALLENGE = 3
EXIT_API_ERROR = 4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{os.getpid()}"


def safe_slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower()
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]
    return f"{cleaned[:80]}-{digest}"


def load_venue_scope(path: Path) -> Dict[str, Any]:
    scope = json.loads(path.read_text(encoding="utf-8"))
    if scope.get("schema_version") != "ai-openreview-venues/v2":
        raise ValueError(f"Unsupported venue scope schema in {path}")
    if not isinstance(scope.get("venues"), list):
        raise ValueError(f"Venue scope in {path} is missing venues")
    if not isinstance(scope.get("source_types"), dict):
        raise ValueError(f"Venue scope in {path} is missing source_types")
    return scope


def match_venue_scope(
    query: str,
    scope: Dict[str, Any],
    allow_subpath: bool = False,
) -> Optional[Dict[str, Any]]:
    for venue in scope["venues"]:
        pattern = str(venue["pattern"])
        effective_pattern = pattern
        if allow_subpath and pattern.endswith("$"):
            effective_pattern = pattern[:-1] + r"(?:/|$)"
        if re.match(effective_pattern, query):
            source_type = venue.get("source_type", "main-conference")
            source_rules = scope["source_types"].get(source_type)
            if not source_rules:
                raise ValueError(f"Unknown source type {source_type!r}")
            return {
                "family": venue["family"],
                "category": venue["category"],
                "priority": venue["priority"],
                "source_type": source_type,
                "evidence_role": source_rules["evidence_role"],
                "allowed_uses": source_rules["allowed_uses"],
                "forbidden_uses": source_rules["forbidden_uses"],
                "openreview_verified": venue.get("openreview_verified", False),
                "scope_schema": scope["schema_version"],
            }
    return None


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def atomic_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(temporary, path)


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_jsonl_by_id(path: Path, key: str) -> Dict[str, Dict[str, Any]]:
    values: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return values
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if key not in row:
                raise ValueError(f"{path}:{line_number} is missing {key}")
            values[str(row[key])] = row
    return values


class ChallengeRequired(RuntimeError):
    def __init__(self, message: str, challenge_url: Optional[str]) -> None:
        super().__init__(message)
        self.challenge_url = challenge_url


class OpenReviewAPIError(RuntimeError):
    pass


class PublicOpenReviewClient:
    def __init__(
        self,
        api_base: str,
        token_env: str,
        cookie_env: str,
        timeout: int,
        retries: int,
    ) -> None:
        self.api_base = api_base.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.headers = {
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        token = os.environ.get(token_env)
        cookie = os.environ.get(cookie_env)
        if token:
            self.headers["Authorization"] = "Bearer " + token.removeprefix("Bearer ").strip()
        if cookie:
            self.headers["Cookie"] = cookie
        self.auth_mode = (
            "token" if token else "browser-cookie" if cookie else "guest"
        )

    def get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        query = urlencode(
            [(key, item) for key, value in params.items()
             for item in (value if isinstance(value, list) else [value])]
        )
        url = f"{self.api_base}{path}?{query}"
        for attempt in range(self.retries + 1):
            request = Request(url, headers=self.headers, method="GET")
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as error:
                payload = self._error_payload(error)
                name = str(payload.get("name", ""))
                details = payload.get("details") or {}
                if error.code == 403 and name == "ChallengeRequiredError":
                    raise ChallengeRequired(
                        str(payload.get("message", "Challenge verification required")),
                        details.get("challengeUrl"),
                    ) from error
                if error.code == 429 or 500 <= error.code < 600:
                    if attempt < self.retries:
                        delay = min(2 ** attempt, 16)
                        logging.warning(
                            "OpenReview returned HTTP %s; retrying in %ss",
                            error.code,
                            delay,
                        )
                        time.sleep(delay)
                        continue
                raise OpenReviewAPIError(
                    f"HTTP {error.code} from {url}: "
                    f"{payload.get('name', '')} {payload.get('message', '')}".strip()
                ) from error
            except URLError as error:
                if attempt < self.retries:
                    delay = min(2 ** attempt, 16)
                    logging.warning("Network error; retrying in %ss: %s", delay, error)
                    time.sleep(delay)
                    continue
                raise OpenReviewAPIError(f"Network error requesting {url}: {error}") from error
        raise AssertionError("unreachable")

    @staticmethod
    def _error_payload(error: HTTPError) -> Dict[str, Any]:
        try:
            return json.loads(error.read().decode("utf-8"))
        except Exception:
            return {"name": "HTTPError", "message": str(error)}

    def notes(
        self,
        *,
        venue_id: Optional[str],
        invitation: Optional[str],
        limit: int,
        offset: int,
        details: str = "replies",
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "details": details,
        }
        if venue_id:
            params["content.venueid"] = venue_id
        if invitation:
            params["invitation"] = invitation
        return self.get("/notes", params)


def reader_ids(note: Dict[str, Any]) -> List[str]:
    return [str(reader).lower() for reader in note.get("readers", [])]


def is_public_note(note: Dict[str, Any]) -> bool:
    return "everyone" in reader_ids(note)


def unwrap_public_value(value: Any) -> Any:
    if not isinstance(value, dict) or "value" not in value:
        return value
    readers = [str(reader).lower() for reader in value.get("readers", [])]
    if readers and "everyone" not in readers:
        return None
    return value.get("value")


def public_content(note: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in (note.get("content") or {}).items():
        public_value = unwrap_public_value(value)
        if public_value is not None:
            result[key] = public_value
    return result


def invitation_text(note: Dict[str, Any]) -> str:
    invitations = note.get("invitations") or []
    if not invitations and note.get("invitation"):
        invitations = [note["invitation"]]
    return " ".join(str(value) for value in invitations).lower()


def classify_reply(note: Dict[str, Any]) -> str:
    invitation = invitation_text(note)
    keys = {str(key).lower() for key in (note.get("content") or {}).keys()}
    signatures = " ".join(str(value) for value in note.get("signatures", [])).lower()
    if "decision" in invitation or "decision" in keys:
        return "decisions"
    if any(token in invitation for token in ("meta_review", "metareview", "meta-review")):
        return "meta_reviews"
    if any(token in invitation for token in ("rebuttal", "author_response", "author-response")):
        return "author_responses"
    if "authors" in signatures and "official_comment" in invitation:
        return "author_responses"
    if any(token in invitation for token in ("official_review", "/review", "-/review")):
        return "official_reviews"
    if keys.intersection({"strengths", "weaknesses", "rating", "recommendation", "confidence"}):
        return "official_reviews"
    return "public_comments"


def normalize_note(note: Dict[str, Any]) -> Dict[str, Any]:
    invitations = note.get("invitations") or []
    if not invitations and note.get("invitation"):
        invitations = [note["invitation"]]
    return {
        "note_id": note.get("id"),
        "forum_id": note.get("forum"),
        "reply_to": note.get("replyto"),
        "invitations": invitations,
        "signatures": note.get("signatures", []),
        "readers": note.get("readers", []),
        "created_millis": note.get("cdate"),
        "modified_millis": note.get("mdate") or note.get("tmdate"),
        "content": public_content(note),
    }


def normalize_forum(
    submission: Dict[str, Any],
    venue_id: Optional[str],
    source_url: str,
    venue_scope: Dict[str, Any],
) -> Dict[str, Any]:
    grouped = {
        "official_reviews": [],
        "author_responses": [],
        "meta_reviews": [],
        "decisions": [],
        "public_comments": [],
    }
    skipped_nonpublic = 0
    replies = (submission.get("details") or {}).get("replies", [])
    for reply in replies:
        if not is_public_note(reply):
            skipped_nonpublic += 1
            continue
        grouped[classify_reply(reply)].append(normalize_note(reply))
    forum_id = submission.get("forum") or submission.get("id")
    return {
        "schema_version": SCHEMA_VERSION,
        "forum_id": forum_id,
        "venue_id": venue_id,
        "venue_scope": venue_scope,
        "source_url": f"https://openreview.net/forum?id={forum_id}",
        "api_source": source_url,
        "source_terms_url": OPENREVIEW_TERMS_URL,
        "retrieved_at": utc_now(),
        "submission": normalize_note(submission),
        **grouped,
        "public_chain_counts": {key: len(value) for key, value in grouped.items()},
        "skipped_nonpublic_replies": skipped_nonpublic,
    }


def configure_logging(log_path: Path, verbose: bool) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handlers: List[logging.Handler] = [
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ]
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
        force=True,
    )


def storage_paths(project_root: Path, query_name: str, current_run_id: str) -> Dict[str, Path]:
    base = project_root / "research_state" / "review_patterns"
    slug = safe_slug(query_name)
    return {
        "base": base,
        "forums": base / "sources" / "openreview" / slug / "forums.jsonl",
        "checkpoint": base / "checkpoints" / f"{slug}.json",
        "manifest": base / "corpus_manifest.jsonl",
        "log": base / "logs" / f"openreview-{slug}-{current_run_id}.log",
        "events": project_root / "research_state" / "logs" / "research_events.jsonl",
    }


def query_name(args: argparse.Namespace) -> str:
    return args.venue_id or args.invitation


def manifest_base(
    args: argparse.Namespace,
    client: PublicOpenReviewClient,
    current_run_id: str,
) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": current_run_id,
        "started_at": utc_now(),
        "api_base": client.api_base,
        "auth_mode": client.auth_mode,
        "venue_id": args.venue_id,
        "invitation": args.invitation,
        "public_only": True,
        "source_terms_url": OPENREVIEW_TERMS_URL,
        "venue_scope": args.venue_scope,
    }


def record_terminal(
    paths: Dict[str, Path],
    manifest: Dict[str, Any],
    status: str,
    **details: Any,
) -> None:
    row = {
        **manifest,
        "status": status,
        "finished_at": utc_now(),
        **details,
    }
    append_jsonl(paths["manifest"], row)
    append_jsonl(
        paths["events"],
        {
            "event": "openreview-public-corpus",
            "run_id": manifest["run_id"],
            "status": status,
            "venue_id": manifest.get("venue_id"),
            "invitation": manifest.get("invitation"),
            "timestamp": row["finished_at"],
            "details": details,
        },
    )


def coverage_summary(forums: List[Dict[str, Any]]) -> Dict[str, Any]:
    chain_types = (
        "official_reviews",
        "author_responses",
        "meta_reviews",
        "decisions",
        "public_comments",
    )
    decision_outcomes = {"accept": 0, "reject": 0, "other": 0}
    for forum in forums:
        for decision in forum["decisions"]:
            value = str(decision["content"].get("decision", "")).lower()
            if "accept" in value:
                decision_outcomes["accept"] += 1
            elif "reject" in value:
                decision_outcomes["reject"] += 1
            else:
                decision_outcomes["other"] += 1
    public_review_count = sum(len(forum["official_reviews"]) for forum in forums)
    public_decision_count = sum(len(forum["decisions"]) for forum in forums)
    public_meta_count = sum(len(forum["meta_reviews"]) for forum in forums)
    venue_scope = forums[0].get("venue_scope", {}) if forums else {}
    source_type = venue_scope.get("source_type", "unknown")
    allowed_uses = venue_scope.get("allowed_uses", [])
    forbidden_uses = venue_scope.get("forbidden_uses", [])
    chain_supports_fatal = source_type in ("main-conference", "journal")
    return {
        "sampled_submissions": len(forums),
        "public_submissions": len(forums),
        "with_public_chain": {
            key: sum(bool(forum[key]) for forum in forums) for key in chain_types
        },
        "total_public_notes": {
            key: sum(len(forum[key]) for forum in forums) for key in chain_types
        },
        "skipped_nonpublic_replies": sum(
            forum["skipped_nonpublic_replies"] for forum in forums
        ),
        "decision_outcomes": decision_outcomes,
        "source_type": source_type,
        "evidence_role": venue_scope.get("evidence_role"),
        "allowed_uses": allowed_uses,
        "forbidden_uses": forbidden_uses,
        "corpus_eligibility": {
            "review_advice": public_review_count > 0,
            "decision_linked_patterns": (
                public_review_count > 0 and public_decision_count > 0
            ),
            "fatal_or_decision_driving_patterns": (
                chain_supports_fatal
                and
                public_review_count > 0
                and public_decision_count > 0
                and public_meta_count > 0
            ),
            "observed_rejection_patterns": decision_outcomes["reject"] > 0,
            "top_conference_calibration": (
                source_type == "main-conference"
                and "top-conference-calibration" in allowed_uses
                and public_review_count > 0
                and public_decision_count > 0
            ),
        },
    }


def probe(
    args: argparse.Namespace,
    client: PublicOpenReviewClient,
    paths: Dict[str, Path],
    manifest: Dict[str, Any],
) -> int:
    logging.info("Probing public OpenReview coverage for %s", query_name(args))
    try:
        payload = client.notes(
            venue_id=args.venue_id,
            invitation=args.invitation,
            limit=args.sample_size,
            offset=0,
        )
    except ChallengeRequired as error:
        logging.error("OpenReview challenge required: %s", error)
        record_terminal(
            paths,
            manifest,
            "blocked-challenge",
            challenge_url=error.challenge_url,
            message=str(error),
        )
        print(json.dumps({
            "status": "blocked-challenge",
            "challenge_url": error.challenge_url,
        }, ensure_ascii=False, indent=2))
        return EXIT_CHALLENGE
    except OpenReviewAPIError as error:
        logging.error("%s", error)
        record_terminal(paths, manifest, "api-error", message=str(error))
        return EXIT_API_ERROR

    forums = [
        normalize_forum(note, args.venue_id, client.api_base, args.venue_scope)
        for note in payload.get("notes", [])
        if is_public_note(note)
    ]
    summary = {
        "status": "complete",
        "reported_submission_count": payload.get("count"),
        **coverage_summary(forums),
    }
    record_terminal(paths, manifest, "complete", mode="probe", coverage=summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def collect(
    args: argparse.Namespace,
    client: PublicOpenReviewClient,
    paths: Dict[str, Path],
    manifest: Dict[str, Any],
) -> int:
    existing = load_jsonl_by_id(paths["forums"], "forum_id")
    checkpoint: Dict[str, Any] = {}
    if args.resume and paths["checkpoint"].exists():
        checkpoint = json.loads(paths["checkpoint"].read_text(encoding="utf-8"))
    offset = int(checkpoint.get("next_offset", 0)) if args.resume else 0
    collected_this_run = 0
    skipped_nonpublic_submissions = 0
    logging.info(
        "Collecting public OpenReview forums for %s from offset %s",
        query_name(args),
        offset,
    )

    try:
        while True:
            if args.max_submissions and collected_this_run >= args.max_submissions:
                break
            requested = args.page_size
            if args.max_submissions:
                requested = min(
                    requested,
                    args.max_submissions - collected_this_run,
                )
            payload = client.notes(
                venue_id=args.venue_id,
                invitation=args.invitation,
                limit=requested,
                offset=offset,
            )
            notes = payload.get("notes", [])
            if not notes:
                break
            for note in notes:
                if not is_public_note(note):
                    skipped_nonpublic_submissions += 1
                    continue
                forum = normalize_forum(
                    note, args.venue_id, client.api_base, args.venue_scope
                )
                existing[str(forum["forum_id"])] = forum
                collected_this_run += 1
            offset += len(notes)
            atomic_jsonl(
                paths["forums"],
                [existing[key] for key in sorted(existing)],
            )
            atomic_json(
                paths["checkpoint"],
                {
                    "schema_version": SCHEMA_VERSION,
                    "query": query_name(args),
                    "next_offset": offset,
                    "stored_forums": len(existing),
                    "updated_at": utc_now(),
                },
            )
            logging.info(
                "Stored %s forums; next offset %s",
                len(existing),
                offset,
            )
            if len(notes) < requested:
                break
    except ChallengeRequired as error:
        logging.error("OpenReview challenge required: %s", error)
        record_terminal(
            paths,
            manifest,
            "blocked-challenge",
            mode="collect",
            challenge_url=error.challenge_url,
            next_offset=offset,
            stored_forums=len(existing),
            message=str(error),
        )
        return EXIT_CHALLENGE
    except (OpenReviewAPIError, ValueError, json.JSONDecodeError) as error:
        logging.error("%s", error)
        record_terminal(
            paths,
            manifest,
            "error",
            mode="collect",
            next_offset=offset,
            stored_forums=len(existing),
            message=str(error),
        )
        return EXIT_API_ERROR

    forums = list(existing.values())
    summary = coverage_summary(forums)
    record_terminal(
        paths,
        manifest,
        "complete",
        mode="collect",
        next_offset=offset,
        collected_this_run=collected_this_run,
        stored_forums=len(existing),
        skipped_nonpublic_submissions=skipped_nonpublic_submissions,
        coverage=summary,
        corpus_path=str(paths["forums"]),
    )
    logging.info("Collection complete: %s", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ingest(
    args: argparse.Namespace,
    client: PublicOpenReviewClient,
    paths: Dict[str, Path],
    manifest: Dict[str, Any],
) -> int:
    existing = load_jsonl_by_id(paths["forums"], "forum_id")
    imported = 0
    skipped_nonpublic_submissions = 0
    input_records = []
    try:
        for input_path_value in args.input_json:
            input_path = input_path_value.resolve()
            payload = json.loads(input_path.read_text(encoding="utf-8"))
            notes = payload.get("notes")
            if not isinstance(notes, list):
                raise ValueError(f"{input_path} does not contain a notes list")
            for note in notes:
                if not is_public_note(note):
                    skipped_nonpublic_submissions += 1
                    continue
                content_venue = public_content(note).get("venueid")
                if args.venue_id and content_venue != args.venue_id:
                    raise ValueError(
                        f"{input_path} contains note {note.get('id')} for "
                        f"{content_venue!r}, expected {args.venue_id!r}"
                    )
                forum = normalize_forum(
                    note, args.venue_id, client.api_base, args.venue_scope
                )
                existing[str(forum["forum_id"])] = forum
                imported += 1
            input_records.append({
                "path": str(input_path),
                "sha256": file_sha256(input_path),
                "reported_count": payload.get("count"),
                "page_notes": len(notes),
            })
        atomic_jsonl(
            paths["forums"],
            [existing[key] for key in sorted(existing)],
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        logging.error("%s", error)
        record_terminal(
            paths,
            manifest,
            "error",
            mode="browser-ingest",
            message=str(error),
            input_files=input_records,
        )
        return EXIT_API_ERROR

    summary = coverage_summary(list(existing.values()))
    record_terminal(
        paths,
        manifest,
        "complete",
        mode="browser-ingest",
        imported_this_run=imported,
        stored_forums=len(existing),
        skipped_nonpublic_submissions=skipped_nonpublic_submissions,
        input_files=input_records,
        coverage=summary,
        corpus_path=str(paths["forums"]),
    )
    logging.info("Browser export ingest complete: %s", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def browser_plan(
    args: argparse.Namespace,
    client: PublicOpenReviewClient,
    paths: Dict[str, Path],
    manifest: Dict[str, Any],
) -> int:
    if not args.reported_count or args.reported_count < 1:
        raise SystemExit("browser-plan requires --reported-count greater than zero")
    if not args.max_submissions or args.max_submissions < 1:
        raise SystemExit("browser-plan requires --max-submissions greater than zero")
    count = min(args.reported_count, args.max_submissions)
    page_size = args.browser_page_size
    pages = []
    for offset in range(0, count, page_size):
        limit = min(page_size, count - offset)
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "details": "replies",
        }
        if args.venue_id:
            params["content.venueid"] = args.venue_id
        else:
            params["invitation"] = args.invitation
        pages.append({
            "offset": offset,
            "limit": limit,
            "url": f"{client.api_base}/notes?{urlencode(params)}",
            "status": "pending",
        })
    plan_path = (
        paths["base"]
        / "browser_import"
        / safe_slug(query_name(args))
        / "plan.json"
    )
    plan = {
        "schema_version": SCHEMA_VERSION,
        "mode": "browser-plan",
        "query": query_name(args),
        "venue_scope": args.venue_scope,
        "reported_count": args.reported_count,
        "planned_submissions": count,
        "browser_page_size": page_size,
        "created_at": utc_now(),
        "pages": pages,
    }
    atomic_json(plan_path, plan)
    record_terminal(
        paths,
        manifest,
        "complete",
        mode="browser-plan",
        plan_path=str(plan_path),
        planned_pages=len(pages),
        planned_submissions=count,
    )
    print(json.dumps({
        "status": "complete",
        "plan_path": str(plan_path),
        "planned_pages": len(pages),
        "planned_submissions": count,
    }, ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Audit or collect publicly readable OpenReview review chains."
    )
    result.add_argument(
        "command",
        choices=("probe", "collect", "ingest", "browser-plan"),
    )
    result.add_argument("project_root", type=Path)
    query = result.add_mutually_exclusive_group(required=True)
    query.add_argument("--venue-id")
    query.add_argument("--invitation")
    result.add_argument("--api-base", default=DEFAULT_API_BASE)
    result.add_argument("--token-env", default="OPENREVIEW_ACCESS_TOKEN")
    result.add_argument("--cookie-env", default="OPENREVIEW_COOKIE")
    result.add_argument("--timeout", type=int, default=30)
    result.add_argument("--retries", type=int, default=3)
    result.add_argument("--sample-size", type=int, default=5)
    result.add_argument("--page-size", type=int, default=100)
    result.add_argument("--max-submissions", type=int, default=0)
    result.add_argument("--reported-count", type=int, default=0)
    result.add_argument("--browser-page-size", type=int, default=1)
    result.add_argument("--scope-file", type=Path, default=DEFAULT_SCOPE_FILE)
    result.add_argument(
        "--input-json",
        type=Path,
        action="append",
        default=[],
        help="Browser-exported public API JSON page; repeat for multiple pages.",
    )
    result.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True)
    result.add_argument("--verbose", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    if not 1 <= args.sample_size <= 100:
        raise SystemExit("--sample-size must be between 1 and 100")
    if not 1 <= args.page_size <= 1000:
        raise SystemExit("--page-size must be between 1 and 1000")
    if args.max_submissions < 0:
        raise SystemExit("--max-submissions cannot be negative")
    if not 1 <= args.browser_page_size <= 10:
        raise SystemExit("--browser-page-size must be between 1 and 10")
    if args.command == "ingest" and not args.input_json:
        raise SystemExit("ingest requires at least one --input-json")
    if args.command != "ingest" and args.input_json:
        raise SystemExit("--input-json is only valid with ingest")

    project_root = args.project_root.resolve()
    try:
        scope = load_venue_scope(args.scope_file.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"Invalid AI venue scope: {error}") from error
    matched_scope = match_venue_scope(
        query_name(args),
        scope,
        allow_subpath=bool(args.invitation),
    )
    if matched_scope is None:
        raise SystemExit(
            f"Venue is outside the approved AI conference scope: {query_name(args)}"
        )
    args.venue_scope = matched_scope
    current_run_id = run_id()
    paths = storage_paths(project_root, query_name(args), current_run_id)
    configure_logging(paths["log"], args.verbose)
    client = PublicOpenReviewClient(
        args.api_base,
        args.token_env,
        args.cookie_env,
        args.timeout,
        args.retries,
    )
    if args.command in ("ingest", "browser-plan"):
        client.auth_mode = "browser-verified-export"
    manifest = manifest_base(args, client, current_run_id)
    logging.info(
        "Starting %s with auth mode %s; credentials are not persisted",
        args.command,
        client.auth_mode,
    )
    if args.command == "probe":
        return probe(args, client, paths, manifest)
    if args.command == "ingest":
        return ingest(args, client, paths, manifest)
    if args.command == "browser-plan":
        return browser_plan(args, client, paths, manifest)
    return collect(args, client, paths, manifest)


if __name__ == "__main__":
    raise SystemExit(main())
