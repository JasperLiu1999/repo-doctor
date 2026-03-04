"""Rule engine: discover rules, run checks, compute score."""

from __future__ import annotations

from repo_doctor.models import (
    ChangePlan,
    RepoContext,
    RuleResult,
    ScanReport,
    compute_grade,
)
from repo_doctor.rules import BaseRule


class RuleEngine:
    def __init__(
        self,
        only: list[str] | None = None,
        skip: list[str] | None = None,
    ) -> None:
        self.only = set(only) if only else None
        self.skip = set(skip) if skip else set()

    def _get_rules(self) -> list[BaseRule]:
        rules = []
        for rule_id, cls in sorted(BaseRule._registry.items()):
            if self.only and rule_id not in self.only:
                continue
            if rule_id in self.skip:
                continue
            rules.append(cls())
        return rules

    def scan(self, ctx: RepoContext) -> ScanReport:
        rules = self._get_rules()
        results: list[RuleResult] = []

        for rule in rules:
            result = rule.check(ctx)
            results.append(result)

        total_weight = sum(r.weight for r in results)
        earned_weight = sum(r.weight for r in results if r.passed)
        score = round(earned_weight / total_weight * 100) if total_weight > 0 else 0
        grade = compute_grade(score)

        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed

        return ScanReport(
            score=score,
            grade=grade,
            results=results,
            repo_path=str(ctx.root),
            stack=ctx.stack.value,
            total_rules=len(results),
            passed_rules=passed,
            failed_rules=failed,
        )

    def build_change_plan(self, ctx: RepoContext, report: ScanReport) -> ChangePlan:
        rules = self._get_rules()
        rule_map = {r.rule_id: r for r in rules}

        changes = []
        for result in report.results:
            if result.passed or not result.auto_fixable:
                continue
            rule = rule_map.get(result.rule_id)
            if rule:
                fix = rule.fix(ctx)
                if fix:
                    changes.append(fix)

        n = len(changes)
        summary = f"{n} file(s) to {'create or modify' if n else 'change'}"
        return ChangePlan(changes=changes, summary=summary)
