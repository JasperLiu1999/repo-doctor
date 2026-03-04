"""Community & governance rules: CONTRIBUTING, CODE_OF_CONDUCT, SECURITY."""

from __future__ import annotations

import re

from repo_doctor.models import FileOp, FixResult, RepoContext, RuleResult, Severity
from repo_doctor.rules import BaseRule
from repo_doctor.templates.code_of_conduct import render as render_coc
from repo_doctor.templates.contributing import render as render_contributing
from repo_doctor.templates.security import render as render_security


class ContributingExistsRule(BaseRule):
    rule_id = "contributing_exists"
    name = "CONTRIBUTING present"
    category = "community"
    severity = Severity.WARN
    weight = 6

    def check(self, ctx: RepoContext) -> RuleResult:
        for f in ctx.files:
            if re.match(r"^contributing(\.\w+)?$", f, re.IGNORECASE):
                return self._pass(evidence=[f])
        return self._fail(
            "No CONTRIBUTING file found.",
            suggested_fix="Add a CONTRIBUTING.md to guide contributors.",
        )

    def fix(self, ctx: RepoContext) -> FixResult | None:
        for f in ctx.files:
            if re.match(r"^contributing(\.\w+)?$", f, re.IGNORECASE):
                return None
        return FixResult(
            rule_id=self.rule_id,
            file_path="CONTRIBUTING.md",
            operation=FileOp.CREATE,
            content=render_contributing(ctx),
            description="Create CONTRIBUTING.md with contribution guidelines",
        )


class CodeOfConductExistsRule(BaseRule):
    rule_id = "code_of_conduct_exists"
    name = "CODE_OF_CONDUCT present"
    category = "community"
    severity = Severity.WARN
    weight = 5

    def check(self, ctx: RepoContext) -> RuleResult:
        for f in ctx.files:
            if re.match(r"^code[_-]of[_-]conduct(\.\w+)?$", f, re.IGNORECASE):
                return self._pass(evidence=[f])
        return self._fail(
            "No CODE_OF_CONDUCT file found.",
            suggested_fix="Add a CODE_OF_CONDUCT.md (e.g., Contributor Covenant).",
        )

    def fix(self, ctx: RepoContext) -> FixResult | None:
        for f in ctx.files:
            if re.match(r"^code[_-]of[_-]conduct(\.\w+)?$", f, re.IGNORECASE):
                return None
        return FixResult(
            rule_id=self.rule_id,
            file_path="CODE_OF_CONDUCT.md",
            operation=FileOp.CREATE,
            content=render_coc(),
            description="Create CODE_OF_CONDUCT.md (Contributor Covenant)",
        )


class SecurityPolicyRule(BaseRule):
    rule_id = "security_policy"
    name = "SECURITY policy present"
    category = "community"
    severity = Severity.WARN
    weight = 5

    def check(self, ctx: RepoContext) -> RuleResult:
        for f in ctx.files:
            if re.match(r"^security(\.\w+)?$", f, re.IGNORECASE):
                return self._pass(evidence=[f])
        return self._fail(
            "No SECURITY policy file found.",
            suggested_fix="Add a SECURITY.md with vulnerability reporting instructions.",
        )

    def fix(self, ctx: RepoContext) -> FixResult | None:
        for f in ctx.files:
            if re.match(r"^security(\.\w+)?$", f, re.IGNORECASE):
                return None
        return FixResult(
            rule_id=self.rule_id,
            file_path="SECURITY.md",
            operation=FileOp.CREATE,
            content=render_security(ctx),
            description="Create SECURITY.md with vulnerability reporting policy",
        )
