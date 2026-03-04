"""Rule engine base class and auto-registration."""

from __future__ import annotations

from abc import abstractmethod

from repo_doctor.models import FixResult, RepoContext, RuleResult, Severity


class BaseRule:
    """Base class for all rules. Subclasses auto-register via __init_subclass__."""

    rule_id: str = ""
    name: str = ""
    category: str = ""
    severity: Severity = Severity.WARN
    weight: int = 5

    _registry: dict[str, type[BaseRule]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if cls.rule_id:
            BaseRule._registry[cls.rule_id] = cls

    @abstractmethod
    def check(self, ctx: RepoContext) -> RuleResult:
        ...

    def fix(self, ctx: RepoContext) -> FixResult | None:
        return None

    def _pass(self, rationale: str = "", evidence: list[str] | None = None) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            name=self.name,
            category=self.category,
            severity=self.severity,
            passed=True,
            weight=self.weight,
            rationale=rationale or f"{self.name}: OK",
            evidence=evidence or [],
            auto_fixable=self.fix.__func__ is not BaseRule.fix,
        )

    def _fail(
        self,
        rationale: str,
        evidence: list[str] | None = None,
        suggested_fix: str = "",
    ) -> RuleResult:
        return RuleResult(
            rule_id=self.rule_id,
            name=self.name,
            category=self.category,
            severity=self.severity,
            passed=False,
            weight=self.weight,
            rationale=rationale,
            evidence=evidence or [],
            suggested_fix=suggested_fix,
            auto_fixable=self.fix.__func__ is not BaseRule.fix,
        )


# Import rule modules to trigger registration
from repo_doctor.rules import (  # noqa: E402, F401
    basics,
    build,
    community,
    hygiene,
    reproducibility,
    security,
)
