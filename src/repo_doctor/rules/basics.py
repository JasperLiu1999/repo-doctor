"""Repository basics rules: README, LICENSE."""

from __future__ import annotations

import re

from repo_doctor.models import FileOp, FixResult, RepoContext, RuleResult, Severity
from repo_doctor.rules import BaseRule
from repo_doctor.templates.license import render as render_license
from repo_doctor.templates.readme import render as render_readme


class ReadmeExistsRule(BaseRule):
    rule_id = "readme_exists"
    name = "README present"
    category = "basics"
    severity = Severity.ERROR
    weight = 15

    def check(self, ctx: RepoContext) -> RuleResult:
        for f in ctx.files:
            if re.match(r"^readme(\.\w+)?$", f, re.IGNORECASE):
                return self._pass(evidence=[f])
        return self._fail(
            "No README file found.",
            suggested_fix="Create a README.md with project description and quickstart.",
        )

    def fix(self, ctx: RepoContext) -> FixResult | None:
        for f in ctx.files:
            if re.match(r"^readme(\.\w+)?$", f, re.IGNORECASE):
                return None
        content = render_readme(ctx)
        return FixResult(
            rule_id=self.rule_id,
            file_path="README.md",
            operation=FileOp.CREATE,
            content=content,
            description="Create README.md with project overview and quickstart",
        )


class ReadmeSectionsRule(BaseRule):
    rule_id = "readme_sections"
    name = "README has key sections"
    category = "basics"
    severity = Severity.WARN
    weight = 5

    REQUIRED_PATTERNS = [
        (r"#+\s*(install|setup|getting\s*started)", "Installation/Setup"),
        (r"#+\s*(usage|quickstart|quick\s*start|how\s*to)", "Usage"),
    ]

    def check(self, ctx: RepoContext) -> RuleResult:
        readme_path = None
        for f in ctx.files:
            if re.match(r"^readme(\.\w+)?$", f, re.IGNORECASE):
                readme_path = ctx.root / f
                break
        if not readme_path:
            return self._fail("No README found to check sections.")

        try:
            content = readme_path.read_text(errors="replace").lower()
        except OSError:
            return self._fail("Could not read README.")

        missing = []
        for pattern, label in self.REQUIRED_PATTERNS:
            if not re.search(pattern, content, re.IGNORECASE):
                missing.append(label)

        if missing:
            return self._fail(
                f"README missing sections: {', '.join(missing)}",
                suggested_fix="Add Installation and Usage sections to your README.",
            )
        return self._pass()


class LicenseExistsRule(BaseRule):
    rule_id = "license_exists"
    name = "LICENSE present"
    category = "basics"
    severity = Severity.ERROR
    weight = 12

    def check(self, ctx: RepoContext) -> RuleResult:
        for f in ctx.files:
            if re.match(r"^licen[sc]e(\.\w+)?$", f, re.IGNORECASE):
                return self._pass(evidence=[f])
        return self._fail(
            "No LICENSE file found.",
            suggested_fix="Add a LICENSE file (e.g., MIT or Apache-2.0).",
        )

    def fix(self, ctx: RepoContext) -> FixResult | None:
        for f in ctx.files:
            if re.match(r"^licen[sc]e(\.\w+)?$", f, re.IGNORECASE):
                return None
        content = render_license()
        return FixResult(
            rule_id=self.rule_id,
            file_path="LICENSE",
            operation=FileOp.CREATE,
            content=content,
            description="Create MIT LICENSE file",
        )
