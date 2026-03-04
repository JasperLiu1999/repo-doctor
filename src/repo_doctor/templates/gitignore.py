"""Gitignore template."""

from __future__ import annotations

from repo_doctor.models import RepoContext, StackType

_BASE = """# OS
.DS_Store
Thumbs.db
*.log

# Editor
.vscode/
.idea/
*.swp
*.swo
*~
"""

_PYTHON = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
dist/
build/
*.egg-info/
.eggs/
venv/
.venv/
env/
.env
.tox/
.mypy_cache/
.pytest_cache/
.ruff_cache/
htmlcov/
.coverage
"""

_NODE = """
# Node
node_modules/
dist/
.env
.env.local
.env.*.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.cache/
"""

_RUST = """
# Rust
/target/
Cargo.lock
"""

_GO = """
# Go
/vendor/
*.exe
*.exe~
*.dll
*.so
*.dylib
"""

_SWIFT = """
# Swift / Xcode
build/
DerivedData/
*.xcuserstate
*.xcworkspace/xcuserdata/
*.pbxuser
*.mode1v3
*.mode2v3
*.perspectivev3
xcuserdata/
*.hmap
*.ipa
*.dSYM.zip
*.dSYM
Pods/
.build/
"""


def render(ctx: RepoContext) -> str:
    parts = [_BASE.strip()]

    stack_extras = {
        StackType.PYTHON: _PYTHON,
        StackType.NODE: _NODE,
        StackType.RUST: _RUST,
        StackType.GO: _GO,
        StackType.SWIFT: _SWIFT,
    }

    for stack in [ctx.stack] + ctx.secondary_stacks:
        extra = stack_extras.get(stack)
        if extra:
            parts.append(extra.strip())

    return "\n\n".join(parts) + "\n"
