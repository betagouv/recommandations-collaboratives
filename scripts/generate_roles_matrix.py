#!/usr/bin/env python3
"""
Generates a fine-grained, developer-facing REST API permissions table: one
row per viewset/endpoint x verb, with the actual permission expression,
the roles it maps to, the code_ref to jump to, and any flags (severity,
undocumented gap, deprecated, unverified). Unlike generate_acm.py's plain-
language capability matrix, this keeps the technical vocabulary
(permission codenames, code_ref) so a developer can go straight to the
enforcing code.

Fully mechanical, no LLM involved: everything comes straight from
docs/api_permissions.yaml's `viewsets:` and `endpoints:` sections. Re-run
this after that file changes.

The PDF output requires pandoc and a LaTeX engine (lualatex) on PATH; pass
--no-pdf to skip it and only regenerate the RST fragment.

Usage:
    uv run python scripts/generate_roles_matrix.py
    uv run python scripts/generate_roles_matrix.py --no-pdf
    uv run python scripts/generate_roles_matrix.py --pdf-out docs/api_roles_matrix.pdf
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_PERMISSIONS_YAML = "docs/api_permissions.yaml"
DEFAULT_PDF_OUT = "docs/api_roles_matrix.pdf"
DEFAULT_RST_OUT = "docs/roles_matrix_generated.rst"

SEVERITY_ABBR = {"High": "H", "Medium": "M", "Low": "L"}


@dataclass
class Row:
    source: str  # "viewset" or "endpoint"
    name: str
    verb: str
    permission: str
    roles: list
    code_ref: str
    flags: list = field(default_factory=list)
    n_tests: int = 0


def tool_path(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"error: '{name}' not found on PATH")
    return path


def repo_root() -> Path:
    out = subprocess.run(  # noqa: S603 -- hardcoded, non-user-controlled arguments
        [tool_path("git"), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip())


def flags_for(container: dict, action: dict) -> list:
    """Collect short developer-facing flags for one row.

    `container` is the enclosing viewset/endpoint dict (for deprecated/
    same_as), `action` is the specific action dict actually describing this
    row (may be `container` itself for action-less endpoints).
    """
    flags = []
    if container.get("deprecated"):
        flags.append("DEPRECATED?")
    severity = action.get("severity") or container.get("severity")
    if severity:
        flags.append(SEVERITY_ABBR.get(severity, severity))
    verified = action.get("verified", "unset")
    if verified is None:
        flags.append("gap")  # undocumented in the original source doc
    elif verified is False:
        flags.append("MISMATCH")
    if container.get("skip_check") or action.get("skip_check"):
        flags.append("skip")
    return flags


def flatten(perm_data: dict) -> list:
    rows = []

    for vs in perm_data.get("viewsets", []):
        vs_code_ref = vs.get("code_ref", "")
        for action in vs.get("actions", []):
            code_ref = action.get("code_ref") or vs_code_ref
            rows.append(
                Row(
                    source="viewset",
                    name=vs["name"],
                    verb=str(action.get("verb", "")),
                    permission=str(action.get("permission", "")),
                    roles=action.get("roles") or [],
                    code_ref=code_ref,
                    flags=flags_for(vs, action),
                    n_tests=len(action.get("tests") or []),
                )
            )

    for ep in perm_data.get("endpoints", []):
        ep_code_ref = ep.get("code_ref", "")
        actions = ep.get("actions")
        if actions:
            for action in actions:
                code_ref = action.get("code_ref") or ep_code_ref
                rows.append(
                    Row(
                        source="endpoint",
                        name=ep["name"],
                        verb=str(action.get("verb", "")),
                        permission=str(action.get("permission", "")),
                        roles=action.get("roles") or [],
                        code_ref=code_ref,
                        flags=flags_for(ep, action),
                        n_tests=len(action.get("tests") or []),
                    )
                )
        else:
            # single-purpose APIView: one row, `route` stands in for verb,
            # `permission` is free-form prose rather than a codename.
            rows.append(
                Row(
                    source="endpoint",
                    name=ep["name"],
                    verb=ep.get("route", ""),
                    permission=str(ep.get("permission", "")),
                    roles=ep.get("roles") or [],
                    code_ref=ep_code_ref,
                    flags=flags_for(ep, ep),
                    n_tests=len(ep.get("tests") or []),
                )
            )

    return rows


def latex_esc(s) -> str:
    s = str(s)
    s = s.replace("\\", "@@BS@@")
    s = s.replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
    s = s.replace("#", r"\#").replace("_", r"\_")
    s = s.replace("{", r"\{").replace("}", r"\}")
    s = s.replace("~", r"\textasciitilde{}")
    s = s.replace("^", r"\textasciicircum{}")
    s = s.replace('"', "''")
    s = s.replace("@@BS@@", "\\")
    return s


def latex_col(width: str) -> str:
    return r">{\raggedright\arraybackslash}p{%s\linewidth}" % width


def build_markdown(rows: list) -> str:
    colspec = (
        "|"
        + "|".join(
            latex_col(w) for w in ("0.23", "0.10", "0.20", "0.27", "0.06", "0.05")
        )
        + "|"
    )

    body_rows = []
    for row in rows:
        roles_str = ", ".join(row.roles) if row.roles else r"\textit{--}"
        flags_str = latex_esc(", ".join(row.flags) if row.flags else "")
        tests_str = r"\textcolor{red}{0}" if row.n_tests == 0 else str(row.n_tests)
        cells = [
            latex_esc(row.name),
            latex_esc(row.verb),
            latex_esc(row.permission),
            roles_str if roles_str == r"\textit{--}" else latex_esc(roles_str),
            tests_str,
            flags_str,
        ]
        body_rows.append(" & ".join(cells) + r" \\" + "\n\\hline")

    table = (
        "```{=latex}\n\\tiny\n\\begin{longtable}{" + colspec + "}\n\\hline\n"
        r"\textbf{Viewset / Endpoint} & \textbf{Verb} & \textbf{Permission} & "
        r"\textbf{Roles} & \textbf{\#T} & \textbf{Flags} \\"
        + "\n\\hline\n\\endhead\n"
        + "\n".join(body_rows)
        + "\n\\end{longtable}\n```\n"
    )

    n_gap = sum(1 for r in rows if "gap" in r.flags)
    n_mismatch = sum(1 for r in rows if "MISMATCH" in r.flags)
    n_untested = sum(1 for r in rows if r.n_tests == 0)

    return f"""---
title: REST API Permissions -- Developer Reference
---

# REST API permissions -- developer reference

One row per viewset/endpoint x verb, straight from the code-verified
`docs/api_permissions.yaml`. Unlike the plain-language Access Control
Matrix, this keeps permission codenames, role codes, and test counts so
you can jump straight to the enforcing code.

**#T** is the number of tests found exercising that row's permission --
**0** (highlighted) means no test was located for it, not necessarily that
none exists. **Flags**: a severity letter (H/M/L) when a concern was
noted, `gap` when the row was undocumented in the original source and
added from code, `MISMATCH` when code contradicts what was documented,
`skip` when this row is excluded from the automated staleness check
(`scripts/check_permissions_matrix.py`), `DEPRECATED?` when the source
doc's deprecated marker is itself disputed (see the row's entry in the
YAML for detail).

Summary: {len(rows)} rows, {n_gap} undocumented gaps found from code,
{n_mismatch} confirmed mismatches, {n_untested} with no test located.

## Table

{table}

## Where this comes from

Generated automatically (`scripts/generate_roles_matrix.py`) from
`docs/api_permissions.yaml`. For the full detail behind any row --
discrepancy notes, exact test file/line, roles-vs-code reasoning -- open
that file and search for the viewset/endpoint name. To check whether this
table has drifted from the code since it was last verified, run
`scripts/check_permissions_matrix.py`.
"""


def render_pdf(markdown: str, out_path: Path):
    header = (
        r"\usepackage{longtable}"
        "\n"
        r"\usepackage{array}"
        "\n"
        r"\usepackage{colortbl}"
        "\n"
        r"\usepackage[a3paper,landscape,margin=1cm]{geometry}"
        "\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        md_file = tmp_path / "roles_matrix.md"
        header_file = tmp_path / "header.tex"
        md_file.write_text(markdown)
        header_file.write_text(header)

        result = subprocess.run(  # noqa: S603 -- hardcoded, non-user-controlled arguments
            [
                tool_path("pandoc"),
                str(md_file),
                "-o",
                str(out_path),
                "--pdf-engine=lualatex",
                "-V",
                "colorlinks=true",
                "-H",
                str(header_file),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            raise SystemExit(f"error: pandoc failed with exit code {result.returncode}")
        overfull = [
            line for line in result.stderr.splitlines() if "verfull" in line.lower()
        ]
        if overfull:
            print("warning: layout may not fit the page:", file=sys.stderr)
            for line in overfull:
                print(f"  {line}", file=sys.stderr)


# --------------------------------------------------------------------- RST


def rst_escape(s) -> str:
    s = str(s)
    return s.replace("\\", "\\\\").replace("`", r"\`").replace("*", r"\*")


def build_rst(rows: list) -> str:
    lines = []
    lines.append(".. GENERATED FILE -- do not edit by hand.")
    lines.append("   Regenerate with: uv run python scripts/generate_roles_matrix.py")
    lines.append("")
    lines.append("REST API permissions -- developer reference")
    lines.append("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    lines.append("")
    lines.append(
        "One row per viewset/endpoint x verb, straight from "
        "``docs/api_permissions.yaml``. **#T** is the number of tests "
        "found exercising that row; **Flags** mark severity (H/M/L), "
        "``gap`` (undocumented in the original source), ``MISMATCH`` "
        "(code contradicts the doc), or ``skip`` (excluded from the "
        "automated staleness check)."
    )
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1")
    lines.append("   :widths: 22 8 20 27 6 10")
    lines.append("")
    lines.append("   * - Viewset / Endpoint")
    lines.append("     - Verb")
    lines.append("     - Permission")
    lines.append("     - Roles")
    lines.append("     - #T")
    lines.append("     - Flags")
    for row in rows:
        roles_str = ", ".join(row.roles) if row.roles else "--"
        flags_str = ", ".join(row.flags) if row.flags else ""
        lines.append(f"   * - {rst_escape(row.name)}")
        lines.append(f"     - {rst_escape(row.verb)}")
        lines.append(f"     - {rst_escape(row.permission)}")
        lines.append(f"     - {rst_escape(roles_str)}")
        lines.append(f"     - {row.n_tests}")
        lines.append(f"     - {rst_escape(flags_str)}")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--permissions-yaml", default=DEFAULT_PERMISSIONS_YAML)
    parser.add_argument("--pdf-out", default=DEFAULT_PDF_OUT)
    parser.add_argument("--rst-out", default=DEFAULT_RST_OUT)
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="skip PDF generation (no pandoc/lualatex needed)",
    )
    parser.add_argument("--no-rst", action="store_true", help="skip RST generation")
    args = parser.parse_args()

    if not args.no_pdf:
        for tool in ("pandoc", "lualatex"):
            if not shutil.which(tool):
                raise SystemExit(
                    f"error: '{tool}' not found on PATH -- install it, or pass --no-pdf"
                )

    root = repo_root()
    perm_data = yaml.safe_load((root / args.permissions_yaml).read_text())
    rows = flatten(perm_data)

    if not args.no_rst:
        rst_path = root / args.rst_out
        rst_path.write_text(build_rst(rows))
        print(f"wrote {rst_path}")

    if not args.no_pdf:
        markdown = build_markdown(rows)
        pdf_path = root / args.pdf_out
        render_pdf(markdown, pdf_path)
        print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
