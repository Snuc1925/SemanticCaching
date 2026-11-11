"""Liệt kê mọi hàm/class/method top-level trong một package Python (để đối chiếu danh mục trong WALKTHROUGH).

    python3 .claude/skills/walkthrough/scripts/inventory.py backend/app [--check docs/WALKTHROUGH.md]

--check: in ra các hàm/class có trong code nhưng CHƯA được nhắc trong file tài liệu.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re


def inventory(root: pathlib.Path) -> list[tuple[str, str]]:
    out = []
    for f in sorted(root.rglob("*.py")):
        mod = ".".join(f.relative_to(root).with_suffix("").parts)
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = [a.arg for a in n.args.args] + ([f"*{n.args.vararg.arg}"] if n.args.vararg else []) \
                    + [a.arg for a in n.args.kwonlyargs] + ([f"**{n.args.kwarg.arg}"] if n.args.kwarg else [])
                out.append((mod, f"{n.name}({', '.join(args)})"))
            elif isinstance(n, ast.ClassDef):
                methods = [m.name for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
                out.append((mod, f"class {n.name}" + (f" {{{', '.join(methods)}}}" if methods else "")))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--check")
    a = ap.parse_args()
    items = inventory(pathlib.Path(a.root))
    if not a.check:
        cur = None
        for mod, item in items:
            if mod != cur:
                print(f"\n[{mod}]")
                cur = mod
            print("  ", item)
        return
    doc = pathlib.Path(a.check).read_text(encoding="utf-8")
    missing = []
    for mod, item in items:
        name = re.sub(r"^class ", "", item).split("(")[0].split(" ")[0]
        if not re.search(rf"\b{re.escape(name)}\b", doc):
            missing.append(f"{mod}.{name}")
    print("Chưa được nhắc trong tài liệu:" if missing else "Mọi hàm/class đều đã được nhắc.")
    for m in missing:
        print("  -", m)


if __name__ == "__main__":
    main()
