# Repo Doctor

> Turn any repository into an open-source-ready, professional repo in one command.

## Install

```bash
pipx install repo-doctor
```

## Quickstart

```bash
# Scan a repo and get a health report
repo-doctor scan /path/to/repo

# Fix issues automatically (with preview)
repo-doctor fix /path/to/repo

# Fix without prompts
repo-doctor fix --yes /path/to/repo
```

## What it checks

| Category | Rules |
|----------|-------|
| **Basics** | README, LICENSE, default branch |
| **Community** | CONTRIBUTING, CODE_OF_CONDUCT, SECURITY |
| **Build** | CI pipeline, test command, linter |
| **Hygiene** | .gitignore, no committed venv/caches, repo size |
| **Security** | No secrets (.env, .pem, id_rsa), high-entropy strings |
| **Reproducibility** | Lockfiles, pinned dependencies |

## How fixes work

Repo Doctor is **safe by default**:

- Never deletes files
- Never modifies your source code
- Only generates meta-files (README, LICENSE, CI, etc.)
- Always shows a diff preview before applying
- Use `--dry-run` to see what would change

## Config

Create `.repo-doctor.yml` in your repo:

```yaml
license: mit
ci: github-actions
readme: standard
skip:
  - lint_config
  - pinned_deps
```

Or run `repo-doctor init` to generate one interactively.

## License

MIT
