from pathlib import Path

import pytest

from scripts.clean_mlperf_tiny import MODEL_IDS, main


def _write(path: Path, data: bytes = b"data") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_model_selection_removes_only_known_build_outputs_and_keeps_assets(tmp_path, capsys):
    benchmark = tmp_path / "vta" / "apps" / "mlperf_tiny_benchmark"
    selected = MODEL_IDS[0]
    generated = _write(benchmark / selected / "build" / "vta_llvm" / "graph.json", b"bundle")
    generated_source = _write(
        benchmark / selected / "build" / "tune" / "deploy" / "vta_llvm" / "source" / "main.ll"
    )
    matrix_output = _write(
        benchmark / selected / "build" / "llvm-tsim" / "reference" / "graph.json"
    )
    other = _write(benchmark / MODEL_IDS[1] / "build" / "vta_llvm" / "graph.json")
    unknown = _write(benchmark / selected / "build" / "vta_llvm" / "notes.md")
    nested_unknown = _write(benchmark / selected / "build" / "archive" / "reference" / "graph.json")
    tune = _write(benchmark / selected / "tune" / "vta_64mac" / "best.log")
    asset = _write(benchmark / selected / "samples" / "sample.wav")

    status = main(["--model", selected], repo_root=tmp_path, tracked_paths=set())

    output = capsys.readouterr().out
    assert status == 0
    assert "removed: " in output
    assert not generated.exists() and not generated_source.exists() and not matrix_output.exists()
    assert other.exists() and unknown.exists() and nested_unknown.exists() and tune.exists() and asset.exists()
    assert f"unknown, retained: {unknown.resolve()}" in output


def test_all_selects_only_the_five_migrated_build_roots(tmp_path, capsys):
    benchmark = tmp_path / "vta" / "apps" / "mlperf_tiny_benchmark"
    outputs = [_write(benchmark / model / "build" / "llvm" / "graph.json") for model in MODEL_IDS]
    read_only = _write(benchmark / "image_classification_v1" / "build" / "llvm" / "graph.json")

    assert main(["--model", "all"], repo_root=tmp_path, tracked_paths=set()) == 0
    capsys.readouterr()
    assert all(not output.exists() for output in outputs)
    assert read_only.exists()


def test_dry_run_reports_candidates_without_mutating(tmp_path, capsys):
    benchmark = tmp_path / "vta" / "apps" / "mlperf_tiny_benchmark"
    generated = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "model.dylib", b"compiled")

    assert main(["--model", MODEL_IDS[0], "--dry-run"], repo_root=tmp_path, tracked_paths=set()) == 0

    output = capsys.readouterr().out
    assert "would remove: 1 file(s), 8 bytes" in output
    assert str(generated.resolve()) in output
    assert generated.exists()


def test_tracked_generated_file_is_preserved(tmp_path, capsys):
    benchmark = tmp_path / "vta" / "apps" / "mlperf_tiny_benchmark"
    tracked = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "graph.json")

    assert main(
        ["--model", MODEL_IDS[0]], repo_root=tmp_path, tracked_paths={tracked.resolve()}
    ) == 0

    assert tracked.exists()
    assert f"tracked, retained: {tracked.resolve()}" in capsys.readouterr().out


def test_symlink_in_build_tree_blocks_deletion_and_preserves_external_target(tmp_path, capsys):
    benchmark = tmp_path / "vta" / "apps" / "mlperf_tiny_benchmark"
    generated = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "graph.json")
    outside = _write(tmp_path / "outside" / "model.dylib")
    (generated.parent / "external.dylib").symlink_to(outside)

    assert main(["--model", MODEL_IDS[0]], repo_root=tmp_path, tracked_paths=set()) == 2

    assert generated.exists() and outside.exists()
    assert "symlink refused" in capsys.readouterr().err


@pytest.mark.parametrize("args", [["--model", "image_classification_v1"], ["--model", "all", "--tuning-runs"]])
def test_cli_rejects_read_only_model_and_retired_options(args, tmp_path):
    with pytest.raises(SystemExit) as error:
        main(args, repo_root=tmp_path, tracked_paths=set())
    assert error.value.code == 2


def test_migration_removes_shared_runtime_and_old_root_consumers():
    app_root = Path(__file__).resolve().parents[2] / "vta" / "apps"
    benchmark = app_root / "mlperf_tiny_benchmark"
    assert not any(path.is_file() for path in (app_root / "common").rglob("*.py"))
    for obsolete in (
        benchmark / "model_registry.py",
        benchmark / "tuning_controller.py",
        benchmark / "deployment_evidence.py",
    ):
        assert not obsolete.exists()
    assert not any(path.is_file() for path in (benchmark / "tests").rglob("*.py"))


def test_runner_has_no_retired_shared_callers_or_reference_app_acceptance():
    repo_root = Path(__file__).resolve().parents[2]
    runner = (repo_root / "scripts" / "test_vta_byoc.sh").read_text()
    assert "apps/common" not in runner
    assert "image_classification_v1" not in runner


def test_migrated_apps_have_no_shared_or_neighbor_imports():
    app_root = Path(__file__).resolve().parents[2] / "vta" / "apps" / "mlperf_tiny_benchmark"
    forbidden = ("from common", "import common", "apps.common", "model_registry", "tuning_controller")
    for model in MODEL_IDS:
        if model == "image_classification_v1":
            continue
        for path in (app_root / model).rglob("*.py"):
            if "tests" in path.parts:
                continue
            source = path.read_text()
            assert not any(token in source for token in forbidden), path


def test_reference_application_matches_the_approved_vta_base():
    import subprocess

    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root / "vta"),
            "diff",
            "26e9c86035b3ef8d6ff68bbbeb8ee7819a297401",
            "--",
            "apps/mlperf_tiny_benchmark/image_classification_v1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout == ""
