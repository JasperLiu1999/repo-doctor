"""Build & quality rules: CI, test command, lint config."""

from __future__ import annotations

import json

from repo_doctor.models import FileOp, FixResult, RepoContext, RuleResult, Severity, StackType
from repo_doctor.rules import BaseRule
from repo_doctor.templates.ci import render as render_ci


class CIWorkflowRule(BaseRule):
    rule_id = "ci_workflow"
    name = "CI pipeline exists"
    category = "build"
    severity = Severity.ERROR
    weight = 10

    CI_PATTERNS = [
        ".github/workflows/",
        ".gitlab-ci.yml",
        ".circleci/",
        "Jenkinsfile",
        ".travis.yml",
        "azure-pipelines.yml",
        "bitbucket-pipelines.yml",
    ]

    def check(self, ctx: RepoContext) -> RuleResult:
        for f in ctx.files:
            for pattern in self.CI_PATTERNS:
                if f.startswith(pattern) or f == pattern.rstrip("/"):
                    return self._pass(evidence=[f])
        return self._fail(
            "No CI/CD pipeline found.",
            suggested_fix="Add a GitHub Actions workflow or other CI configuration.",
        )

    def fix(self, ctx: RepoContext) -> FixResult | None:
        for f in ctx.files:
            for pattern in self.CI_PATTERNS:
                if f.startswith(pattern) or f == pattern.rstrip("/"):
                    return None
        content = render_ci(ctx)
        return FixResult(
            rule_id=self.rule_id,
            file_path=".github/workflows/ci.yml",
            operation=FileOp.CREATE,
            content=content,
            description="Create GitHub Actions CI workflow",
        )


class TestCommandRule(BaseRule):
    rule_id = "test_command"
    name = "Test command discoverable"
    category = "build"
    severity = Severity.WARN
    weight = 5

    def check(self, ctx: RepoContext) -> RuleResult:
        # Check for test directories/files
        test_exts = (".py", ".js", ".ts", ".rs")
        has_tests = any(
            "test" in f.lower() and f.endswith(test_exts)
            for f in ctx.files
        )

        if ctx.stack == StackType.PYTHON:
            if has_tests or any(f in ctx.files for f in ["pytest.ini", "setup.cfg", "tox.ini"]):
                return self._pass("Python test infrastructure detected.")
        elif ctx.stack == StackType.NODE:
            pkg_path = ctx.root / "package.json"
            if pkg_path.exists():
                try:
                    pkg = json.loads(pkg_path.read_text())
                    if "test" in pkg.get("scripts", {}):
                        return self._pass("npm test script found.")
                except (json.JSONDecodeError, OSError):
                    pass
        elif ctx.stack == StackType.RUST:
            if has_tests:
                return self._pass("Rust tests detected.")
        elif ctx.stack == StackType.GO:
            if any(f.endswith("_test.go") for f in ctx.files):
                return self._pass("Go tests detected.")

        if has_tests:
            return self._pass("Test files detected.")

        return self._fail(
            "No test command or test files detected.",
            suggested_fix="Add tests and ensure they can be run with a standard command.",
        )


class LintConfigRule(BaseRule):
    rule_id = "lint_config"
    name = "Linter configured"
    category = "build"
    severity = Severity.INFO
    weight = 3

    LINT_FILES = [
        ".eslintrc", ".eslintrc.js", ".eslintrc.json", ".eslintrc.yml",
        "eslint.config.js", "eslint.config.mjs",
        ".flake8", ".pylintrc", "pyrightconfig.json",
        "ruff.toml", ".ruff.toml",
        ".rubocop.yml",
        "clippy.toml", ".clippy.toml",
        ".golangci.yml", ".golangci.yaml",
        "biome.json",
    ]

    def check(self, ctx: RepoContext) -> RuleResult:
        for f in ctx.files:
            basename = f.split("/")[-1]
            if basename in self.LINT_FILES:
                return self._pass(evidence=[f])

        # Check pyproject.toml for ruff/flake8 config
        if "pyproject.toml" in ctx.files:
            try:
                content = (ctx.root / "pyproject.toml").read_text()
                linters = ("[tool.ruff", "[tool.flake8", "[tool.pylint")
                if any(pat in content for pat in linters):
                    return self._pass(evidence=["pyproject.toml"])
            except OSError:
                pass

        return self._fail(
            "No linter configuration found.",
            suggested_fix="Consider adding a linter (e.g., ruff for Python, eslint for JS).",
        )
