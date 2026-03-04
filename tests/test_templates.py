"""Tests for template rendering."""

from pathlib import Path

from repo_doctor.models import RepoContext, StackType
from repo_doctor.templates.ci import render as render_ci
from repo_doctor.templates.code_of_conduct import render as render_coc
from repo_doctor.templates.contributing import render as render_contributing
from repo_doctor.templates.gitignore import render as render_gitignore
from repo_doctor.templates.license import render as render_license
from repo_doctor.templates.readme import render as render_readme
from repo_doctor.templates.security import render as render_security


def _make_ctx(stack: StackType = StackType.PYTHON) -> RepoContext:
    return RepoContext(
        root=Path("/tmp/test"),
        stack=stack,
        project_name="test-project",
    )


def test_readme_contains_project_name() -> None:
    content = render_readme(_make_ctx())
    assert "test-project" in content


def test_readme_minimal_is_shorter() -> None:
    standard = render_readme(_make_ctx(), style="standard")
    minimal = render_readme(_make_ctx(), style="minimal")
    assert len(minimal) < len(standard)


def test_license_mit() -> None:
    content = render_license("mit")
    assert "MIT License" in content


def test_license_apache() -> None:
    content = render_license("apache-2.0")
    assert "Apache License" in content


def test_contributing_contains_name() -> None:
    content = render_contributing(_make_ctx())
    assert "test-project" in content


def test_coc_contains_pledge() -> None:
    content = render_coc()
    assert "Pledge" in content


def test_security_contains_name() -> None:
    content = render_security(_make_ctx())
    assert "test-project" in content


def test_ci_python() -> None:
    content = render_ci(_make_ctx(StackType.PYTHON))
    assert "python" in content.lower()
    assert "pytest" in content


def test_ci_node() -> None:
    content = render_ci(_make_ctx(StackType.NODE))
    assert "node" in content.lower()
    assert "npm" in content


def test_ci_rust() -> None:
    content = render_ci(_make_ctx(StackType.RUST))
    assert "cargo" in content


def test_ci_generic() -> None:
    content = render_ci(_make_ctx(StackType.UNKNOWN))
    assert "CI" in content


def test_gitignore_python() -> None:
    content = render_gitignore(_make_ctx(StackType.PYTHON))
    assert "__pycache__" in content
    assert ".DS_Store" in content


def test_gitignore_node() -> None:
    content = render_gitignore(_make_ctx(StackType.NODE))
    assert "node_modules" in content
