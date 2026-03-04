"""README template."""

from __future__ import annotations

from repo_doctor.models import RepoContext, StackType


def _install_section(ctx: RepoContext) -> str:
    if ctx.stack == StackType.PYTHON:
        return """## Installation

```bash
pip install {name}
```""".format(name=ctx.project_name)
    elif ctx.stack == StackType.NODE:
        return """## Installation

```bash
npm install {name}
```""".format(name=ctx.project_name)
    elif ctx.stack == StackType.RUST:
        return """## Installation

```bash
cargo install {name}
```""".format(name=ctx.project_name)
    elif ctx.stack == StackType.GO:
        return """## Installation

```bash
go install {name}@latest
```""".format(name=ctx.project_name)
    return """## Installation

```bash
# TODO: Add installation instructions
```"""


def _usage_section(ctx: RepoContext) -> str:
    return """## Usage

```bash
# TODO: Add usage examples
```"""


def render(ctx: RepoContext, style: str = "standard") -> str:
    parts = [
        f"# {ctx.project_name}\n",
        f"> TODO: Add a one-line description of {ctx.project_name}.\n",
    ]

    if style != "minimal":
        parts.append(_install_section(ctx))
        parts.append("")

    parts.append(_usage_section(ctx))
    parts.append("")

    if style != "minimal":
        parts.append("## Contributing\n")
        parts.append("See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.\n")
        parts.append("## License\n")
        parts.append(
            "This project is licensed under the MIT License "
            "- see [LICENSE](LICENSE) for details.\n"
        )

    return "\n".join(parts)
