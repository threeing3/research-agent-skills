from __future__ import annotations

import json
import hashlib
import datetime as dt
import io
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"


def canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def run_script(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )


class PaperProject:
    def __init__(self, root: Path) -> None:
        self.root = root
        (root / "paper").mkdir()
        (root / "plan/task-packets").mkdir(parents=True)
        (root / "paper/main.tex").write_text(
            """\\documentclass{article}
\\begin{document}
\\begin{abstract}A supported claim.\\end{abstract}
\\section{Introduction}Prior work exists~\\cite{demo_2026_work}.
\\section{Limitations}This fixture is intentionally small.
\\bibliographystyle{plain}
\\bibliography{references}
\\end{document}
""",
            encoding="utf-8",
        )
        (root / "paper/references.bib").write_text(
            "@article{demo_2026_work, title={A Work}, author={Demo, A.}, year={2026}}\n",
            encoding="utf-8",
        )
        (root / "paper/main.pdf").write_bytes(b"%PDF-1.4\nfixture\n")
        (root / "paper_story.md").write_text("# Story\n\nA bounded thesis.\n", encoding="utf-8")
        (root / "claim_evidence_map.md").write_text(
            "# Claims\n\n| Claim | Evidence | Status |\n|---|---|---|\n| A claim | fixture | Supported |\n",
            encoding="utf-8",
        )
        (root / "citation_verification.md").write_text(
            "# Citations\n\n| Key | Source | Status |\n|---|---|---|\n| `demo_2026_work` | DOI | verified |\n",
            encoding="utf-8",
        )
        citation_entries = [
            {
                "key": "demo_2026_work",
                "identifier": "doi:10.0000/demo",
                "claim_support": [
                    {
                        "claim": "Prior work exists.",
                        "relation": "background",
                        "status": "verified",
                        "evidence": "Fixture evidence.",
                        "source": "fixture",
                    }
                ],
            }
        ]
        (root / "citation_requests.json").write_text(
            json.dumps({"schema_version": "ai-research-writing/citation-requests-v1", "entries": citation_entries}),
            encoding="utf-8",
        )
        metadata = {"title": "A Work", "authors": ["A. Demo"], "year": 2026, "doi": "10.0000/demo"}
        (root / "citation_lock.json").write_text(
            json.dumps(
                {
                    "schema_version": "ai-research-writing/citation-lock-v1",
                    "request_sha256": canonical_digest(citation_entries),
                    "records": [
                        {
                            "key": "demo_2026_work",
                            "identifier": "doi:10.0000/demo",
                            "status": "verified",
                            "provider": "crossref",
                            "request_url": "https://api.crossref.org/works/10.0000%2Fdemo",
                            "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                            "metadata": metadata,
                            "metadata_sha256": canonical_digest(metadata),
                            "claim_support_sha256": canonical_digest(citation_entries[0]["claim_support"]),
                            "cross_check": None,
                            "cross_check_sha256": canonical_digest(None),
                            "error": "",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (root / "build_check.md").write_text("# Build\n\nBuild passed.\n", encoding="utf-8")
        (root / "plan/progress.md").write_text("# Progress\n\nVerification run: passed.\n", encoding="utf-8")
        (root / "plan/task-packets/write.md").write_text("# Task\n\nAcceptance criteria recorded.\n", encoding="utf-8")
        state = {
            "schema_version": "ai-research-writing/paper-state-v1",
            "mode": "full-paper",
            "stage": "complete",
            "target_venue": "Test Venue 2026",
            "main_tex": "paper/main.tex",
            "bibliography": "paper/references.bib",
            "required_artifacts": [],
            "blockers": [],
            "build": {
                "status": "passed",
                "command": "fixture build",
                "pdf": "paper/main.pdf",
                "external_inputs": [],
                "input_sha256": "pending",
                "pdf_sha256": "pending",
            },
        }
        (root / "paper_state.json").write_text(json.dumps(state), encoding="utf-8")

    def record_build(self) -> None:
        result = run_script("record_build.py", self.root)
        if result.returncode != 0:
            raise AssertionError(result.stderr or result.stdout)


class QualityGateTests(unittest.TestCase):
    def test_valid_full_paper_contract_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            project.record_build()
            result = run_script("research_quality_gate.py", project.root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_terminal_progress_cannot_remain_pending(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            project.record_build()
            (project.root / "plan/progress.md").write_text("Verification planned: citation check.\n", encoding="utf-8")
            result = run_script("research_quality_gate.py", project.root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("verification as pending", result.stdout)

    def test_missing_latex_input_fails_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            with (project.root / "paper/main.tex").open("a", encoding="utf-8") as handle:
                handle.write("\\input{missing-section}\n")
            result = run_script("check_citations.py", project.root / "paper/main.tex", project.root / "paper/references.bib")
            self.assertEqual(result.returncode, 2)
            self.assertIn("Missing LaTeX input", result.stderr)

    def test_cited_key_requires_verified_record(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            project.record_build()
            (project.root / "citation_verification.md").write_text(
                "| Key | Source | Status |\n|---|---|---|\n| `other` | DOI | verified |\n",
                encoding="utf-8",
            )
            result = run_script("research_quality_gate.py", project.root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("lack a verified citation record", result.stdout)

    def test_changed_source_invalidates_recorded_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            project.record_build()
            with (project.root / "paper/main.tex").open("a", encoding="utf-8") as handle:
                handle.write("% changed after build\n")
            result = run_script("research_quality_gate.py", project.root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Build input digest is stale", result.stdout)

    def test_unknown_state_field_fails_strict_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            project.record_build()
            state_path = project.root / "paper_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["silent_fallback"] = True
            state_path.write_text(json.dumps(state), encoding="utf-8")
            result = run_script("research_quality_gate.py", project.root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("contains unknown fields: silent_fallback", result.stdout)

    def test_record_build_refuses_pdf_older_than_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            os.utime(project.root / "paper/main.pdf", ns=(1, 1))
            with (project.root / "paper/main.tex").open("a", encoding="utf-8") as handle:
                handle.write("% source changed after PDF generation\n")
            result = run_script("record_build.py", project.root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("PDF is older than one or more build inputs", result.stderr)

    def test_submission_ready_requires_executed_build_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            state_path = project.root / "paper_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["stage"] = "submission-ready"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            project.record_build()
            result = run_script("research_quality_gate.py", project.root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("requires record_build.py --run", result.stdout)

    def test_record_build_run_executes_command_and_records_log(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            build_script = project.root / "paper/build_fixture.py"
            build_script.write_text(
                "from pathlib import Path\nPath('main.pdf').write_bytes(b'%PDF-1.4\\nexecuted\\n')\n",
                encoding="utf-8",
            )
            state_path = project.root / "paper_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["stage"] = "submission-ready"
            state["build"]["command"] = f"{sys.executable} build_fixture.py"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            result = run_script("record_build.py", project.root, "--run")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            recorded = json.loads(state_path.read_text(encoding="utf-8"))["build"]
            self.assertEqual(recorded["attestation"], "executed")
            self.assertEqual(recorded["exit_code"], 0)
            self.assertTrue((project.root / recorded["log"]).is_file())
            gate = run_script("research_quality_gate.py", project.root)
            self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)

    def test_unreadable_text_is_not_silently_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "bad.tex"
            bad.write_bytes(b"\xff\xfe\x00")
            result = run_script("check_todos.py", bad)
            self.assertEqual(result.returncode, 2)
            self.assertIn("not valid UTF-8", result.stderr)

    def test_quality_gate_enforces_declared_numeric_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            with (project.root / "paper/main.tex").open("a", encoding="utf-8") as handle:
                handle.write("\\section{Results}Measured accuracy is 91.2 percent.\n")
            (project.root / "results.json").write_text('{"accuracy": 0.8}\n', encoding="utf-8")
            (project.root / "numeric_evidence.json").write_text(
                json.dumps(
                    {
                        "schema_version": "ai-research-writing/numeric-evidence-v2",
                        "entries": [{
                            "value": 0.8,
                            "source": "results.json",
                            "selector": {"kind": "json-pointer", "pointer": "/accuracy"},
                            "representations": ["percent"],
                        }],
                    }
                ),
                encoding="utf-8",
            )
            (project.root / "paper/main.pdf").write_bytes(b"%PDF-1.4\nrebuilt fixture\n")
            project.record_build()
            result = run_script("research_quality_gate.py", project.root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Unverified manuscript numbers: 91.2", result.stdout)


class NumericEvidenceTests(unittest.TestCase):
    def _write_project(self, root: Path, entries: list[dict[str, object]]) -> None:
        (root / "paper").mkdir()
        (root / "paper/main.tex").write_text(
            """\\documentclass{article}
\\begin{document}
\\section{Results}
Accuracy is 91.2\\% across 10 runs.
\\begin{table}\\begin{tabular}{lc}Metric & Value \\\\ Accuracy & 91.2 \\\\ \\end{tabular}\\end{table}
\\end{document}
""",
            encoding="utf-8",
        )
        (root / "results.json").write_text('{"accuracy": 0.912, "runs": 10}\n', encoding="utf-8")
        (root / "numeric_evidence.json").write_text(
            json.dumps(
                {
                    "schema_version": "ai-research-writing/numeric-evidence-v2",
                    "entries": entries,
                }
            ),
            encoding="utf-8",
        )

    def test_percent_and_raw_representations_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_project(
                root,
                [
                    {"value": 0.912, "source": "results.json", "selector": {"kind": "json-pointer", "pointer": "/accuracy"}, "representations": ["percent"]},
                    {"value": 10, "source": "results.json", "selector": {"kind": "json-pointer", "pointer": "/runs"}},
                ],
            )
            result = run_script(
                "check_numeric_evidence.py",
                root,
                "--main",
                "paper/main.tex",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unregistered_result_number_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_project(root, [{"value": 10, "source": "results.json", "selector": {"kind": "json-pointer", "pointer": "/runs"}}])
            result = run_script(
                "check_numeric_evidence.py",
                root,
                "--main",
                "paper/main.tex",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("91.2", result.stdout)

    def test_missing_provenance_file_fails_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_project(root, [{"value": 91.2, "source": "missing.json", "selector": {"kind": "json-pointer", "pointer": "/score"}}])
            result = run_script(
                "check_numeric_evidence.py",
                root,
                "--main",
                "paper/main.tex",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("source does not exist", result.stderr)

    def test_json_pointer_value_must_match_registry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_project(
                root,
                [{"value": 0.8, "source": "results.json", "selector": {"kind": "json-pointer", "pointer": "/accuracy"}, "representations": ["percent"]}],
            )
            result = run_script(
                "check_numeric_evidence.py",
                root,
                "--main",
                "paper/main.tex",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("does not match computed source value", result.stderr)

    def test_csv_mean_is_recomputed_from_selected_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "paper").mkdir()
            (root / "paper/main.tex").write_text(
                "\\section{Results}Mean accuracy is 91.0 percent.\n", encoding="utf-8"
            )
            (root / "results.csv").write_text(
                "method,seed,accuracy\nours,1,0.90\nours,2,0.92\nbaseline,1,0.80\n",
                encoding="utf-8",
            )
            (root / "numeric_evidence.json").write_text(
                json.dumps({
                    "schema_version": "ai-research-writing/numeric-evidence-v2",
                    "entries": [{
                        "value": 0.91,
                        "source": "results.csv",
                        "selector": {"kind": "csv", "column": "accuracy", "where": {"method": "ours"}},
                        "aggregate": "mean",
                        "representations": ["percent"],
                    }],
                }),
                encoding="utf-8",
            )
            result = run_script("check_numeric_evidence.py", root, "--main", "paper/main.tex")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_v1_registry_requires_explicit_migration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_project(root, [{"value": 10, "source": "results.json#/runs"}])
            registry = json.loads((root / "numeric_evidence.json").read_text(encoding="utf-8"))
            registry["schema_version"] = "ai-research-writing/numeric-evidence-v1"
            (root / "numeric_evidence.json").write_text(json.dumps(registry), encoding="utf-8")
            result = run_script("check_numeric_evidence.py", root, "--main", "paper/main.tex")
            self.assertEqual(result.returncode, 2)
            self.assertIn("numeric-evidence-v2", result.stderr)


class CitationLockTests(unittest.TestCase):
    def test_stale_request_digest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            requests_path = project.root / "citation_requests.json"
            requests = json.loads(requests_path.read_text(encoding="utf-8"))
            requests["entries"][0]["claim_support"][0]["claim"] = "Changed claim."
            requests_path.write_text(json.dumps(requests), encoding="utf-8")
            result = run_script("check_citation_lock.py", project.root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("is stale", result.stderr)

    def test_nonterminal_claim_support_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = PaperProject(Path(directory))
            requests_path = project.root / "citation_requests.json"
            requests = json.loads(requests_path.read_text(encoding="utf-8"))
            requests["entries"][0]["claim_support"][0]["status"] = "metadata-only"
            requests_path.write_text(json.dumps(requests), encoding="utf-8")
            lock_path = project.root / "citation_lock.json"
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            lock["request_sha256"] = canonical_digest(requests["entries"])
            lock["records"][0]["claim_support_sha256"] = canonical_digest(requests["entries"][0]["claim_support"])
            lock_path.write_text(json.dumps(lock), encoding="utf-8")
            result = run_script("check_citation_lock.py", project.root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("claim support is not terminal", result.stdout)

    def test_crossref_response_is_normalized(self) -> None:
        sys.path.insert(0, str(SCRIPTS))
        try:
            import verify_citations
            payload = json.dumps({
                "message": {
                    "title": ["A Reliable Paper"],
                    "author": [{"given": "Ada", "family": "Lovelace"}],
                    "issued": {"date-parts": [[2025, 1, 2]]},
                    "DOI": "10.1000/TEST",
                    "type": "proceedings-article",
                }
            }).encode("utf-8")
            with mock.patch.object(verify_citations, "fetch", return_value=payload):
                metadata, _ = verify_citations.crossref("10.1000/test", None, 1.0)
        finally:
            sys.path.pop(0)
        self.assertEqual(metadata["title"], "A Reliable Paper")
        self.assertEqual(metadata["authors"], ["Ada Lovelace"])
        self.assertEqual(metadata["year"], 2025)
        self.assertEqual(metadata["doi"], "10.1000/test")

    def test_network_error_is_written_as_nonterminal_lock(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            entries = [{
                "key": "demo",
                "identifier": "doi:10.1000/demo",
                "claim_support": [{
                    "claim": "A claim", "relation": "direct", "status": "verified",
                    "evidence": "Evidence", "source": "paper text",
                }],
            }]
            (root / "citation_requests.json").write_text(
                json.dumps({"schema_version": "ai-research-writing/citation-requests-v1", "entries": entries}),
                encoding="utf-8",
            )
            sys.path.insert(0, str(SCRIPTS))
            try:
                import verify_citations
                with mock.patch.object(
                    verify_citations,
                    "crossref",
                    side_effect=verify_citations.ProviderFailure("network-error", "offline"),
                ), mock.patch.object(sys, "argv", ["verify_citations.py", str(root)]):
                    result = verify_citations.main()
            finally:
                sys.path.pop(0)
            self.assertEqual(result, 1)
            lock = json.loads((root / "citation_lock.json").read_text(encoding="utf-8"))
            self.assertEqual(lock["records"][0]["status"], "network-error")
            self.assertEqual(lock["records"][0]["error"], "offline")


class ResearchHandoffTests(unittest.TestCase):
    def _write_handoff(self, root: Path, *, quantitative: bool, artifacts: dict[str, str]) -> None:
        for relative in set(artifacts.values()) - {"numeric_evidence.json"}:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Evidence artifact.\n", encoding="utf-8")
        (root / "research_handoff.json").write_text(
            json.dumps(
                {
                    "schema_version": "ai-research-writing/research-handoff-v1",
                    "research_question": "Does X improve Y?",
                    "paper_type": "empirical ML paper",
                    "target_venue": "ICML",
                    "quantitative": quantitative,
                    "artifacts": artifacts,
                    "blockers": [],
                }
            ),
            encoding="utf-8",
        )

    def _write_shared_state_project(
        self,
        root: Path,
        *,
        lifecycle_validity: str = "active",
        experiment_stage: str = "paper-ready",
        verification_passed: bool = True,
        admission_mode: str = "formal",
    ) -> Path:
        ideas = root / "research_state" / "ideas"
        experiment = root / "research_state" / "experiments" / "exp-1"
        analysis = experiment / "analysis"
        contract_path = ideas / "idea-1" / "idea_contract.yaml"
        contract_path.parent.mkdir(parents=True)
        analysis.mkdir(parents=True)
        pool_status = "experiment-ready" if lifecycle_validity == "active" else "rejected"
        pool_path = ideas / "idea_pool.json"
        pool_path.write_text(
            json.dumps(
                {
                    "schema_version": "research-idea-pool/v1",
                    "updated_at": "fixture",
                    "ideas": [{"id": "idea-1", "status": pool_status}],
                }
            ),
            encoding="utf-8",
        )
        contract = {
            "schema_version": "research-idea/v4",
            "idea_id": "idea-1",
            "revision": 1,
            "status": "experiment-ready",
            "lifecycle": {
                "validity": lifecycle_validity,
                "current_pool_status": pool_status,
                "invalidation_reason": "fixture invalidation" if lifecycle_validity != "active" else None,
                "superseded_by_revision": None,
            },
        }
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
        consistency_path = ideas / "state_consistency.json"
        consistency_path.write_text(
            json.dumps(
                {
                    "schema_version": "research-idea/state-consistency-v2",
                    "passed": True,
                    "pool_sha256": hashlib.sha256(pool_path.read_bytes()).hexdigest(),
                    "records": [
                        {
                            "idea_id": "idea-1",
                            "pool_status": pool_status,
                            "contract_revision": 1,
                            "contract_sha256": contract_hash,
                            "lifecycle_validity": lifecycle_validity,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        plan_path = experiment / "experiment_plan.json"
        plan_path.write_text(
            json.dumps(
                {
                    "schema_version": "research-experiment/plan-v2",
                    "admission_mode": admission_mode,
                    "experiment_id": "exp-1",
                    "plan_revision": 1,
                    "idea_id": "idea-1",
                    "idea_revision": 1,
                    "idea_contract_sha256": contract_hash,
                    "method_identity": {
                        "method_tier": "full",
                        "publication_eligible": True,
                        "scientific_configuration": "complete fixture method",
                        "excluded_simplifications": [],
                    },
                }
            ),
            encoding="utf-8",
        )
        plan_hash = hashlib.sha256(plan_path.read_bytes()).hexdigest()
        (experiment / "experiment_state.json").write_text(
            json.dumps(
                {
                    "schema_version": "research-experiment/state-v1",
                    "experiment_id": "exp-1",
                    "plan_revision": 1,
                    "idea_id": "idea-1",
                    "idea_revision": 1,
                    "stage": experiment_stage,
                }
            ),
            encoding="utf-8",
        )
        (experiment / "verification_report.json").write_text(
            json.dumps(
                {
                    "schema_version": "research-experiment/experiment-verification-v2",
                    "admission_mode": admission_mode,
                    "experiment_id": "exp-1",
                    "plan_revision": 1,
                    "idea_id": "idea-1",
                    "idea_revision": 1,
                    "idea_contract_sha256": contract_hash,
                    "experiment_plan_sha256": plan_hash,
                    "method_identity": {
                        "method_tier": "full",
                        "publication_eligible": True,
                        "scientific_configuration": "complete fixture method",
                        "excluded_simplifications": [],
                    },
                    "stage": experiment_stage,
                    "passed": verification_passed,
                    "blockers": [] if verification_passed else ["fixture-failure"],
                    "checks": [],
                }
            ),
            encoding="utf-8",
        )
        (analysis / "run_index.csv").write_text("run_id,status\nrun-1,verified\n", encoding="utf-8")
        (analysis / "metric_summary.csv").write_text("metric,mean\nscore,0.9\n", encoding="utf-8")
        (root / "research_state.json").write_text(
            json.dumps(
                {
                    "schema_version": "research-state/v1",
                    "revision": 1,
                    "phase": "writing",
                    "active_idea_id": "idea-1",
                    "active_experiment_id": "exp-1",
                    "paths": {
                        "idea_pool": "research_state/ideas/idea_pool.json",
                        "idea_state_consistency": "research_state/ideas/state_consistency.json",
                        "experiments": "research_state/experiments",
                    },
                    "updated_at": "fixture",
                }
            ),
            encoding="utf-8",
        )
        evidence = root / "evidence"
        evidence.mkdir()
        for name in ("project.md", "analysis.md", "decision.md", "experiments.md"):
            (evidence / name).write_text("Verified evidence.\n", encoding="utf-8")
        (root / "results.json").write_text('{"score": 0.9}\n', encoding="utf-8")
        (root / "numeric_evidence.json").write_text(
            json.dumps(
                {
                    "schema_version": "ai-research-writing/numeric-evidence-v2",
                    "entries": [
                        {
                            "value": 0.9,
                            "source": "results.json",
                            "selector": {"kind": "json-pointer", "pointer": "/score"},
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        handoff_path = root / "research_handoff.json"
        handoff_path.write_text(
            json.dumps(
                {
                    "schema_version": "ai-research-writing/research-handoff-v2",
                    "source_idea_id": "idea-1",
                    "source_idea_revision": 1,
                    "source_idea_contract_sha256": contract_hash,
                    "experiment_id": "exp-1",
                    "experiment_plan_revision": 1,
                    "experiment_plan_sha256": plan_hash,
                    "research_question": "Does X improve Y?",
                    "paper_type": "empirical ML paper",
                    "target_venue": "ICML",
                    "quantitative": True,
                    "artifacts": {
                        "project_inventory": "evidence/project.md",
                        "analysis": "evidence/analysis.md",
                        "decision": "evidence/decision.md",
                        "experiment_inventory": "evidence/experiments.md",
                        "numeric_evidence": "numeric_evidence.json",
                        "experiment_verification": "research_state/experiments/exp-1/verification_report.json",
                        "run_index": "research_state/experiments/exp-1/analysis/run_index.csv",
                        "metric_summary": "research_state/experiments/exp-1/analysis/metric_summary.csv",
                    },
                    "blockers": [],
                }
            ),
            encoding="utf-8",
        )
        return handoff_path

    def test_quantitative_handoff_with_registry_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "results.json").write_text('{"score": 0.9}\n', encoding="utf-8")
            (root / "numeric_evidence.json").write_text(
                json.dumps(
                    {
                        "schema_version": "ai-research-writing/numeric-evidence-v2",
                        "entries": [{"value": 0.9, "source": "results.json", "selector": {"kind": "json-pointer", "pointer": "/score"}}],
                    }
                ),
                encoding="utf-8",
            )
            self._write_handoff(
                root,
                quantitative=True,
                artifacts={
                    "project_inventory": "evidence/project.md",
                    "analysis": "evidence/analysis.md",
                    "decision": "evidence/decision.md",
                    "experiment_inventory": "evidence/experiments.md",
                    "numeric_evidence": "numeric_evidence.json",
                },
            )
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_quantitative_handoff_requires_numeric_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_handoff(
                root,
                quantitative=True,
                artifacts={
                    "project_inventory": "evidence/project.md",
                    "analysis": "evidence/analysis.md",
                    "decision": "evidence/decision.md",
                    "experiment_inventory": "evidence/experiments.md",
                },
            )
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing required artifacts: numeric_evidence", result.stderr)

    def test_require_unblocked_fails_on_declared_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_handoff(
                root,
                quantitative=False,
                artifacts={
                    "project_inventory": "evidence/project.md",
                    "analysis": "evidence/analysis.md",
                    "decision": "evidence/decision.md",
                },
            )
            handoff_path = root / "research_handoff.json"
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
            handoff["blockers"] = ["Experiments require another iteration"]
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
            result = run_script("check_research_handoff.py", root, "--require-unblocked")
            self.assertEqual(result.returncode, 1)
            self.assertIn("another iteration", result.stdout)

    def test_shared_state_handoff_reconciles_active_lifecycle_and_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_shared_state_project(root)
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shared_state_handoff_accepts_revision_identity_without_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            handoff_path = self._write_shared_state_project(root)
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
            handoff.pop("source_idea_contract_sha256")
            handoff.pop("experiment_plan_sha256")
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
            result = run_script("check_research_handoff.py", root, "--require-unblocked")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shared_state_handoff_rejects_legacy_presence_only_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            handoff_path = self._write_shared_state_project(root)
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
            handoff["schema_version"] = "ai-research-writing/research-handoff-v1"
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("shared-state handoff schema_version", result.stderr)

    def test_shared_state_handoff_rejects_non_active_idea(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_shared_state_project(root, lifecycle_validity="invalidated")
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("not experiment-ready", result.stderr)

    def test_shared_state_handoff_rejects_stale_active_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_shared_state_project(root)
            state_path = root / "research_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["active_idea_id"] = "idea-2"
            state_path.write_text(json.dumps(state), encoding="utf-8")
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("active idea mismatch", result.stderr)

    def test_shared_state_handoff_rejects_non_paper_ready_experiment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_shared_state_project(root, experiment_stage="verified-scientific")
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("experiment state stage mismatch", result.stderr)

    def test_shared_state_handoff_rejects_exploratory_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_shared_state_project(
                root, admission_mode="exploratory-validation"
            )
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("experiment plan admission mode mismatch", result.stderr)

    def test_shared_state_handoff_rejects_plan_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            handoff_path = self._write_shared_state_project(root)
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
            handoff["experiment_plan_sha256"] = "0" * 64
            handoff_path.write_text(json.dumps(handoff), encoding="utf-8")
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("experiment plan SHA-256 mismatch", result.stderr)

    def test_shared_state_handoff_rejects_failed_verification(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._write_shared_state_project(root, verification_passed=False)
            result = run_script("check_research_handoff.py", root)
            self.assertEqual(result.returncode, 2)
            self.assertIn("passed: true", result.stderr)


class CameraReadyTests(unittest.TestCase):
    def test_word_checklist_does_not_count_as_checklist_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            main = Path(directory) / "main.tex"
            main.write_text(
                """\\documentclass{article}
\\author{A. Author}
\\begin{document}
This sentence mentions checklist but is not one.
\\section{Limitations}Limits.
\\section{Acknowledgments}Thanks.
\\bibliography{refs}
\\end{document}
""",
                encoding="utf-8",
            )
            result = run_script("camera_ready_check.py", main)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Venue checklist artifact present | fail", result.stdout)


class TemplateAuditTests(unittest.TestCase):
    def test_contract_schemas_are_valid_json_objects(self) -> None:
        for name in (
            "paper-state.schema.json",
            "numeric-evidence.schema.json",
            "research-handoff.schema.json",
            "citation-requests.schema.json",
            "citation-lock.schema.json",
        ):
            schema = json.loads((REPO / "references" / name).read_text(encoding="utf-8"))
            self.assertEqual(schema["type"], "object")
            self.assertFalse(schema["additionalProperties"])

    def test_manifest_tracks_nine_venues_without_vendored_directories(self) -> None:
        manifest = json.loads((REPO / "templates/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["templates"]), 9)
        self.assertEqual([path for path in (REPO / "templates").iterdir() if path.is_dir()], [])

    def test_template_extractor_rejects_path_traversal(self) -> None:
        sys.path.insert(0, str(SCRIPTS))
        try:
            from fetch_template import safe_members
        finally:
            sys.path.pop(0)
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("../escape.txt", "bad")
        payload.seek(0)
        with zipfile.ZipFile(payload) as archive:
            with self.assertRaisesRegex(RuntimeError, "Unsafe archive path"):
                safe_members(archive)


if __name__ == "__main__":
    unittest.main()
