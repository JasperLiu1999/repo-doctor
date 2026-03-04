# Changelog

## 0.1.0 (2026-03-04)

Initial release.

### Features

- `repo-doctor scan` - Analyze any repo and produce a health report (MD + JSON)
- `repo-doctor fix` - Auto-generate missing meta-files (README, LICENSE, CI, etc.)
- `repo-doctor init` - Create a `.repo-doctor.yml` config file
- 17 rules across 6 categories: basics, community, build, hygiene, security, reproducibility
- 0-100 scoring with A/B/C/D grades
- Stack detection: Python, Node, Rust, Go, Swift
- Safe by default: never deletes files, never touches source code
- Rich terminal output with colored tables and diff previews
- `--dry-run` and `--yes` flags for CI integration
- `--strict` mode for treating warnings as errors
- `--only` and `--skip` for rule filtering
