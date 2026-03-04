"""SECURITY policy template."""

from __future__ import annotations

from repo_doctor.models import RepoContext


def render(ctx: RepoContext) -> str:
    return f"""# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in {ctx.project_name}, please report it responsibly.

**Do not open a public issue.**

Instead, please send an email to **[SECURITY_EMAIL]** with:

- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix and disclosure**: Coordinated with reporter

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |

## Security Best Practices

- Keep dependencies up to date
- Use the latest stable release
- Report vulnerabilities responsibly
"""
