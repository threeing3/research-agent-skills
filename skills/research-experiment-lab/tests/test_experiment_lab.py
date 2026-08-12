from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
WRITING_SKILL = SKILL.parent / "ai-research-writing-skill"


def run(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *(str(value) for value in args)],
        text=True,
        capture_output=True,
        check=False,
    )


class ExperimentLabTests(unittest.TestCase):
    def make_project(self, root: Path) -> None:
        (root / "research_state/logs").mkdir(parents=True)
        ideas = root / "research_state" / "ideas"
        contract_path = ideas / "idea-1" / "idea_contract.yaml"
        contract_path.parent.mkdir(parents=True)
        pool_path = ideas / "idea_pool.json"
        pool_path.write_text(
            json.dumps(
                {
                    "schema_version": "research-idea-pool/v1",
                    "updated_at": "fixture",
                    "ideas": [{"id": "idea-1", "status": "experiment-ready"}],
                }
            ),
            encoding="utf-8",
        )
        contract_path.write_text(
            json.dumps(
                {
                    "schema_version": "research-idea/v4",
                    "idea_id": "idea-1",
                    "revision": 1,
                    "status": "experiment-ready",
                    "lifecycle": {
                        "validity": "active",
                        "current_pool_status": "experiment-ready",
                        "invalidation_reason": None,
                        "superseded_by_revision": None,
                    },
                }
            ),
            encoding="utf-8",
        )
        contract_hash = hashlib.sha256(contract_path.read_bytes()).hexdigest()
        (ideas / "state_consistency.json").write_text(
            json.dumps(
                {
                    "schema_version": "research-idea/state-consistency-v2",
                    "passed": True,
                    "pool_sha256": hashlib.sha256(pool_path.read_bytes()).hexdigest(),
                    "records": [
                        {
                            "idea_id": "idea-1",
                            "pool_status": "experiment-ready",
                            "contract_revision": 1,
                            "contract_sha256": contract_hash,
                            "lifecycle_validity": "active",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (root / "research_state.json").write_text(
            json.dumps(
                {
                    "schema_version": "research-state/v1",
                    "revision": 0,
                    "phase": "ideation",
                    "active_idea_id": "idea-1",
                    "paths": {
                        "events": "research_state/logs/research_events.jsonl",
                        "idea_pool": "research_state/ideas/idea_pool.json",
                        "idea_state_consistency": "research_state/ideas/state_consistency.json",
                        "experiments": "research_state/experiments",
                    },
                    "updated_at": "fixture",
                }
            ),
            encoding="utf-8",
        )

    def create_experiment_and_run(
        self,
        root: Path,
        run_id: str,
        value: float,
        exit_code: int = 0,
        *,
        experiment_id: str = "exp-1",
        mode: str = "full",
        admission_mode: str | None = None,
    ) -> Path:
        experiment = root / "research_state" / "experiments" / experiment_id
        if not experiment.exists():
            init_args: list[object] = [
                "init", root,
                "--experiment-id", experiment_id,
                "--mode", mode,
                "--idea-id", "idea-1",
                "--idea-revision", 1,
                "--scientific-configuration", "complete fixture method",
                "--research-question", "Does X improve Y?",
            ]
            if admission_mode is not None:
                init_args.extend(["--admission-mode", admission_mode])
            if admission_mode == "exploratory-validation":
                init_args.extend(
                    [
                        "--implementation-revision", 1,
                        "--validation-alignment", "research_state/ideas/idea-1/validation/align-1.yaml",
                        "--validation-alignment-id", "align-1",
                        "--method-tier", "simplified",
                    ]
                )
            result = run("experimentctl.py", *init_args)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        command = {
            "argv": [
                sys.executable,
                "-c",
                (
                    "import json,sys;"
                    f"print('METRIC_JSON:'+json.dumps({{'name':'accuracy','value':{value},"
                    f"'split':'val'}}));sys.exit({exit_code})"
                ),
            ],
            "cwd": ".",
            "env": {},
            "metrics_required": True,
            "resource_interval_seconds": 1,
        }
        command_path = root / f"{run_id}.command.json"
        command_path.write_text(json.dumps(command), encoding="utf-8")
        result = run(
            "experimentctl.py", "new-run", root,
            "--experiment-id", experiment_id,
            "--run-id", run_id,
            "--command-json", command_path,
            "--variant", "ours",
            "--dataset", "fixture",
            "--split", "val",
            "--seed", int(run_id.rsplit("-", 1)[-1]),
            "--snapshot-id", "snapshot-1",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        run_dir = experiment / "runs" / run_id
        result = run(
            "remote_run.py",
            "--run-dir", run_dir,
            "--workspace", root,
            "--command-json", run_dir / "records/command.json",
        )
        self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
        return run_dir

    def test_exploratory_validation_verifies_diagnostic_but_not_paper_ready(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            run_dir = self.create_experiment_and_run(
                root,
                "probe-1",
                0.7,
                experiment_id="exp-probe",
                mode="pilot",
                admission_mode="exploratory-validation",
            )
            result = run("verify_run.py", run_dir, "--require-metrics")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            experiment = root / "research_state/experiments/exp-probe"
            plan_path = experiment / "experiment_plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan.update(
                {
                    "datasets": ["fixture"],
                    "variants": ["ours"],
                    "metrics": ["accuracy"],
                    "seeds": [1],
                    "required_runs": [
                        {
                            "variant": "ours",
                            "dataset": "fixture",
                            "split": "val",
                            "seed": 1,
                        }
                    ],
                    "success_thresholds": [],
                }
            )
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = run("aggregate_results.py", experiment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run("verify_experiment.py", experiment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(
                (experiment / "verification_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(report["stage"], "verified-diagnostic")
            result = run("verify_experiment.py", experiment, "--promote-paper-ready")
            self.assertEqual(result.returncode, 1)
            self.assertIn("paper-ready-admission", result.stdout)

    def test_complete_logged_run_verifies_and_aggregates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            first = self.create_experiment_and_run(root, "run-1", 0.8)
            second = self.create_experiment_and_run(root, "run-2", 0.9)
            for run_dir in (first, second):
                result = run("verify_run.py", run_dir, "--require-metrics")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                records = run_dir / "records"
                for name in (
                    "run.log", "events.jsonl", "metrics.jsonl", "resource_usage.jsonl",
                    "environment.json", "status.json", "run_summary.json",
                    "output_manifest.json", "verification_report.json",
                ):
                    self.assertGreater((records / name).stat().st_size, 0, name)
            experiment = root / "research_state/experiments/exp-1"
            plan_path = experiment / "experiment_plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan.update(
                {
                    "idea_contract_sha256": hashlib.sha256(
                        (
                            root
                            / "research_state"
                            / "ideas"
                            / "idea-1"
                            / "idea_contract.yaml"
                        ).read_bytes()
                    ).hexdigest(),
                    "datasets": ["fixture"],
                    "variants": ["ours"],
                    "metrics": ["accuracy"],
                    "seeds": [1, 2],
                    "required_runs": [
                        {"variant": "ours", "dataset": "fixture", "split": "val", "seed": 1},
                        {"variant": "ours", "dataset": "fixture", "split": "val", "seed": 2},
                    ],
                    "success_thresholds": [
                        {
                            "metric": "accuracy",
                            "variant": "ours",
                            "dataset": "fixture",
                            "split": "val",
                            "op": ">=",
                            "value": 0.84,
                        }
                    ],
                }
            )
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = run("aggregate_results.py", experiment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with (experiment / "analysis/metric_summary.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 1)
            self.assertAlmostEqual(float(rows[0]["mean"]), 0.85)
            self.assertEqual(rows[0]["n"], "2")
            with (experiment / "analysis/resource_summary.csv").open(encoding="utf-8-sig", newline="") as handle:
                resources = list(csv.DictReader(handle))
            self.assertEqual(len(resources), 2)
            self.assertGreaterEqual(int(resources[0]["sample_count"]), 1)
            result = run("verify_experiment.py", experiment, "--promote-paper-ready")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            state = json.loads((experiment / "experiment_state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["stage"], "paper-ready")
            verification = json.loads(
                (experiment / "verification_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                verification["schema_version"],
                "research-experiment/experiment-verification-v2",
            )
            self.assertEqual(verification["experiment_id"], "exp-1")
            self.assertEqual(verification["plan_revision"], 1)
            self.assertEqual(verification["idea_id"], "idea-1")
            self.assertEqual(verification["idea_revision"], 1)
            self.assertEqual(verification["stage"], "paper-ready")
            self.assertNotIn("experiment_plan_sha256", verification)

    def test_paper_ready_evidence_enters_writing_and_videoqa_figure_route(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            run_dir = self.create_experiment_and_run(root, "run-1", 0.9)
            result = run("verify_run.py", run_dir, "--require-metrics")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            experiment = root / "research_state/experiments/exp-1"
            plan_path = experiment / "experiment_plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan.update(
                {
                    "idea_contract_sha256": hashlib.sha256(
                        (
                            root
                            / "research_state"
                            / "ideas"
                            / "idea-1"
                            / "idea_contract.yaml"
                        ).read_bytes()
                    ).hexdigest(),
                    "datasets": ["fixture"],
                    "variants": ["ours"],
                    "metrics": ["accuracy"],
                    "seeds": [1],
                    "required_runs": [
                        {
                            "variant": "ours",
                            "dataset": "fixture",
                            "split": "val",
                            "seed": 1,
                        }
                    ],
                    "success_thresholds": [
                        {
                            "metric": "accuracy",
                            "variant": "ours",
                            "dataset": "fixture",
                            "split": "val",
                            "op": ">=",
                            "value": 0.8,
                        }
                    ],
                }
            )
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            result = run("aggregate_results.py", experiment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = run("verify_experiment.py", experiment, "--promote-paper-ready")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            evidence = root / "evidence"
            evidence.mkdir()
            for name in ("project.md", "analysis.md", "decision.md", "experiments.md"):
                (evidence / name).write_text("Verified smoke-test evidence.\n", encoding="utf-8")
            (root / "results.json").write_text('{"accuracy": 0.9}\n', encoding="utf-8")
            (root / "numeric_evidence.json").write_text(
                json.dumps(
                    {
                        "schema_version": "ai-research-writing/numeric-evidence-v2",
                        "entries": [
                            {
                                "value": 0.9,
                                "source": "results.json",
                                "selector": {
                                    "kind": "json-pointer",
                                    "pointer": "/accuracy",
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            handoff = {
                "schema_version": "ai-research-writing/research-handoff-v2",
                "source_idea_id": "idea-1",
                "source_idea_revision": 1,
                "experiment_id": "exp-1",
                "experiment_plan_revision": 1,
                "research_question": "Does X improve Y?",
                "paper_type": "empirical VideoQA paper",
                "target_venue": "CVPR",
                "quantitative": True,
                "artifacts": {
                    "project_inventory": "evidence/project.md",
                    "analysis": "evidence/analysis.md",
                    "decision": "evidence/decision.md",
                    "experiment_inventory": "evidence/experiments.md",
                    "experiment_verification": "research_state/experiments/exp-1/verification_report.json",
                    "run_index": "research_state/experiments/exp-1/analysis/run_index.csv",
                    "metric_summary": "research_state/experiments/exp-1/analysis/metric_summary.csv",
                    "numeric_evidence": "numeric_evidence.json",
                },
                "blockers": [],
            }
            (root / "research_handoff.json").write_text(
                json.dumps(handoff),
                encoding="utf-8",
            )
            writing_check = subprocess.run(
                [
                    sys.executable,
                    str(WRITING_SKILL / "scripts/check_research_handoff.py"),
                    str(root),
                    "--require-unblocked",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(
                writing_check.returncode,
                0,
                writing_check.stdout + writing_check.stderr,
            )
            writing_skill_text = (WRITING_SKILL / "SKILL.md").read_text(encoding="utf-8")
            figure_route_text = (
                WRITING_SKILL / "references/figure-workflow.md"
            ).read_text(encoding="utf-8")
            self.assertIn("videoqa-paper-figures", writing_skill_text)
            self.assertIn("videoqa-paper-figures", figure_route_text)
            self.assertIn("originpro-paper-figures", figure_route_text)

    def test_failed_process_is_preserved_and_not_verified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            run_dir = self.create_experiment_and_run(root, "run-3", 0.2, exit_code=7)
            result = run("verify_run.py", run_dir, "--require-metrics")
            self.assertEqual(result.returncode, 1)
            self.assertIn("RUN VERIFICATION: FAIL", result.stdout)
            self.assertTrue((run_dir / "records/run.log").is_file())

    def test_snapshot_is_explicit_and_excludes_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/train.py").write_text("print('ok')\n", encoding="utf-8")
            (root / ".env").write_text("SECRET=bad\n", encoding="utf-8")
            output = root / "snapshots"
            result = run(
                "prepare_snapshot.py", root,
                "--include", "src",
                "--include", ".env",
                "--output-dir", output,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            metadata = json.loads(result.stdout)
            manifest = json.loads(Path(metadata["manifest"]).read_text(encoding="utf-8"))
            self.assertEqual([item["path"] for item in manifest["files"]], ["src/train.py"])

    def test_autodl_dry_run_is_bounded_to_remote_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiles = root / "profiles.json"
            profiles.write_text(
                json.dumps(
                    {
                        "profiles": {
                            "demo": {
                                "ssh_alias": "autodl-demo",
                                "remote_root": "/root/autodl-tmp/research/demo",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            result = run(
                "autodl_backend.py",
                "--profiles", profiles,
                "--profile", "demo",
                "--dry-run",
                "preflight",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("BatchMode=yes", result.stdout)
            bad = root / "bad.json"
            bad.write_text(
                json.dumps({"profiles": {"demo": {"ssh_alias": "x", "remote_root": "/"}}}),
                encoding="utf-8",
            )
            result = run(
                "autodl_backend.py",
                "--profiles", bad,
                "--profile", "demo",
                "--dry-run",
                "preflight",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("remote_root", result.stderr)

    def test_autodl_interactive_password_profile_never_contains_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            profiles = root / "profiles.json"
            profiles.write_text(
                json.dumps(
                    {
                        "profiles": {
                            "demo": {
                                "host": "example.invalid",
                                "port": 12345,
                                "user": "root",
                                "auth": "interactive-password",
                                "session_backend": "screen",
                                "remote_root": "/root/autodl-tmp/research/demo",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            result = run(
                "autodl_backend.py",
                "--profiles", profiles,
                "--profile", "demo",
                "--dry-run",
                "preflight",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("BatchMode=no", result.stdout)
            self.assertIn("PreferredAuthentications=password", result.stdout)
            self.assertIn("session_backend=screen", result.stdout)
            forbidden = root / "forbidden.json"
            forbidden.write_text(
                json.dumps(
                    {
                        "profiles": {
                            "demo": {
                                "host": "example.invalid",
                                "port": 12345,
                                "user": "root",
                                "password": "must-not-be-accepted",
                                "remote_root": "/root/autodl-tmp/research/demo",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            result = run(
                "autodl_backend.py",
                "--profiles", forbidden,
                "--profile", "demo",
                "--dry-run",
                "preflight",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("must not store credential", result.stderr)
            self.assertNotIn("must-not-be-accepted", result.stdout + result.stderr)

    def test_autodl_snapshot_launch_and_pull_dry_run_do_not_mutate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            (root / "src").mkdir()
            (root / "src/train.py").write_text("print('ok')\n", encoding="utf-8")
            snapshot_result = run(
                "prepare_snapshot.py", root,
                "--include", "src",
                "--output-dir", root / "snapshots",
            )
            self.assertEqual(snapshot_result.returncode, 0, snapshot_result.stdout + snapshot_result.stderr)
            snapshot = json.loads(snapshot_result.stdout)
            command = root / "command.json"
            command.write_text(
                json.dumps(
                    {
                        "argv": ["python", "train.py"],
                        "cwd": ".",
                        "env": {},
                        "metrics_required": False,
                        "resource_interval_seconds": 30,
                    }
                ),
                encoding="utf-8",
            )
            init_result = run(
                "experimentctl.py", "init", root,
                "--experiment-id", "exp-remote",
                "--mode", "pilot",
                "--research-question", "remote fixture",
            )
            self.assertEqual(init_result.returncode, 0, init_result.stdout + init_result.stderr)
            new_result = run(
                "experimentctl.py", "new-run", root,
                "--experiment-id", "exp-remote",
                "--run-id", "remote-1",
                "--command-json", command,
                "--variant", "ours",
                "--dataset", "fixture",
                "--split", "val",
                "--seed", 1,
                "--snapshot-id", snapshot["snapshot_id"],
                "--remote-profile", "demo",
            )
            self.assertEqual(new_result.returncode, 0, new_result.stdout + new_result.stderr)
            profiles = root / "profiles.json"
            profiles.write_text(
                json.dumps(
                    {
                        "profiles": {
                            "demo": {
                                "ssh_alias": "autodl-demo",
                                "remote_root": "/root/autodl-tmp/research/demo",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            push_manifest = root / "push-sync.json"
            push = run(
                "autodl_backend.py",
                "--profiles", profiles, "--profile", "demo", "--dry-run",
                "push-snapshot",
                "--archive", snapshot["archive"],
                "--manifest", snapshot["manifest"],
                "--sync-manifest", push_manifest,
            )
            self.assertEqual(push.returncode, 0, push.stdout + push.stderr)
            self.assertIn('"scp"', push.stdout)
            self.assertFalse(push_manifest.exists())
            local_run = root / "research_state/experiments/exp-remote/runs/remote-1"
            sync_before = (local_run / "records/sync_manifest.json").read_bytes()
            launch = run(
                "autodl_backend.py",
                "--profiles", profiles, "--profile", "demo", "--dry-run",
                "launch",
                "--experiment-id", "exp-remote",
                "--run-id", "remote-1",
                "--snapshot-id", snapshot["snapshot_id"],
                "--local-run-dir", local_run,
            )
            self.assertEqual(launch.returncode, 0, launch.stdout + launch.stderr)
            self.assertIn("tmux new-session", launch.stdout)
            self.assertEqual((local_run / "records/sync_manifest.json").read_bytes(), sync_before)
            destination = root / "download"
            pull = run(
                "autodl_backend.py",
                "--profiles", profiles, "--profile", "demo", "--dry-run",
                "pull-records",
                "--experiment-id", "exp-remote",
                "--run-id", "remote-1",
                "--destination", destination,
            )
            self.assertEqual(pull.returncode, 0, pull.stdout + pull.stderr)
            self.assertFalse(destination.exists())
            output_destination = root / "output-download"
            output_pull = run(
                "autodl_backend.py",
                "--profiles", profiles, "--profile", "demo", "--dry-run",
                "pull-output",
                "--experiment-id", "exp-remote",
                "--run-id", "remote-1",
                "--relative-path", "checkpoints/best.pt",
                "--destination", output_destination,
                "--max-bytes", 1024,
            )
            self.assertEqual(output_pull.returncode, 0, output_pull.stdout + output_pull.stderr)
            self.assertIn("du -sb", output_pull.stdout)
            self.assertFalse(output_destination.exists())

    def test_autodl_screen_launch_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            command = root / "command.json"
            command.write_text(
                json.dumps(
                    {
                        "argv": ["python3", "-c", "print('ok')"],
                        "cwd": ".",
                        "env": {},
                        "metrics_required": False,
                        "resource_interval_seconds": 30,
                    }
                ),
                encoding="utf-8",
            )
            init_result = run(
                "experimentctl.py", "init", root,
                "--experiment-id", "exp-screen",
                "--mode", "pilot",
                "--research-question", "screen fixture",
            )
            self.assertEqual(init_result.returncode, 0, init_result.stdout + init_result.stderr)
            new_result = run(
                "experimentctl.py", "new-run", root,
                "--experiment-id", "exp-screen",
                "--run-id", "screen-1",
                "--command-json", command,
                "--variant", "ours",
                "--dataset", "fixture",
                "--split", "val",
                "--seed", 1,
                "--snapshot-id", "snapshot-screen",
                "--remote-profile", "demo",
            )
            self.assertEqual(new_result.returncode, 0, new_result.stdout + new_result.stderr)
            profiles = root / "profiles.json"
            profiles.write_text(
                json.dumps(
                    {
                        "profiles": {
                            "demo": {
                                "ssh_alias": "autodl-demo",
                                "session_backend": "screen",
                                "remote_root": "/root/autodl-tmp/research/demo",
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            local_run = root / "research_state/experiments/exp-screen/runs/screen-1"
            result = run(
                "autodl_backend.py",
                "--profiles", profiles,
                "--profile", "demo",
                "--dry-run",
                "launch",
                "--experiment-id", "exp-screen",
                "--run-id", "screen-1",
                "--snapshot-id", "snapshot-screen",
                "--local-run-dir", local_run,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("screen -DmS", result.stdout)
            self.assertNotIn("tmux new-session", result.stdout)

    def test_download_ingest_refuses_conflicting_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "download/records"
            destination = root / "local/records"
            source.mkdir(parents=True)
            destination.mkdir(parents=True)
            (destination / "command.json").write_text('{"argv":["python"]}\n', encoding="utf-8")
            (source / "command.json").write_text('{"argv":["python"]}\n', encoding="utf-8")
            (source / "status.json").write_text('{"state":"completed"}\n', encoding="utf-8")
            result = run("ingest_records.py", root / "download", root / "local")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((destination / "status.json").is_file())
            (source / "command.json").write_text('{"argv":["changed"]}\n', encoding="utf-8")
            result = run("ingest_records.py", root / "download", root / "local")
            self.assertEqual(result.returncode, 2)
            self.assertIn("refusing overwrite", result.stderr)


if __name__ == "__main__":
    unittest.main()
