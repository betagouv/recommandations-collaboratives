#!/usr/bin/env python3
"""
Checks docs/api_permissions.yaml for staleness: for every viewset action,
endpoint, and test it references, resolves the enclosing Python symbol
(class/method/function) rather than trusting the recorded line numbers
directly, and compares that symbol's source text between the matrix's
`verified_commit` baseline and the current working tree. Flags anything
whose *symbol* body actually changed, so unrelated edits elsewhere in the
same file (or line drift from unrelated code shifting) don't cause noise.

Usage:
    uv run python scripts/check_permissions_matrix.py
    uv run python scripts/check_permissions_matrix.py --only-stale
    uv run python scripts/check_permissions_matrix.py --json
    uv run python scripts/check_permissions_matrix.py --commit <sha>
    uv run python scripts/check_permissions_matrix.py --update

Exit code is 1 if anything needs review (unless --update succeeds), else 0.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

DEFAULT_YAML = "docs/api_permissions.yaml"

PY_PATH_RE = re.compile(r"[\w./-]+\.py")
LINE_NUM_RE = re.compile(r":(\d+)")
TEST_REF_RE = re.compile(r"^([\w./-]+\.py)(?::([\w.]+))?\s*(?:\((.*)\))?\s*$")


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip())


def git_show(commit: str, path: str, root: Path) -> str | None:
    result = subprocess.run(  # noqa: S603
        ["git", "show", f"{commit}:{path}"],  # noqa: S607
        capture_output=True,
        text=True,
        cwd=root,
    )
    if result.returncode != 0:
        return None
    return result.stdout


def read_worktree(path: str, root: Path) -> str | None:
    p = root / path
    if not p.exists():
        return None
    try:
        return p.read_text()
    except (UnicodeDecodeError, OSError):
        return None


@dataclass
class SymbolInfo:
    name: str
    start: int
    end: int
    text: str


@dataclass
class SymbolIndex:
    by_name: dict[str, SymbolInfo] = field(default_factory=dict)
    by_line: dict[int, str] = field(default_factory=dict)

    @classmethod
    def from_source(cls, source: str) -> "SymbolIndex | None":
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None
        lines = source.splitlines()
        idx = cls()

        def visit(node: ast.AST, prefix: str = ""):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    qualname = f"{prefix}{child.name}"
                    # decorators (e.g. @action(..., permission_classes=[...]))
                    # often carry permission-relevant config themselves, and
                    # a code_ref line number may point at one -- include them
                    # in the symbol's span so both line-lookup and the
                    # change-detection text comparison cover them.
                    deco_start = min(
                        (d.lineno for d in child.decorator_list), default=child.lineno
                    )
                    start, end = deco_start, (child.end_lineno or child.lineno)
                    text = "\n".join(lines[start - 1 : end])
                    idx.by_name[qualname] = SymbolInfo(qualname, start, end, text)
                    idx.by_name.setdefault(child.name, idx.by_name[qualname])
                    for ln in range(start, end + 1):
                        idx.by_line[ln] = qualname
                    visit(child, prefix=f"{qualname}.")
                elif isinstance(child, ast.ClassDef):
                    qualname = f"{prefix}{child.name}"
                    start, end = child.lineno, (child.end_lineno or child.lineno)
                    text = "\n".join(lines[start - 1 : end])
                    idx.by_name[qualname] = SymbolInfo(qualname, start, end, text)
                    for ln in range(start, end + 1):
                        idx.by_line.setdefault(ln, qualname)
                    visit(child, prefix=f"{qualname}.")
                else:
                    visit(child, prefix=prefix)

        visit(tree)
        return idx


@dataclass
class CheckResult:
    label: str
    path: str
    symbol: str | None
    status: str  # unchanged | changed | missing | new-file | deleted-file | unresolved
    detail: str = ""


def extract_refs(text: str) -> list[tuple[str, str | None, int | None]]:
    """Best-effort extraction of (path, symbol_name, line_hint) from a
    free-text code_ref/tests string. Returns possibly multiple refs when a
    string lists several line numbers for one file with no named symbol."""
    if not text:
        return []
    paths = PY_PATH_RE.findall(text)
    if not paths:
        return []
    path = paths[0]

    m = TEST_REF_RE.match(text.strip())
    if m and m.group(1) == path and m.group(2) and not m.group(2).isdigit():
        return [(path, m.group(2), None)]

    # look for a colon-attached line number right after the path, e.g. "foo.py:56-216 (...)"
    after_path = text.split(path, 1)[1]
    line_match = LINE_NUM_RE.match(after_path)
    if line_match:
        return [(path, None, int(line_match.group(1)))]

    # fall back: pull every integer out of the trailing parenthetical, if any
    paren = re.search(r"\((.*)\)", text)
    if paren:
        nums = [int(n) for n in re.findall(r"\d+", paren.group(1))]
        if nums:
            return [(path, None, n) for n in nums]

    # no line info at all -- whole-file fallback
    return [(path, None, None)]


class Checker:
    def __init__(self, root: Path, baseline_commit: str):
        self.root = root
        self.baseline_commit = baseline_commit
        self._baseline_cache: dict[str, str | None] = {}
        self._current_cache: dict[str, str | None] = {}
        self._baseline_idx: dict[str, SymbolIndex | None] = {}
        self._current_idx: dict[str, SymbolIndex | None] = {}

    def _baseline_source(self, path: str) -> str | None:
        if path not in self._baseline_cache:
            self._baseline_cache[path] = git_show(self.baseline_commit, path, self.root)
        return self._baseline_cache[path]

    def _current_source(self, path: str) -> str | None:
        if path not in self._current_cache:
            self._current_cache[path] = read_worktree(path, self.root)
        return self._current_cache[path]

    def _baseline_symbols(self, path: str) -> SymbolIndex | None:
        if path not in self._baseline_idx:
            src = self._baseline_source(path)
            self._baseline_idx[path] = (
                SymbolIndex.from_source(src) if src is not None else None
            )
        return self._baseline_idx[path]

    def _current_symbols(self, path: str) -> SymbolIndex | None:
        if path not in self._current_idx:
            src = self._current_source(path)
            self._current_idx[path] = (
                SymbolIndex.from_source(src) if src is not None else None
            )
        return self._current_idx[path]

    def check_one(
        self, label: str, path: str, symbol_hint: str | None, line_hint: int | None
    ) -> CheckResult:
        baseline_src = self._baseline_source(path)
        current_src = self._current_source(path)

        if baseline_src is None:
            return CheckResult(
                label,
                path,
                symbol_hint,
                "new-file",
                "not found at baseline commit — added since, nothing to compare",
            )
        if current_src is None:
            return CheckResult(
                label,
                path,
                symbol_hint,
                "deleted-file",
                "file no longer exists in the working tree",
            )

        baseline_idx = self._baseline_symbols(path)
        current_idx = self._current_symbols(path)

        if baseline_idx is None or current_idx is None:
            # AST parse failed (shouldn't happen for valid Python) -- fall
            # back to whole-file text comparison
            status = "unchanged" if baseline_src == current_src else "changed"
            return CheckResult(
                label,
                path,
                symbol_hint,
                status,
                "whole-file fallback (AST parse failed)",
            )

        symbol_name = symbol_hint
        if symbol_name is None and line_hint is not None:
            symbol_name = baseline_idx.by_line.get(line_hint)
        if symbol_name is None and line_hint is None and symbol_hint is None:
            status = "unchanged" if baseline_src == current_src else "changed"
            return CheckResult(
                label,
                path,
                None,
                status,
                "whole-file fallback (no symbol/line recorded)",
            )
        if symbol_name is None:
            return CheckResult(
                label,
                path,
                None,
                "unresolved",
                f"no symbol found at line {line_hint} in baseline",
            )

        baseline_symbol = baseline_idx.by_name.get(symbol_name)
        if baseline_symbol is None:
            return CheckResult(
                label,
                path,
                symbol_name,
                "unresolved",
                "symbol not found in baseline commit (recorded ref may be stale)",
            )

        current_symbol = current_idx.by_name.get(symbol_name)
        if current_symbol is None:
            return CheckResult(
                label,
                path,
                symbol_name,
                "missing",
                "symbol no longer found in the working tree — renamed, moved, or removed",
            )

        if baseline_symbol.text == current_symbol.text:
            return CheckResult(label, path, symbol_name, "unchanged")
        return CheckResult(
            label,
            path,
            symbol_name,
            "changed",
            f"body differs between {self.baseline_commit[:12]} and working tree",
        )

    def check_ref(self, label: str, text: str) -> list[CheckResult]:
        refs = extract_refs(text)
        if not refs:
            return []
        return [self.check_one(label, path, name, line) for path, name, line in refs]


NEEDS_REVIEW = {"changed", "missing", "unresolved"}


def iter_entries(data: dict):
    """Yields (owner_label, code_ref_text, tests_texts, entry_verified_commit).
    Entries (or their parent viewset/endpoint) marked `skip_check: true` are
    omitted entirely."""
    for vs in data.get("viewsets", []):
        if vs.get("skip_check"):
            continue
        vs_name = vs["name"]
        vs_commit = vs.get("verified_commit")
        actions = vs.get("actions") or []
        if not actions:
            if vs.get("code_ref"):
                yield (vs_name, vs.get("code_ref"), vs.get("tests") or [], vs_commit)
            continue
        for a in actions:
            if a.get("skip_check"):
                continue
            label = f"{vs_name} :: {a.get('verb')}"
            yield (
                label,
                a.get("code_ref"),
                a.get("tests") or [],
                a.get("verified_commit") or vs_commit,
            )

    for ep in data.get("endpoints", []):
        if ep.get("skip_check"):
            continue
        ep_name = ep["name"]
        ep_commit = ep.get("verified_commit")
        sub_actions = ep.get("actions") or []
        if not sub_actions:
            yield (ep_name, ep.get("code_ref"), ep.get("tests") or [], ep_commit)
            continue
        for a in sub_actions:
            if a.get("skip_check"):
                continue
            label = f"{ep_name} :: {a.get('verb')}"
            yield (
                label,
                a.get("code_ref"),
                a.get("tests") or [],
                a.get("verified_commit") or ep_commit,
            )


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--yaml",
        default=DEFAULT_YAML,
        help="path to the reference matrix (relative to repo root)",
    )
    parser.add_argument(
        "--commit",
        default=None,
        help="override the baseline commit (default: verified_commit in the yaml)",
    )
    parser.add_argument(
        "--only-stale", action="store_true", help="only print entries that need review"
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument(
        "--update",
        action="store_true",
        help="if nothing needs review, bump verified_commit to HEAD",
    )
    args = parser.parse_args()

    root = repo_root()
    yaml_path = root / args.yaml
    data = yaml.safe_load(yaml_path.read_text())

    baseline_commit = args.commit or data.get("verified_commit")
    if not baseline_commit:
        print(
            "error: no verified_commit in the yaml and no --commit given",
            file=sys.stderr,
        )
        sys.exit(2)

    checker = Checker(root, baseline_commit)

    rows = []
    for label, code_ref, tests, entry_commit in iter_entries(data):
        this_checker = (
            checker
            if not entry_commit or entry_commit == baseline_commit
            else Checker(root, entry_commit)
        )

        code_results = (
            this_checker.check_ref(f"{label} [code]", code_ref) if code_ref else []
        )
        test_results = []
        for t in tests:
            test_results.extend(this_checker.check_ref(f"{label} [test]", t))

        all_results = code_results + test_results
        stale = [r for r in all_results if r.status in NEEDS_REVIEW]
        rows.append(
            dict(
                label=label,
                baseline=this_checker.baseline_commit,
                code_results=code_results,
                test_results=test_results,
                needs_review=bool(stale),
            )
        )

    any_stale = any(r["needs_review"] for r in rows)

    if args.json:

        def serialize(r: CheckResult):
            return dict(path=r.path, symbol=r.symbol, status=r.status, detail=r.detail)

        out = [
            dict(
                label=r["label"],
                baseline=r["baseline"],
                needs_review=r["needs_review"],
                code=[serialize(c) for c in r["code_results"]],
                tests=[serialize(t) for t in r["test_results"]],
            )
            for r in rows
            if r["needs_review"] or not args.only_stale
        ]
        print(json.dumps(out, indent=2))
    else:
        console = Console()
        table = Table(
            title=f"Permissions matrix staleness check (baseline {baseline_commit[:12]})"
        )
        table.add_column("Entry", overflow="fold", max_width=45)
        table.add_column("Status")
        table.add_column("Detail", overflow="fold", max_width=60)

        shown = 0
        for r in rows:
            if args.only_stale and not r["needs_review"]:
                continue
            for res in r["code_results"] + r["test_results"]:
                if args.only_stale and res.status not in NEEDS_REVIEW:
                    continue
                color = {
                    "unchanged": "green",
                    "changed": "red",
                    "missing": "red",
                    "unresolved": "yellow",
                    "new-file": "yellow",
                    "deleted-file": "red",
                }.get(res.status, "white")
                table.add_row(
                    res.label,
                    f"[{color}]{res.status}[/{color}]",
                    res.detail or (res.symbol or ""),
                )
                shown += 1

        console.print(table)
        console.print(
            f"\n{shown} checks shown, "
            f"{sum(1 for r in rows if r['needs_review'])} of {len(rows)} entries need review."
        )

    if args.update:
        if any_stale:
            print(
                "\nnot updating verified_commit: some entries still need review",
                file=sys.stderr,
            )
            sys.exit(1)
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],  # noqa: S607
            capture_output=True,
            text=True,
            cwd=root,
            check=True,
        ).stdout.strip()
        # Surgical text edit, not a full yaml.safe_dump round-trip: this
        # file is hand-maintained with comments, flow-style lists, and a
        # named YAML anchor that a re-serialize would silently destroy.
        raw = yaml_path.read_text()
        new_raw, count = re.subn(
            r"^verified_commit:\s*\S+",
            f"verified_commit: {head}",
            raw,
            count=1,
            flags=re.MULTILINE,
        )
        if count != 1:
            print(
                "\nerror: could not find a top-level 'verified_commit:' line to update — "
                "refusing to guess, edit it by hand",
                file=sys.stderr,
            )
            sys.exit(2)
        yaml_path.write_text(new_raw)
        print(f"\nupdated verified_commit to {head}")
        sys.exit(0)

    sys.exit(1 if any_stale else 0)


if __name__ == "__main__":
    main()
