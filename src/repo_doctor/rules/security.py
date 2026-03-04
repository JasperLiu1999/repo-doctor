"""Security rules: no secrets, no high-entropy strings."""

from __future__ import annotations

import math
import re

from repo_doctor.models import RepoContext, RuleResult, Severity
from repo_doctor.rules import BaseRule


class NoSecretsRule(BaseRule):
    rule_id = "no_secrets"
    name = "No secret files committed"
    category = "security"
    severity = Severity.ERROR
    weight = 8

    SECRET_PATTERNS = [
        r"\.env$",
        r"\.env\.\w+$",
        r".*\.pem$",
        r".*\.key$",
        r"id_rsa",
        r"id_ed25519",
        r"id_ecdsa",
        r"id_dsa",
        r"\.htpasswd$",
        r"credentials\.json$",
        r"secrets\.ya?ml$",
        r".*\.p12$",
        r".*\.pfx$",
        r".*\.jks$",
    ]

    SAFE_PREFIXES = [
        ".env.example",
        ".env.sample",
        ".env.template",
    ]

    def check(self, ctx: RepoContext) -> RuleResult:
        found = []
        for f in ctx.files:
            basename = f.split("/")[-1]
            # Skip safe examples
            if any(basename.startswith(safe) for safe in self.SAFE_PREFIXES):
                continue
            for pattern in self.SECRET_PATTERNS:
                if re.search(pattern, basename, re.IGNORECASE):
                    found.append(f)
                    break

        if found:
            return self._fail(
                f"Found {len(found)} potentially sensitive file(s).",
                evidence=found[:10],
                suggested_fix="Remove these files from git history and add them to .gitignore.",
            )
        return self._pass()


class NoHighEntropyRule(BaseRule):
    rule_id = "no_high_entropy"
    name = "No high-entropy strings"
    category = "security"
    severity = Severity.INFO
    weight = 3

    # Only check certain file types
    CHECK_EXTENSIONS = {
        ".py", ".js", ".ts", ".rb", ".go", ".rs", ".java",
        ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini",
        ".sh", ".bash", ".env",
    }

    MIN_LENGTH = 20
    ENTROPY_THRESHOLD = 4.5

    def _shannon_entropy(self, s: str) -> float:
        if not s:
            return 0.0
        freq: dict[str, int] = {}
        for c in s:
            freq[c] = freq.get(c, 0) + 1
        length = len(s)
        return -sum(
            (count / length) * math.log2(count / length)
            for count in freq.values()
        )

    def check(self, ctx: RepoContext) -> RuleResult:
        suspicious: list[str] = []
        token_pattern = re.compile(r'["\']([A-Za-z0-9+/=_\-]{20,})["\']')

        for f in ctx.files:
            ext = "." + f.rsplit(".", 1)[-1] if "." in f else ""
            if ext not in self.CHECK_EXTENSIONS:
                continue

            full_path = ctx.root / f
            try:
                content = full_path.read_text(errors="replace")
            except OSError:
                continue

            # Limit to first 500 lines to keep it fast
            for i, line in enumerate(content.splitlines()[:500]):
                for match in token_pattern.finditer(line):
                    token = match.group(1)
                    if len(token) >= self.MIN_LENGTH:
                        entropy = self._shannon_entropy(token)
                        if entropy >= self.ENTROPY_THRESHOLD:
                            suspicious.append(f"{f}:{i + 1}")
                            if len(suspicious) >= 10:
                                break
                if len(suspicious) >= 10:
                    break
            if len(suspicious) >= 10:
                break

        if suspicious:
            return self._fail(
                f"Found {len(suspicious)} high-entropy string(s) that may be secrets.",
                evidence=suspicious,
                suggested_fix=(
                    "Review these strings. If they are secrets, "
                    "move them to environment variables."
                ),
            )
        return self._pass()
