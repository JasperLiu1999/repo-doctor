# Contributing to Repo Doctor

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork and install dependencies:
   ```bash
   git clone https://github.com/YOUR_USERNAME/repo-doctor.git
   cd repo-doctor
   uv sync --dev
   ```
3. Create a feature branch (`git checkout -b feature/my-feature`)
4. Make your changes
5. Run tests: `uv run pytest -x -v`
6. Run linter: `uv run ruff check src/ tests/`
7. Commit and push, then open a Pull Request

## Adding a New Rule

1. Choose the right category file in `src/repo_doctor/rules/`
2. Create a subclass of `BaseRule` with a unique `rule_id`
3. Implement `check(self, ctx: RepoContext) -> RuleResult`
4. Optionally implement `fix(self, ctx: RepoContext) -> FixResult | None`
5. Add tests in `tests/test_rules/`

The rule auto-registers via `__init_subclass__` - no manual wiring needed.

## Guidelines

- Write clear commit messages
- Add tests for new features and rules
- Keep templates concise - no fluff
- Never modify user source code in fix mode
- Follow existing code style (enforced by ruff)

## Reporting Issues

- Use the GitHub issue tracker
- Include the output of `repo-doctor scan` if relevant
- Include steps to reproduce

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
