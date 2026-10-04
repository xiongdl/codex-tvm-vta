from pathlib import Path

from common.artifacts import MODEL_IDS, cleanup_artifacts
from scripts.clean_mlperf_tiny import main


def _write(path: Path, data: bytes = b"data") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def test_cleanup_dry_run_reports_bytes_without_mutating(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    cache = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "model.dylib", b"compiled")
    state = _write(
        benchmark / MODEL_IDS[0] / "build" / "actual_compute_tuning" / "20261002T123456Z" / "occurrence-000.ledger.json",
        b"state",
    )

    result = cleanup_artifacts(
        benchmark,
        model=MODEL_IDS[0],
        categories={"cache", "tuning-runs"},
        tracked_paths=set(),
        dry_run=True,
    )

    assert result.removed == ()
    assert {item.path: item.size_bytes for item in result.planned} == {
        cache.resolve(): 8,
        state.resolve(): 5,
    }
    assert result.total_bytes == 13
    assert cache.exists() and state.exists()


def test_cleanup_removes_only_selected_category_and_model(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    cache_one = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "model.dylib")
    cache_two = _write(benchmark / MODEL_IDS[1] / "build" / "reference" / "model.dylib")
    run_one = _write(
        benchmark / MODEL_IDS[0] / "build" / "actual_compute_tuning" / "20261002T123456Z" / "best.json"
    )
    unknown = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "notes.md")

    result = cleanup_artifacts(
        benchmark,
        model=MODEL_IDS[0],
        categories={"cache"},
        tracked_paths=set(),
        dry_run=False,
    )

    assert {item.path for item in result.removed} == {cache_one.resolve()}
    assert not cache_one.exists()
    assert cache_two.exists() and run_one.exists() and unknown.exists()


def test_cleanup_all_covers_shared_and_each_model_build_directory(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    candidates = []
    for model in MODEL_IDS:
        candidates.append(_write(benchmark / model / "build" / "reference" / "model.dylib"))
        candidates.append(
            _write(
                benchmark / model / "build" / "actual_compute_tuning" / "20261002T123456Z" / "best.json"
            )
        )
        candidates.append(
            _write(benchmark / "build" / "autotvm" / f"{model}-fsim-20261002T123456Z.log")
        )
    candidates.append(
        _write(
            benchmark / "build" / "autotvm-comparison" / "checkpoint" / "tuned" / "mixed" / "model.dylib"
        )
    )
    saved = _write(benchmark / MODEL_IDS[0] / "tune" / "optimal" / "best.json")

    result = cleanup_artifacts(
        benchmark,
        model="all",
        categories={"cache", "tuning-runs"},
        tracked_paths=set(),
        dry_run=False,
    )

    assert {item.path for item in result.removed} == {path.resolve() for path in candidates}
    assert all(not path.exists() for path in candidates)
    assert saved.exists()


def test_cleanup_recognizes_resnet_make_intermediates_and_retains_saved_tuning(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    app_root = benchmark / MODEL_IDS[0]
    workloads = _write(app_root / "build" / "tune" / "workloads.json")
    default_bundle = _write(app_root / "build" / "vta_llvm" / "graph.json")
    bundle = _write(app_root / "build" / "tune" / "deploy" / "vta_llvm" / "model.dylib")
    source = _write(app_root / "build" / "tune" / "deploy" / "vta_llvm" / "source" / "00-llvm.ll")
    unknown = _write(app_root / "build" / "tune" / "deploy" / "vta_llvm" / "notes.md")
    archived_reference = _write(app_root / "build" / "archive" / "reference" / "graph.json")
    other_model_cache = _write(benchmark / MODEL_IDS[1] / "build" / "reference" / "graph.json")
    saved = _write(app_root / "tune" / "vta_64mac" / "fsim.tmp")

    result = cleanup_artifacts(
        benchmark,
        model=MODEL_IDS[0],
        categories={"cache", "tuning-runs"},
        tracked_paths=set(),
        dry_run=False,
    )

    assert {item.path for item in result.removed} == {
        workloads.resolve(), default_bundle.resolve(), bundle.resolve(), source.resolve()
    }
    assert not workloads.exists() and not default_bundle.exists()
    assert not bundle.exists() and not source.exists()
    assert unknown.exists() and archived_reference.exists() and saved.exists()
    assert other_model_cache.exists()


def test_cleanup_preserves_tracked_files(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    tracked = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "graph.json")
    candidate = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "model.dylib")

    result = cleanup_artifacts(
        benchmark,
        model=MODEL_IDS[0],
        categories={"cache"},
        tracked_paths={tracked.resolve()},
        dry_run=False,
    )

    assert {item.path for item in result.removed} == {candidate.resolve()}
    assert tracked.exists()


def test_cleanup_missing_build_directories_is_a_noop(tmp_path):
    result = cleanup_artifacts(
        tmp_path / "missing",
        model="all",
        categories={"cache", "tuning-runs"},
        tracked_paths=set(),
        dry_run=False,
    )
    assert result.planned == ()
    assert result.removed == ()
    assert result.errors == ()


def test_cleanup_refuses_symlinked_roots_and_preserves_external_files(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    external = _write(tmp_path / "external" / "reference" / "model.dylib")
    build = benchmark / MODEL_IDS[0] / "build"
    build.parent.mkdir(parents=True)
    build.symlink_to(external.parents[1], target_is_directory=True)

    result = cleanup_artifacts(
        benchmark,
        model=MODEL_IDS[0],
        categories={"cache"},
        tracked_paths=set(),
        dry_run=False,
    )

    assert result.removed == ()
    assert result.errors
    assert external.exists()


def test_cleanup_symlink_escape_blocks_the_whole_operation(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    candidate = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "model.dylib")
    external = _write(tmp_path / "external.txt")
    link = benchmark / MODEL_IDS[0] / "build" / "reference" / "external.txt"
    link.symlink_to(external)

    result = cleanup_artifacts(
        benchmark,
        model=MODEL_IDS[0],
        categories={"cache"},
        tracked_paths=set(),
        dry_run=False,
    )

    assert result.removed == ()
    assert result.errors
    assert candidate.exists() and external.exists()


def test_cleanup_retains_unknown_files_and_validates_categories(tmp_path):
    benchmark = tmp_path / "mlperf_tiny_benchmark"
    unknown = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "model.custom")
    result = cleanup_artifacts(
        benchmark,
        model=MODEL_IDS[0],
        categories={"cache"},
        tracked_paths=set(),
        dry_run=False,
    )
    assert result.removed == ()
    assert unknown.exists()

    try:
        cleanup_artifacts(benchmark, model="all", categories=set(), tracked_paths=set())
    except ValueError as error:
        assert "category" in str(error)
    else:
        raise AssertionError("at least one explicit cleanup category is required")


def test_cli_dry_run_shows_resolved_paths_and_category_byte_totals(tmp_path, capsys):
    benchmark = tmp_path / "vta" / "apps" / "mlperf_tiny_benchmark"
    cache = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "model.dylib", b"cache-data")
    unknown = _write(benchmark / MODEL_IDS[0] / "build" / "reference" / "notes.md")

    status = main(
        ["--model", MODEL_IDS[0], "--cache", "--dry-run"],
        repo_root=tmp_path,
        tracked_paths=set(),
    )

    output = capsys.readouterr().out
    assert status == 0
    assert f"cache: 1 file(s), 10 bytes" in output
    assert str(cache.resolve()) in output
    assert f"unknown, retained: {unknown.resolve()}" in output
    assert "would remove: 1 file(s), 10 bytes" in output
    assert cache.exists()


def test_cli_requires_an_explicit_category(tmp_path):
    try:
        main(["--model", "all"], repo_root=tmp_path, tracked_paths=set())
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError("cleanup CLI must require at least one category")
