"""Build RepoContext from a repository path."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .models import RepoContext, StackType


def _run_git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _detect_stack(files: list[str]) -> tuple[StackType, list[StackType]]:
    indicators: dict[StackType, list[str]] = {
        StackType.PYTHON: [
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "Pipfile",
        ],
        StackType.NODE: ["package.json", "package-lock.json", "yarn.lock"],
        StackType.RUST: ["Cargo.toml"],
        StackType.GO: ["go.mod"],
        StackType.SWIFT: [
            "Package.swift",
            "*.xcodeproj",
            "*.xcworkspace",
            "*.swift",
        ],
    }

    scores: dict[StackType, int] = {}
    file_set = set(files)
    basenames = {f.split("/")[-1] for f in files}
    dir_names = {f.split("/")[0] for f in files if "/" in f}

    for stack, markers in indicators.items():
        for marker in markers:
            if marker.startswith("*"):
                suffix = marker[1:]
                in_files = any(f.endswith(suffix) for f in files)
                in_dirs = any(d.endswith(suffix) for d in dir_names)
                if in_files or in_dirs:
                    scores[stack] = scores.get(stack, 0) + 1
            elif marker in file_set or marker in basenames or marker in dir_names:
                scores[stack] = scores.get(stack, 0) + 1

    if not scores:
        return StackType.UNKNOWN, []

    sorted_stacks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_stacks[0][0]
    secondary = [s for s, _ in sorted_stacks[1:]]
    return primary, secondary


def _index_files(root: Path) -> tuple[list[str], dict[str, int]]:
    tracked = _run_git(root, "ls-files")
    # Always include untracked files (so newly created files are visible)
    untracked = _run_git(root, "ls-files", "--others", "--exclude-standard")

    if tracked or untracked:
        paths = set()
        if tracked:
            paths.update(p for p in tracked.splitlines() if p)
        if untracked:
            paths.update(p for p in untracked.splitlines() if p)
        paths_list = list(paths)
    else:
        # Fallback (non-git directory): walk the directory, skip .git
        paths_list = []
        for p in root.rglob("*"):
            if ".git" in p.parts:
                continue
            if p.is_file():
                paths_list.append(str(p.relative_to(root)))

    sizes: dict[str, int] = {}
    for rel in paths_list:
        full = root / rel
        try:
            sizes[rel] = full.stat().st_size
        except OSError:
            sizes[rel] = 0

    return sorted(paths_list), sizes


def _detect_project_name(root: Path) -> str:
    return root.resolve().name


def build_context(repo_path: Path) -> RepoContext:
    root = repo_path.resolve()
    files, sizes = _index_files(root)
    stack, secondary = _detect_stack(files)

    # Git metadata
    git_status = _run_git(root, "status", "--porcelain")
    git_clean = git_status == ""
    default_branch = _run_git(root, "rev-parse", "--abbrev-ref", "HEAD") or "main"
    remote_url = _run_git(root, "remote", "get-url", "origin")
    has_remote = bool(remote_url)

    return RepoContext(
        root=root,
        stack=stack,
        secondary_stacks=secondary,
        files=files,
        file_sizes=sizes,
        git_clean=git_clean,
        default_branch=default_branch,
        has_remote=has_remote,
        remote_url=remote_url,
        project_name=_detect_project_name(root),
    )
