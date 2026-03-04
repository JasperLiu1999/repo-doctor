"""Tests for the rule engine."""

from pathlib import Path

from repo_doctor.context import build_context
from repo_doctor.engine import RuleEngine
from repo_doctor.models import Grade


def test_bad_repo_low_score(bad_repo: Path) -> None:
    ctx = build_context(bad_repo)
    engine = RuleEngine()
    report = engine.scan(ctx)
    assert report.score < 55
    assert report.grade == Grade.D


def test_good_repo_high_score(good_repo: Path) -> None:
    ctx = build_context(good_repo)
    engine = RuleEngine()
    report = engine.scan(ctx)
    assert report.score >= 90
    assert report.grade == Grade.A


def test_avg_repo_middle_score(avg_repo: Path) -> None:
    ctx = build_context(avg_repo)
    engine = RuleEngine()
    report = engine.scan(ctx)
    assert 40 <= report.score <= 80


def test_only_filter(good_repo: Path) -> None:
    ctx = build_context(good_repo)
    engine = RuleEngine(only=["readme_exists"])
    report = engine.scan(ctx)
    assert report.total_rules == 1
    assert report.results[0].rule_id == "readme_exists"


def test_skip_filter(good_repo: Path) -> None:
    ctx = build_context(good_repo)
    engine_all = RuleEngine()
    engine_skip = RuleEngine(skip=["readme_exists"])
    report_all = engine_all.scan(ctx)
    report_skip = engine_skip.scan(ctx)
    assert report_skip.total_rules == report_all.total_rules - 1


def test_change_plan_has_fixes(bad_repo: Path) -> None:
    ctx = build_context(bad_repo)
    engine = RuleEngine()
    report = engine.scan(ctx)
    plan = engine.build_change_plan(ctx, report)
    assert len(plan.changes) > 0
    # Should generate README, LICENSE, etc.
    file_paths = {c.file_path for c in plan.changes}
    assert "README.md" in file_paths
    assert "LICENSE" in file_paths


def test_good_repo_no_fixes(good_repo: Path) -> None:
    ctx = build_context(good_repo)
    engine = RuleEngine()
    report = engine.scan(ctx)
    plan = engine.build_change_plan(ctx, report)
    assert len(plan.changes) == 0
