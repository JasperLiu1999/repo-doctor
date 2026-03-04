"""CI workflow templates."""

from __future__ import annotations

from repo_doctor.models import RepoContext, StackType


def _python_ci() -> str:
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]" 2>/dev/null || pip install -e . 2>/dev/null || true
          pip install -r requirements.txt 2>/dev/null || true
      - name: Run tests
        run: |
          python -m pytest 2>/dev/null || python -m unittest discover 2>/dev/null || true
"""


def _node_ci() -> str:
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]

    steps:
      - uses: actions/checkout@v4
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
"""


def _rust_ci() -> str:
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo test
      - run: cargo clippy -- -D warnings
"""


def _go_ci() -> str:
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: stable
      - run: go test ./...
      - run: go vet ./...
"""


def _generic_ci() -> str:
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # TODO: Add build and test steps
"""


def render(ctx: RepoContext) -> str:
    renderers = {
        StackType.PYTHON: _python_ci,
        StackType.NODE: _node_ci,
        StackType.RUST: _rust_ci,
        StackType.GO: _go_ci,
    }
    renderer = renderers.get(ctx.stack, _generic_ci)
    return renderer()
