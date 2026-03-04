"""Hygiene rules: .gitignore, no committed venv/caches, repo size."""

from __future__ import annotations

from repo_doctor.models import FileOp, FixResult, RepoContext, RuleResult, Severity
from repo_doctor.rules import BaseRule
from repo_doctor.templates.gitignore import render as render_gitignore


class GitignoreExistsRule(BaseRule):
    rule_id = "gitignore_exists"
    name = ".gitignore present"
    category = "hygiene"
    severity = Severity.ERROR
    weight = 8

    def check(self, ctx: RepoContext) -> RuleResult:
        if ".gitignore" in ctx.files:
            return self._pass(evidence=[".gitignore"])
        return self._fail(
            "No .gitignore file found.",
            suggested_fix="Add a .gitignore for your project type.",
        )

    def fix(self, ctx: RepoContext) -> FixResult | None:
        if ".gitignore" in ctx.files:
            return None
        return FixResult(
            rule_id=self.rule_id,
            file_path=".gitignore",
            operation=FileOp.CREATE,
            content=render_gitignore(ctx),
            description="Create .gitignore for detected project stack",
        )


class GitignoreCoverageRule(BaseRule):
    rule_id = "gitignore_coverage"
    name = ".gitignore covers common junk"
    category = "hygiene"
    severity = Severity.WARN
    weight = 4

    ESSENTIAL_PATTERNS = [
        ".DS_Store",
        "*.log",
        "Thumbs.db",
    ]

    def check(self, ctx: RepoContext) -> RuleResult:
        gitignore_path = ctx.root / ".gitignore"
        if not gitignore_path.exists():
            return self._fail("No .gitignore to evaluate.")

        try:
            content = gitignore_path.read_text()
        except OSError:
            return self._fail("Could not read .gitignore.")

        missing = []
        for pattern in self.ESSENTIAL_PATTERNS:
            if pattern not in content:
                missing.append(pattern)

        if missing:
            return self._fail(
                f".gitignore missing common patterns: {', '.join(missing)}",
                evidence=missing,
                suggested_fix="Add missing patterns to .gitignore.",
            )
        return self._pass()

    def fix(self, ctx: RepoContext) -> FixResult | None:
        gitignore_path = ctx.root / ".gitignore"
        if not gitignore_path.exists():
            return None

        try:
            content = gitignore_path.read_text()
        except OSError:
            return None

        additions = []
        for pattern in self.ESSENTIAL_PATTERNS:
            if pattern not in content:
                additions.append(pattern)

        if not additions:
            return None

        new_content = content.rstrip("\n") + "\n\n# Added by repo-doctor\n"
        new_content += "\n".join(additions) + "\n"

        return FixResult(
            rule_id=self.rule_id,
            file_path=".gitignore",
            operation=FileOp.PATCH,
            content=new_content,
            description=f"Append missing patterns to .gitignore: {', '.join(additions)}",
        )


class NoVenvCommittedRule(BaseRule):
    rule_id = "no_venv_committed"
    name = "No venv/node_modules committed"
    category = "hygiene"
    severity = Severity.ERROR
    weight = 5

    BAD_DIRS = [
        "venv/", ".venv/", "env/",
        "node_modules/",
        "__pycache__/",
        ".tox/",
        ".mypy_cache/",
        ".pytest_cache/",
        "dist/",
        "build/",
        ".eggs/",
    ]

    def check(self, ctx: RepoContext) -> RuleResult:
        found = []
        for f in ctx.files:
            for bad in self.BAD_DIRS:
                if f.startswith(bad) or f"/{bad}" in f:
                    found.append(f)
                    break

        if found:
            # Limit evidence to first 10
            return self._fail(
                f"Found {len(found)} files in directories that should not be committed.",
                evidence=found[:10],
                suggested_fix="Remove these directories from git and add them to .gitignore.",
            )
        return self._pass()


class RepoSizeRule(BaseRule):
    rule_id = "repo_size"
    name = "Reasonable repo size"
    category = "hygiene"
    severity = Severity.INFO
    weight = 3

    MAX_TOTAL_MB = 100
    MAX_FILE_MB = 50

    def check(self, ctx: RepoContext) -> RuleResult:
        total_bytes = sum(ctx.file_sizes.values())
        total_mb = total_bytes / (1024 * 1024)

        large_files = [
            f for f, size in ctx.file_sizes.items()
            if size > self.MAX_FILE_MB * 1024 * 1024
        ]

        issues = []
        if total_mb > self.MAX_TOTAL_MB:
            issues.append(f"Total repo size is {total_mb:.1f} MB (>{self.MAX_TOTAL_MB} MB)")
        if large_files:
            issues.append(f"{len(large_files)} file(s) over {self.MAX_FILE_MB} MB")

        if issues:
            return self._fail(
                "; ".join(issues),
                evidence=large_files[:5],
                suggested_fix="Consider using Git LFS for large files or removing binaries.",
            )
        return self._pass(f"Repo size: {total_mb:.1f} MB")
