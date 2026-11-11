"""(Bản chép từ skill walkthrough: ~/.claude/skills/walkthrough/scripts/trace_calls.py — giữ trong repo để `make trace` chạy được trên máy khác.)

Ghi lại MỌI lời gọi hàm Python nằm trong một thư mục mã nguồn khi chạy các kịch bản thật,
xuất thành cây gọi hàm có tham số (in), giá trị trả về (out), thời gian, thread.

Tổng quát, không phụ thuộc project. Phần riêng của project nằm trong FILE KỊCH BẢN (--scenarios):

    # scenarios.py (ví dụ tối thiểu)
    HIDE = {"config._expand"}          # tuỳ chọn: ẩn hàm + cây con (tên dạng module.qualname, tương đối với --src)
    HIDE_PREFIX = ("clients.",)        # tuỳ chọn
    FOLD = {"config.load_yaml"}        # tuỳ chọn: hiện hàm, ẩn cây con
    TRANSPARENT = {"sync.Worker._run"} # tuỳ chọn: hàm chạy mãi (vòng lặp thread) -> con của nó được coi là gốc
    def NOISE(node): return False      # tuỳ chọn: bỏ cây gốc không có thông tin (vd poll không có sự kiện)
    SUMMARIZERS = {"Trace": lambda v: f"Trace(id={v.id})"}   # tuỳ chọn: cách tóm tắt object theo tên class

    def run(trace):                    # BẮT BUỘC
        from app.main import app       # mọi thứ chạy trước lần trace() đầu tiên được ghi vào nhãn "00_startup"
        ...
        trace.off()                    # ngừng ghi (vd khi chuẩn bị dữ liệu, lấy token)
        trace("01_login", "Mô tả", lambda: client.post(...).json(), wait=1.0)

Chạy:
    python trace_calls.py --src backend/app --scenarios scripts/walkthrough/scenarios.py \
        --out docs/walkthrough/raw [--path backend] [--render-only]

--path: thư mục thêm vào sys.path để import được code (mặc định: thư mục cha của --src).
Kết quả: <out>/<nhãn>.md (cây dễ đọc), <out>/<nhãn>.json (dữ liệu thô), <out>/README.md (mục lục).
Giới hạn: chỉ Python (dùng sys.setprofile / threading.setprofile_all_threads, cần Python 3.12+).
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import sys
import threading
import time
from pathlib import Path

SKIP_NAMES = {"<listcomp>", "<dictcomp>", "<setcomp>", "<genexpr>", "<lambda>", "<module>"}
CFG: dict = {"HIDE": set(), "HIDE_PREFIX": (), "FOLD": set(), "TRANSPARENT": set(),
             "NOISE": lambda n: False, "SUMMARIZERS": {}}


# ----------------------------------------------------------------------------- tóm tắt giá trị
def summarize(v, depth: int = 0, width: int = 220) -> str:
    try:
        custom = CFG["SUMMARIZERS"].get(type(v).__name__)
        if custom:
            return custom(v)
        if v is None or isinstance(v, (bool, int)):
            return repr(v)
        if isinstance(v, float):
            return f"{v:.4f}".rstrip("0").rstrip(".") if abs(v) < 1e6 else f"{v:.4g}"
        if isinstance(v, str):
            s = v.replace("\n", "⏎")
            return repr(s if len(s) <= width else s[:width] + f"…(+{len(s) - width} ký tự)")
        if isinstance(v, (bytes, bytearray)):
            return f"<{len(v)} bytes>"
        if depth >= 3:
            return f"<{type(v).__name__}>"
        if isinstance(v, (list, tuple, set, frozenset)):
            seq = list(v)
            if len(seq) > 16 and all(isinstance(x, float) for x in seq[:16]):
                return f"<vector {len(seq)} số: [{', '.join(f'{x:.4f}' for x in seq[:3])}, …]>"
            items = [summarize(x, depth + 1, 120) for x in seq[:6]]
            more = f", …(+{len(seq) - 6})" if len(seq) > 6 else ""
            o, c = ("[", "]") if isinstance(v, list) else ("(", ")") if isinstance(v, tuple) else ("{", "}")
            return o + ", ".join(items) + more + c
        if isinstance(v, dict):
            items = [f"{k!s}: {summarize(x, depth + 1, 120)}" for k, x in list(v.items())[:10]]
            more = f", …(+{len(v) - 10} khoá)" if len(v) > 10 else ""
            return "{" + ", ".join(items) + more + "}"
        if dataclasses.is_dataclass(v) and not isinstance(v, type):
            fs = [f"{f.name}={summarize(getattr(v, f.name), depth + 1, 120)}" for f in dataclasses.fields(v)]
            return f"{type(v).__name__}(" + ", ".join(fs) + ")"
        name = type(v).__name__
        if hasattr(v, "status_code") and hasattr(v, "request"):          # httpx/requests Response
            return f"<HTTP {v.status_code} {getattr(v.request, 'url', '')}>"
        if hasattr(v, "model_dump"):                                      # pydantic
            return f"{name}({summarize(v.model_dump(), depth + 1)})"
        if hasattr(v, "payload") and hasattr(v, "score"):                 # Qdrant ScoredPoint
            return f"ScoredPoint(score={v.score:.4f}, payload={summarize(v.payload, depth + 1)})"
        return f"<{name}>"
    except Exception as e:  # noqa: BLE001
        return f"<không tóm tắt được: {e}>"


# ----------------------------------------------------------------------------- bộ ghi
class Recorder:
    def __init__(self, src_dir: str):
        self.src = src_dir.rstrip("/")
        self.calls: list[dict] = []
        self.stacks: dict[int, list[dict]] = {}
        self.label = "00_startup"
        self.enabled = True
        self.lock = threading.Lock()

    def _name(self, code) -> str | None:
        f = code.co_filename
        if not f.startswith(self.src + "/"):
            return None
        mod = f[len(self.src) + 1:].removesuffix(".py").replace("/", ".")
        return f"{mod}.{code.co_qualname}"

    def profile(self, frame, event, arg):
        if event not in ("call", "return") or not self.enabled:
            return
        code = frame.f_code
        if code.co_name in SKIP_NAMES:
            return
        name = self._name(code)
        if name is None:
            return
        stack = self.stacks.setdefault(threading.get_ident(), [])
        if event == "call":
            n = code.co_argcount + code.co_kwonlyargcount
            names = list(code.co_varnames[:n])
            if code.co_flags & 0x04:
                names.append(code.co_varnames[n]); n += 1
            if code.co_flags & 0x08:
                names.append(code.co_varnames[n])
            loc = frame.f_locals
            args = {a: summarize(loc.get(a)) for a in names if a not in ("self", "cls")}
            node = {"name": name, "line": code.co_firstlineno, "args": args, "children": [],
                    "t0": time.perf_counter(), "thread": threading.current_thread().name, "label": self.label,
                    "frame": id(frame), "parent": stack[-1]["id"] if stack else None}
            with self.lock:
                node["id"] = len(self.calls)
                self.calls.append(node)
            if stack:
                stack[-1]["children"].append(node["id"])
            stack.append(node)
        else:
            if not stack or stack[-1]["frame"] != id(frame):
                return
            node = stack.pop()
            node["ms"] = round((time.perf_counter() - node["t0"]) * 1000, 1)
            node["result"] = summarize(arg)

    def install(self):
        sys.setprofile(self.profile)
        threading.setprofile_all_threads(self.profile)

    def uninstall(self):
        sys.setprofile(None)
        threading.setprofile_all_threads(None)


class Tracer:
    """Đối tượng truyền vào run(trace) của file kịch bản."""

    def __init__(self, rec: Recorder):
        self.rec = rec
        self.scenarios: list[tuple[str, str]] = [("00_startup", "Khởi động / import")]

    def __call__(self, label: str, title: str, fn, wait: float = 0.0):
        self.rec.label = label
        self.rec.enabled = True
        try:
            return fn()
        finally:
            if wait:
                time.sleep(wait)          # chờ tác vụ nền (background task, thread) chạy xong
            self.rec.enabled = False
            self.scenarios.append((label, title))

    def off(self):
        self.rec.enabled = False

    def untraced(self, fn):
        was = self.rec.enabled
        self.rec.enabled = False
        try:
            return fn()
        finally:
            self.rec.enabled = was


# ----------------------------------------------------------------------------- xuất
def hidden(name: str) -> bool:
    return name in CFG["HIDE"] or name.startswith(tuple(CFG["HIDE_PREFIX"]))


def render_calls(calls: list[dict], label: str) -> str:
    by_id = {c["id"]: c for c in calls}
    roots = []
    for c in calls:
        if c["label"] != label or hidden(c["name"]) or c["name"] in CFG["TRANSPARENT"]:
            continue
        p = by_id.get(c["parent"]) if c["parent"] is not None else None
        if (p is None or p["name"] in CFG["TRANSPARENT"]) and not CFG["NOISE"](c):
            roots.append(c)
    lines: list[str] = []

    def walk(n: dict, d: int):
        ind = "│  " * d
        lines.append(f"{ind}▶ {n['name']}   [{n.get('ms', '?')} ms]   (thread: {n['thread']}, dòng {n['line']})")
        for k, v in n["args"].items():
            lines.append(f"{ind}│    in  {k} = {v}")
        if n["name"] not in CFG["FOLD"]:
            for cid in n["children"]:
                ch = by_id.get(cid)
                if ch is not None and not hidden(ch["name"]):
                    walk(ch, d + 1)
        lines.append(f"{ind}│    out = {n.get('result', '(chưa return)')}")

    for r in roots:
        walk(r, 0)
        lines.append("")
    return "\n".join(lines)


def write_outputs(calls: list[dict], scenarios: list[tuple[str, str]], out: Path) -> None:
    index = ["# Bản ghi lời gọi hàm (tự sinh bởi trace_calls.py)\n",
             f"Thời điểm: {time.strftime('%Y-%m-%d %H:%M:%S')}. `▶` = vào hàm, `in` = tham số, "
             "`out` = giá trị trả về, thụt lề = hàm con. Hàm tiện ích có thể đã bị ẩn (HIDE/FOLD).\n"]
    for label, title in scenarios:
        mine = [c for c in calls if c["label"] == label]
        clean = [{k: v for k, v in c.items() if k not in ("t0", "frame")} for c in mine]
        (out / f"{label}.json").write_text(json.dumps({"title": title, "calls": clean}, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
        (out / f"{label}.md").write_text(
            f"# {label}: {title}\n\n{len(mine)} lời gọi hàm.\n\n```text\n{render_calls(clean, label)}\n```\n",
            encoding="utf-8")
        index.append(f"- [{label}]({label}.md): {title} ({len(mine)} lời gọi)")
    (out / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print("\n".join(index))


def load_scenarios(path: Path):
    spec = importlib.util.spec_from_file_location("walkthrough_scenarios", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for k in CFG:
        if hasattr(mod, k):
            CFG[k] = getattr(mod, k)
    if not hasattr(mod, "run"):
        raise SystemExit(f"{path} thiếu hàm run(trace)")
    return mod


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", required=True, help="thư mục mã nguồn cần ghi (vd backend/app)")
    ap.add_argument("--scenarios", required=True, help="file Python định nghĩa run(trace)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--path", action="append", default=[], help="thêm vào sys.path (mặc định: cha của --src)")
    ap.add_argument("--render-only", action="store_true", help="chỉ dựng lại .md từ .json đã có")
    a = ap.parse_args()
    src = Path(a.src).resolve()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for p in (a.path or [str(src.parent)]):
        sys.path.insert(0, str(Path(p).resolve()))
    mod = load_scenarios(Path(a.scenarios).resolve())

    if a.render_only:
        scen, calls = [], []
        for jf in sorted(out.glob("*.json")):
            d = json.loads(jf.read_text(encoding="utf-8"))
            scen.append((jf.stem, d["title"]))
            calls += d["calls"]
        write_outputs(calls, scen, out)
        return

    rec = Recorder(str(src))
    tracer = Tracer(rec)
    rec.install()
    try:
        mod.run(tracer)
    finally:
        rec.uninstall()
    write_outputs(rec.calls, tracer.scenarios, out)


if __name__ == "__main__":
    main()
