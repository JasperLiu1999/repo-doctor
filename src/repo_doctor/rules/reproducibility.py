"""Reproducibility rules: lockfiles, pinned dependencies."""

from __future__ import annotations

from repo_doctor.models import RepoContext, RuleResult, Severity, StackType
from repo_doctor.rules import BaseRule


class LockfileExistsRule(BaseRule):
    rule_id = "lockfile_exists"
    name = "Lockfile present"
    category = "reproducibility"
    severity = Severity.WARN
    weight = 5

    LOCKFILES = {
        StackType.PYTHON: [
            "poetry.lock", "Pipfile.lock", "uv.lock",
            "requirements.txt",  # counts as pinned deps
        ],
        StackType.NODE: [
            "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb",
        ],
        StackType.RUST: ["Cargo.lock"],
        StackType.GO: ["go.sum"],
    }

    def check(self, ctx: RepoContext) -> RuleResult:
        expected = self.LOCKFILES.get(ctx.stack, [])
        if not expected:
            return self._pass("No lockfile expected for this stack.")

        for f in ctx.files:
            basename = f.split("/")[-1]
            if basename in expected:
                return self._pass(evidence=[f])

        return self._fail(
            f"No lockfile found for {ctx.stack.value} project.",
            evidence=[f"Expected one of: {', '.join(expected)}"],
            suggested_fix="Generate a lockfile to ensure reproducible builds.",
        )


class PinnedDepsRule(BaseRule):
    rule_id = "pinned_deps"
    name = "Dependencies pinned"
    category = "reproducibility"
    severity = Severity.INFO
    weight = 3

    def check(self, ctx: RepoContext) -> RuleResult:
        if ctx.stack == StackType.PYTHON:
            return self._check_python(ctx)
        elif ctx.stack == StackType.NODE:
            return self._check_node(ctx)
        return self._pass("Dependency pinning check not applicable for this stack.")

    def _check_python(self, ctx: RepoContext) -> RuleResult:
        # Check requirements.txt for unpinned deps
        req_path = ctx.root / "requirements.txt"
        if not req_path.exists():
            return self._pass("No requirements.txt to check.")
        try:
            lines = req_path.read_text().splitlines()
        except OSError:
            return self._pass()

        unpinned = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            if "==" not in line and ">=" not in line and "~=" not in line:
                unpinned.append(line)

        if unpinned:
            return self._fail(
                f"{len(unpinned)} dependency(ies) without version constraints.",
                evidence=unpinned[:5],
                suggested_fix="Pin dependency versions (e.g., requests==2.31.0).",
            )
        return self._pass()

    def _check_node(self, ctx: RepoContext) -> RuleResult:
        import json

        pkg_path = ctx.root / "package.json"
        if not pkg_path.exists():
            return self._pass()
        try:
            pkg = json.loads(pkg_path.read_text())
        except (json.JSONDecodeError, OSError):
            return self._pass()

        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        unpinned = [
            name for name, ver in deps.items()
            if ver.startswith("*") or ver == "latest"
        ]
        if unpinned:
            return self._fail(
                f"{len(unpinned)} dependency(ies) using wildcard or 'latest'.",
                evidence=unpinned[:5],
                suggested_fix="Pin dependencies to specific version ranges.",
            )
        return self._pass()
