from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import re
from typing import Iterable

FLOAT_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?$")

@dataclass(frozen=True)
class Segment:
    x1: float
    y1: float
    x2: float
    y2: float
    raw_line_no: int
    layer: str = ""
    color: str = ""
    linetype: str = ""

    @property
    def length(self) -> float:
        return math.hypot(self.x2 - self.x1, self.y2 - self.y1)

    def endpoints(self) -> tuple[tuple[float, float], tuple[float, float]]:
        return (self.x1, self.y1), (self.x2, self.y2)

@dataclass
class ParseResult:
    center_segments: list[Segment]
    all_segments: list[Segment]
    messages: list[str]


def _is_four_float_line(line: str) -> bool:
    parts = line.strip().split()
    return len(parts) == 4 and all(FLOAT_RE.match(p) for p in parts)


def _to_segment(line: str, line_no: int, layer: str, color: str, linetype: str) -> Segment:
    x1, y1, x2, y2 = map(float, line.strip().split())
    return Segment(x1, y1, x2, y2, line_no, layer, color, linetype)


def parse_jwc_temp(path: str | Path) -> ParseResult:
    """Parse Jw_cad external-transform temp text.

    First target rule for NEVIS PipeTool:
    - centerline = numeric 4-float lines where current state is lyb/lc6/lt5.
    - if not found, fallback to all lt5 numeric lines.
    """
    p = Path(path)
    raw = p.read_bytes()

    # JWW external temp is usually CP932. Accept UTF-8 too for edited samples.
    for enc in ("cp932", "utf-8-sig", "utf-8"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("cp932", errors="ignore")

    layer = color = linetype = ""
    all_segments: list[Segment] = []
    center_segments: list[Segment] = []
    lt5_segments: list[Segment] = []

    for i, original in enumerate(text.splitlines(), start=1):
        line = original.strip()
        if not line:
            continue

        low = line.lower()
        if re.fullmatch(r"ly[0-9a-f]", low):
            layer = low
            continue
        if re.fullmatch(r"lc\d+", low):
            color = low
            continue
        if re.fullmatch(r"lt\d+", low):
            linetype = low
            continue

        if _is_four_float_line(line):
            seg = _to_segment(line, i, layer, color, linetype)
            if seg.length <= 1e-9:
                continue
            all_segments.append(seg)
            if linetype == "lt5":
                lt5_segments.append(seg)
            if layer == "lyb" and color == "lc6" and linetype == "lt5":
                center_segments.append(seg)

    messages: list[str] = []
    if not center_segments and lt5_segments:
        center_segments = lt5_segments
        messages.append("Không thấy đúng nhóm lyb/lc6/lt5, đã fallback lấy toàn bộ lt5.")
    if not center_segments:
        messages.append("Không tìm thấy tim ống. Hãy kiểm tra layer/màu/kiểu nét tim ống trong JWW.")
    else:
        messages.append(f"Đã đọc {len(center_segments)} đoạn tim ống.")

    return ParseResult(center_segments=center_segments, all_segments=all_segments, messages=messages)
