"""CONTRIBUTING template."""

from __future__ import annotations

from repo_doctor.models import RepoContext


def render(ctx: RepoContext) -> str:
    return f"""# Contributing to {ctx.project_name}

Thank you for your interest in contributing! Here's how you can help.

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests to ensure everything works
5. Commit your changes (`git commit -m 'Add my feature'`)
6. Push to the branch (`git push origin feature/my-feature`)
7. Open a Pull Request

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/{ctx.project_name}.git
cd {ctx.project_name}
# TODO: Add setup instructions
```

## Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Follow the existing code style

## Reporting Issues

- Use the GitHub issue tracker
- Include steps to reproduce the issue
- Include expected and actual behavior
- Include relevant logs or screenshots

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
"""
