#!/usr/bin/env python3
"""
Generates a plain-language Access Control Matrix (ACM): which type of user
can do which high-level thing, with no permission codenames or code
references in the output. Writes both a PDF (for sharing/printing) and an
RST fragment (embedded into the Sphinx docs via `.. include::`).

Fully mechanical, no LLM involved: role -> permission data comes from the
`roles:` section of docs/api_permissions.yaml, and the mapping from those
permissions to plain-language capabilities comes from
docs/acm_capabilities.yaml. Re-run this after either file changes.

The PDF output requires pandoc and a LaTeX engine (lualatex) on PATH; pass
--no-pdf to skip it and only regenerate the RST fragment.

Usage:
    uv run python scripts/generate_acm.py
    uv run python scripts/generate_acm.py --no-pdf
    uv run python scripts/generate_acm.py --pdf-out docs/api_acm.pdf --rst-out docs/acm_generated.rst
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
DEFAULT_CAPABILITIES_YAML = "docs/acm_capabilities.yaml"
DEFAULT_PDF_OUT = "docs/api_acm.pdf"
DEFAULT_RST_OUT = "docs/acm_generated.rst"

FULL, PART, NONE = "Y", "P", "N"
STATUS_LABEL = {FULL: "Yes", PART: "Partly", NONE: "No"}


@dataclass
class Role:
    code: str
    label: str
    subtitle: str
    perms: set
    scope: str


@dataclass
class ACM:
    roles: list = field(default_factory=list)
    capabilities: list = field(default_factory=list)  # list of cap dicts
    grid: list = field(default_factory=list)  # grid[cap_idx][role_idx] -> status
    notes: list = field(default_factory=list)  # list of (title, text)


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


def evaluate(cap: dict, perms: set, scope: str) -> str:
    cap_scope = cap.get("scope")
    if cap_scope == "public":
        return FULL
    if cap_scope == "authenticated":
        return FULL if scope != "public" else NONE

    requires_any = cap.get("requires_any")
    if requires_any:
        return FULL if perms.intersection(requires_any) else NONE

    full_req = set(cap.get("full_requires_all") or [])
    if full_req and full_req.issubset(perms):
        return FULL
    partial_req = set(cap.get("partial_requires_all") or [])
    if partial_req and partial_req.issubset(perms):
        return PART
    return NONE


def compute_acm(perm_data: dict, cap_data: dict) -> ACM:
    known_roles = perm_data.get("roles", {})
    acm = ACM()

    for r in cap_data["roles"]:
        key = r["key"]
        if r.get("virtual"):
            perms, scope = set(), r["scope"]
        else:
            if key not in known_roles:
                raise SystemExit(
                    f"error: role '{key}' in acm_capabilities.yaml has no "
                    f"matching entry in {DEFAULT_PERMISSIONS_YAML}'s roles: section"
                )
            perms, scope = set(known_roles[key]["permissions"]), "role"
        acm.roles.append(
            Role(
                code=f"R{len(acm.roles) + 1}",
                label=r["label"],
                subtitle=r.get("subtitle", ""),
                perms=perms,
                scope=scope,
            )
        )

    acm.capabilities = cap_data["capabilities"]
    for cap in acm.capabilities:
        acm.grid.append([evaluate(cap, role.perms, role.scope) for role in acm.roles])

    for cap_idx, cap in enumerate(acm.capabilities):
        if cap.get("partial_note") and PART in acm.grid[cap_idx]:
            acm.notes.append((cap["label"], cap["partial_note"].strip()))

    for src, role in zip(cap_data["roles"], acm.roles, strict=True):
        footnote_from = src.get("footnote_from_role")
        if footnote_from:
            other = known_roles.get(footnote_from, {})
            full_note = (other.get("note") or "").strip().replace("\n", " ")
            # keep only the first sentence -- the source note was written
            # for api_permissions.yaml's own context and may dangle-reference
            # things ("see finding ... below") that don't apply here
            first_sentence = full_note.split(". ", 1)[0].rstrip(".") + "."
            if first_sentence.strip("."):
                acm.notes.insert(0, (role.label, first_sentence))

    return acm


# ---------------------------------------------------------------- markdown/PDF


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


def build_markdown(acm: ACM) -> str:
    role_header = " & ".join(
        r"\textbf{" + latex_esc(role.code) + "}" for role in acm.roles
    )

    symbol_map = {
        FULL: r"\cellcolor{ok}{\textbf{Yes}}",
        PART: r"\cellcolor{part}{\textbf{Partly}}",
        NONE: r"\cellcolor{no}{No}",
    }
    body_rows = []
    for cap, row_vals in zip(acm.capabilities, acm.grid, strict=True):
        cells = " & ".join(symbol_map[v] for v in row_vals)
        body_rows.append(latex_esc(cap["label"]) + " & " + cells + r" \\" + "\n\\hline")

    colspec = "|" + latex_col("0.30") + "|" + ("c|" * len(acm.roles))
    table = (
        "```{=latex}\n\\small\n\\begin{longtable}{" + colspec + "}\n\\hline\n"
        r"\textbf{Capability} & "
        + role_header
        + r" \\"
        + "\n\\hline\n\\endhead\n"
        + "\n".join(body_rows)
        + "\n\\end{longtable}\n```\n"
    )

    roles_md = "\n".join(
        f"- **{latex_esc(role.code)} -- {latex_esc(role.label)}** ({latex_esc(role.subtitle)})"
        for role in acm.roles
    )
    notes_md = (
        "\n".join(
            f"{i + 1}. **{latex_esc(title)}** -- {latex_esc(text)}"
            for i, (title, text) in enumerate(acm.notes)
        )
        or "_None._"
    )

    return f"""---
title: Who Can Do What
---

# Who can do what, on this platform

This page explains, in plain terms, what each type of user is allowed to do.
It does not describe how it is enforced in the software -- it describes the
end result, for anyone who needs to understand or check who has access to
what.

**How to read it:** each row below is a capability -- something a user
might want to do. Each column is a type of user ("role"), identified by a
short code (explained just below). A green **Yes** means that role can
fully do it. An amber **Partly** means they can do part of it, with the
limit explained in the notes further down. A grey **No** means they cannot
do it at all.

## Roles

{roles_md}

## Access table

{table}

## Legend

- \\cellcolor{{ok}}{{\\textbf{{Yes}}}}  -- this role can fully do this.
- \\cellcolor{{part}}{{\\textbf{{Partly}}}}  -- see the matching note below.
- \\cellcolor{{no}}{{No}}  -- this role cannot do this.

## Notes

{notes_md}

## Where this comes from

This page is generated automatically (`scripts/generate_acm.py`) from
`docs/api_permissions.yaml`'s code-verified `roles:` section and the
capability mapping in `docs/acm_capabilities.yaml`. It carries no manual
interpretation beyond that mapping -- for the exact technical permission
checked on every screen and action, together with the tests that confirm
it, see `docs/api_permissions.yaml` and `docs/api_roles_check.pdf`.
"""


def render_pdf(markdown: str, out_path: Path):
    header = (
        r"\usepackage{longtable}"
        "\n"
        r"\usepackage{array}"
        "\n"
        r"\usepackage{colortbl}"
        "\n"
        r"\definecolor{ok}{HTML}{DFF5E1}"
        "\n"
        r"\definecolor{part}{HTML}{FFF3D6}"
        "\n"
        r"\definecolor{no}{HTML}{F5F5F5}"
        "\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        md_file = tmp_path / "acm.md"
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
                "geometry:margin=1.5cm",
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


def build_rst(acm: ACM) -> str:
    lines = []
    lines.append(".. GENERATED FILE -- do not edit by hand.")
    lines.append("   Regenerate with: uv run python scripts/generate_acm.py")
    lines.append("")
    lines.append("Who can do what, on this platform")
    lines.append("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    lines.append("")
    lines.append(
        "This table explains, in plain terms, what each type of user is "
        "allowed to do. It does not describe how it is enforced in the "
        "software -- it describes the end result. Each row is a capability; "
        'each column is a type of user ("role"), identified by a short '
        "code. **Yes** means that role can fully do it, **Partly** means "
        "they can do part of it (see the notes below the table), and "
        "**No** means they cannot do it at all."
    )
    lines.append("")

    lines.append("Roles")
    lines.append('"""""')
    lines.append("")
    for role in acm.roles:
        suffix = f" ({role.subtitle})" if role.subtitle else ""
        lines.append(f"* **{role.code} -- {role.label}**{suffix}")
    lines.append("")

    lines.append("Access table")
    lines.append('""""""""""""')
    lines.append("")
    lines.append(".. list-table::")
    lines.append("   :header-rows: 1")
    widths = [30] + [8] * len(acm.roles)
    lines.append(f"   :widths: {' '.join(str(w) for w in widths)}")
    lines.append("")
    lines.append("   * - Capability")
    for role in acm.roles:
        lines.append(f"     - {role.code}")
    for cap, row_vals in zip(acm.capabilities, acm.grid, strict=True):
        lines.append(f"   * - {cap['label']}")
        for v in row_vals:
            lines.append(f"     - {STATUS_LABEL[v]}")
    lines.append("")

    lines.append("Notes")
    lines.append('"""""')
    lines.append("")
    if acm.notes:
        for title, text in acm.notes:
            lines.append(f"* **{title}** -- {text}")
    else:
        lines.append("*None.*")
    lines.append("")

    lines.append(
        "This section is generated automatically "
        "(``scripts/generate_acm.py``) from ``docs/api_permissions.yaml``'s "
        "code-verified ``roles:`` section and the capability mapping in "
        "``docs/acm_capabilities.yaml``. For the exact technical permission "
        "checked on every screen and action, together with the tests that "
        "confirm it, see ``docs/api_permissions.yaml`` and "
        "``docs/api_roles_check.pdf``."
    )
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--permissions-yaml", default=DEFAULT_PERMISSIONS_YAML)
    parser.add_argument("--capabilities-yaml", default=DEFAULT_CAPABILITIES_YAML)
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
    cap_data = yaml.safe_load((root / args.capabilities_yaml).read_text())

    acm = compute_acm(perm_data, cap_data)

    if not args.no_rst:
        rst_path = root / args.rst_out
        rst_path.write_text(build_rst(acm))
        print(f"wrote {rst_path}")

    if not args.no_pdf:
        markdown = build_markdown(acm)
        pdf_path = root / args.pdf_out
        render_pdf(markdown, pdf_path)
        print(f"wrote {pdf_path}")


if __name__ == "__main__":
    main()
