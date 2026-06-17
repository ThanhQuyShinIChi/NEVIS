# -*- coding: utf-8 -*-
"""
NEVIS JSON Library Editor FINAL
- TXT -> standalone JSON converter/editor for NEVIS MEP fitting libraries.
- New TXT rule:
    lt49 = centerline / pipe axis
    lt1  = solid outline / fitting body
    ci   = circle/arc, belongs to current line type
- Fitting center is the intersection/common point of lt49 centerlines.
- JSON is independent; after conversion NEVIS can use JSON only.

Run:
    py Nevis_JSON_Library_Editor_FINAL.py
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import sys
import hashlib
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QEvent
    from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QAction, QKeySequence, QPainterPath, QPolygonF
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox, QHBoxLayout,
        QVBoxLayout, QGridLayout, QSplitter, QListWidget, QListWidgetItem, QLabel,
        QLineEdit, QPushButton, QComboBox, QCheckBox, QGroupBox, QTableWidget,
        QTableWidgetItem, QHeaderView, QGraphicsView, QGraphicsScene, QDoubleSpinBox,
        QSpinBox, QTextEdit, QSizePolicy, QFrame, QRadioButton, QButtonGroup, QTreeWidget, QTreeWidgetItem
    )
except Exception:
    print("PySide6 is required. Install with: py -m pip install pyside6")
    raise

NUM = r"-?\d+(?:\.\d+)?"
LINE_RE = re.compile(rf"^\s*({NUM})\s+({NUM})\s+({NUM})\s+({NUM})(?:\s.*)?$")
CI_RE = re.compile(rf"^\s*ci\s+({NUM})\s+({NUM})\s+({NUM})(.*)$", re.IGNORECASE)
LT_RE = re.compile(r"^\s*lt\s*(\d+)\s*$", re.IGNORECASE)
LC_RE = re.compile(r"^\s*lc\s*(\d+)\s*$", re.IGNORECASE)
LY_RE = re.compile(r"^\s*ly\s*(\S+)\s*$", re.IGNORECASE)

CENTER_LT = "49"
SOLID_LT = "1"


def read_text(path: Path) -> str:
    for enc in ("cp932", "utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            pass
    return path.read_text(encoding="cp932", errors="ignore")


def fmt(v: float) -> str:
    if abs(v) < 1e-9:
        v = 0.0
    s = f"{v:.9f}".rstrip("0").rstrip(".")
    return s or "0"


def dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def norm_vec(x: float, y: float) -> Tuple[float, float]:
    l = math.hypot(x, y)
    if l < 1e-9:
        return 0.0, 0.0
    return x / l, y / l


def angle_deg(v: Tuple[float, float]) -> float:
    return (math.degrees(math.atan2(v[1], v[0])) + 360.0) % 360.0


def line_intersection_inf(a1, a2, b1, b2) -> Optional[Tuple[float, float]]:
    x1, y1 = a1; x2, y2 = a2; x3, y3 = b1; x4, y4 = b2
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(den) < 1e-9:
        return None
    px = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / den
    py = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / den
    return px, py


def closest_point_on_segment(p, a, b):
    px, py = p; ax, ay = a; bx, by = b
    dx, dy = bx-ax, by-ay
    l2 = dx*dx + dy*dy
    if l2 < 1e-12:
        return a
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy) / l2))
    return ax + t*dx, ay + t*dy


@dataclass
class Segment:
    x1: float; y1: float; x2: float; y2: float
    lt: str = SOLID_LT
    lc: str = ""
    ly: str = ""
    raw: str = ""
    index: int = -1

    @property
    def p1(self): return (self.x1, self.y1)
    @property
    def p2(self): return (self.x2, self.y2)
    @property
    def length(self): return math.hypot(self.x2-self.x1, self.y2-self.y1)


@dataclass
class CircleArc:
    cx: float; cy: float; r: float
    rest: str = ""
    lt: str = SOLID_LT
    lc: str = ""
    ly: str = ""
    raw: str = ""
    index: int = -1


@dataclass
class Geometry:
    raw_lines: List[str] = field(default_factory=list)
    segments: List[Segment] = field(default_factory=list)
    circles: List[CircleArc] = field(default_factory=list)

    @property
    def centerlines(self) -> List[Segment]:
        return [s for s in self.segments if s.lt == CENTER_LT]

    @property
    def outlines(self) -> List[Segment]:
        return [s for s in self.segments if s.lt != CENTER_LT]


@dataclass
class Port:
    id: str
    role: str = "auto"
    center: Tuple[float, float] = (0.0, 0.0)      # port end on centerline, far from fitting center
    direction: Tuple[float, float] = (1.0, 0.0)  # from fitting center to port
    angle: float = 0.0
    centerline: Tuple[Tuple[float, float], Tuple[float, float]] = ((0.0,0.0),(0.0,0.0))
    cut_point: Optional[Tuple[float, float]] = None
    source: str = "lt49"
    confidence: float = 1.0


def parse_txt(path: Path) -> Geometry:
    lines = read_text(path).splitlines()
    geo = Geometry(raw_lines=lines[:])
    cur_lt = ""
    cur_lc = ""
    cur_ly = ""
    for i, line in enumerate(lines):
        m = LT_RE.match(line)
        if m:
            cur_lt = m.group(1)
            continue
        m = LC_RE.match(line)
        if m:
            cur_lc = m.group(1)
            continue
        m = LY_RE.match(line)
        if m:
            cur_ly = m.group(1)
            continue
        m = LINE_RE.match(line)
        if m:
            geo.segments.append(Segment(
                float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)),
                lt=cur_lt or SOLID_LT, lc=cur_lc, ly=cur_ly, raw=line, index=i
            ))
            continue
        m = CI_RE.match(line)
        if m:
            geo.circles.append(CircleArc(float(m.group(1)), float(m.group(2)), float(m.group(3)),
                                         rest=m.group(4) or "", lt=cur_lt or SOLID_LT,
                                         lc=cur_lc, ly=cur_ly, raw=line, index=i))
    return geo




def geometry_from_json_data(data: Dict[str, Any]) -> Geometry:
    """Build Geometry directly from standalone NEVIS JSON, without temporary TXT files.

    Priority:
    1) geometry.raw_lines: parse exactly like original TXT, preserving lt49/lt1/ci state.
    2) geometry.entities: rebuild objects directly if raw_lines is absent.

    This keeps JSON independent and Windows-safe; no /tmp/nevis_raw_tmp.txt is used.
    """
    geo_block = data.get("geometry", {}) if isinstance(data, dict) else {}
    raw = geo_block.get("raw_lines", []) if isinstance(geo_block, dict) else []
    if isinstance(raw, list) and raw:
        # Parse from in-memory text by reusing the same state machine as parse_txt.
        lines = [str(x) for x in raw]
        geo = Geometry(raw_lines=lines[:])
        cur_lt = ""
        cur_lc = ""
        cur_ly = ""
        for i, line in enumerate(lines):
            m = LT_RE.match(line)
            if m:
                cur_lt = m.group(1); continue
            m = LC_RE.match(line)
            if m:
                cur_lc = m.group(1); continue
            m = LY_RE.match(line)
            if m:
                cur_ly = m.group(1); continue
            m = LINE_RE.match(line)
            if m:
                geo.segments.append(Segment(
                    float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)),
                    lt=cur_lt or SOLID_LT, lc=cur_lc, ly=cur_ly, raw=line, index=i
                ))
                continue
            m = CI_RE.match(line)
            if m:
                geo.circles.append(CircleArc(float(m.group(1)), float(m.group(2)), float(m.group(3)),
                                             rest=m.group(4) or "", lt=cur_lt or SOLID_LT,
                                             lc=cur_lc, ly=cur_ly, raw=line, index=i))
        return geo

    # Fallback: direct entity reconstruction for future/compact JSON files.
    entities = geo_block.get("entities", {}) if isinstance(geo_block, dict) else {}
    geo = Geometry(raw_lines=[])

    def add_seg_from_dict(d: Dict[str, Any], default_lt: str):
        try:
            seg = Segment(
                float(d.get("x1", 0.0)), float(d.get("y1", 0.0)),
                float(d.get("x2", 0.0)), float(d.get("y2", 0.0)),
                lt=str(d.get("lt", default_lt)), lc=str(d.get("lc", "")), ly=str(d.get("ly", "")),
                raw=str(d.get("raw", "")), index=int(d.get("index", -1))
            )
            geo.segments.append(seg)
        except Exception:
            pass

    for d in entities.get("centerlines", []) or []:
        if isinstance(d, dict): add_seg_from_dict(d, CENTER_LT)
    for d in entities.get("outlines", []) or []:
        if isinstance(d, dict): add_seg_from_dict(d, SOLID_LT)
    for d in entities.get("segments", []) or []:
        if isinstance(d, dict): add_seg_from_dict(d, str(d.get("lt", SOLID_LT)))

    for d in entities.get("circles", []) or []:
        if not isinstance(d, dict):
            continue
        try:
            geo.circles.append(CircleArc(
                float(d.get("cx", 0.0)), float(d.get("cy", 0.0)), float(d.get("r", 0.0)),
                rest=str(d.get("rest", "")), lt=str(d.get("lt", SOLID_LT)),
                lc=str(d.get("lc", "")), ly=str(d.get("ly", "")),
                raw=str(d.get("raw", "")), index=int(d.get("index", -1))
            ))
        except Exception:
            pass
    return geo


def arc_preview_points(c: CircleArc, steps: int = 64) -> List[Tuple[float, float]]:
    """AHK/JWW-compatible preview points for `ci` records.

    The old editor shortened every arc to the nearest <=180° span.  That is not
    how the proven AHK preview works.  AHK reads every numeric token, treats
    `ci x y r` as a full circle, treats `ci x y r a1 a2 ... rot` as an arc,
    adds the 7th numeric token as rotation, then only normalizes with
    `while a2 < a1: a2 += 360`.  This keeps long arcs and wrap-around arcs
    exactly like the JWW/TXT libraries.
    """
    nums = [float(x) for x in re.findall(NUM, c.rest or "")]
    r = abs(c.r)
    if len(nums) < 2:
        n = max(96, steps)
        return [(c.cx + r*math.cos(2*math.pi*i/n), c.cy + r*math.sin(2*math.pi*i/n)) for i in range(n+1)]

    a1 = nums[0]
    a2 = nums[1]
    # For a full ci line the numeric tokens are: cx, cy, r, a1, a2, flag, rot.
    # Because c.rest starts after r, the rotation is nums[3] when present.
    rot = nums[3] if len(nums) >= 4 else 0.0
    a1 += rot
    a2 += rot
    while a2 < a1:
        a2 += 360.0
    if abs(a2 - a1) < 0.001:
        a2 = a1 + 360.0

    span = a2 - a1
    n = max(12, int(math.ceil(abs(span) / 2.0)))
    # Keep a reasonable cap for huge/full arcs while preserving shape.
    n = min(max(n, 12), 360)
    return [
        (c.cx + r*math.cos(math.radians(a1 + span*i/n)),
         c.cy + r*math.sin(math.radians(a1 + span*i/n)))
        for i in range(n+1)
    ]


def infer_center(centerlines: List[Segment]) -> Tuple[Tuple[float, float], str, float]:
    cls = [s for s in centerlines if s.length > 1e-6]
    if not cls:
        return (0.0, 0.0), "no_lt49_default_00", 0.0

    # Most new files draw each lt49 from 0,0 to port. Prefer a repeated endpoint.
    pts: List[Tuple[float, float]] = []
    for s in cls:
        pts += [s.p1, s.p2]
    groups: List[List[Tuple[float, float]]] = []
    tol = 0.02
    for p in pts:
        placed = False
        for g in groups:
            if dist(p, g[0]) <= tol:
                g.append(p); placed = True; break
        if not placed:
            groups.append([p])
    groups.sort(key=len, reverse=True)
    if groups and len(groups[0]) >= 2:
        x = sum(p[0] for p in groups[0]) / len(groups[0])
        y = sum(p[1] for p in groups[0]) / len(groups[0])
        confidence = min(1.0, 0.65 + 0.12 * len(groups[0]))
        return (x, y), "lt49_common_endpoint", confidence

    # If no repeated endpoint, use intersection of infinite centerlines.
    inters = []
    for i, a in enumerate(cls):
        for b in cls[i+1:]:
            p = line_intersection_inf(a.p1, a.p2, b.p1, b.p2)
            if p is not None and all(abs(v) < 1e7 for v in p):
                inters.append(p)
    if inters:
        x = sum(p[0] for p in inters) / len(inters)
        y = sum(p[1] for p in inters) / len(inters)
        spread = max(dist((x, y), p) for p in inters) if len(inters) > 1 else 0.0
        confidence = max(0.3, min(0.95, 0.95 - spread / 20.0))
        return (x, y), "lt49_intersection", confidence

    # One centerline only: use endpoint closest to 0,0 if it exists; otherwise shortest-distance endpoint.
    s = cls[0]
    p = s.p1 if dist(s.p1, (0,0)) <= dist(s.p2, (0,0)) else s.p2
    conf = 0.75 if dist(p, (0,0)) < 0.05 else 0.45
    return p, "single_lt49_inner_endpoint", conf


def _point_on_segment_tol(p: Tuple[float, float], s: Segment, tol: float = 0.03) -> bool:
    return dist(closest_point_on_segment(p, s.p1, s.p2), p) <= tol


def _add_port_candidate(cands: List[Port], center: Tuple[float, float], far: Tuple[float, float],
                        near: Tuple[float, float], source_line: Segment, confidence: float = 1.0):
    dx, dy = far[0] - center[0], far[1] - center[1]
    ux, uy = norm_vec(dx, dy)
    if abs(ux) < 1e-9 and abs(uy) < 1e-9:
        return
    ang = angle_deg((ux, uy))
    # Avoid duplicate rays from overlapping lt49 pieces. Same direction within 4 degrees => keep farther one.
    for old in cands:
        da = abs((old.angle - ang + 180.0) % 360.0 - 180.0)
        if da <= 4.0:
            if dist(center, far) > dist(center, old.center):
                old.center = far
                old.direction = (ux, uy)
                old.angle = ang
                old.centerline = (near, far)
                old.confidence = max(old.confidence, confidence)
            return
    cands.append(Port(
        id=f"P{len(cands)+1}", center=far, direction=(ux, uy), angle=ang,
        centerline=(near, far), confidence=confidence
    ))


def _angle_diff_180(a: float, b: float) -> float:
    d = abs((a - b + 180.0) % 360.0 - 180.0)
    return abs(180.0 - d)


def normalize_port_order_and_roles(ports: List[Port], desired_count: int) -> List[Port]:
    """NEVIS convention:
    - 1 port: P1 = single
    - 2 ports: P1/P2 = main line
    - 3 ports: P1/P2 = main line (the most opposite pair), P3 = branch

    This makes later NEVIS placement easier: branch is always P3 for DT/T/Y style fittings.
    """
    ports = ports[:max(1, min(3, desired_count))]
    if not ports:
        return ports
    if len(ports) == 1:
        ports[0].id = "P1"; ports[0].role = "single"
        return ports
    if len(ports) == 2:
        # stable order: from left/up to right/down by angle, both are main
        ports = sorted(ports, key=lambda p: p.angle)
        for i, p in enumerate(ports, 1):
            p.id = f"P{i}"; p.role = "main"
        return ports
    # len >= 3: choose the most collinear/opposite pair as the main route.
    best = None
    for i in range(3):
        for j in range(i+1, 3):
            score = _angle_diff_180(ports[i].angle, ports[j].angle)
            if best is None or score < best[0]:
                best = (score, i, j)
    _, i, j = best
    main = [ports[i], ports[j]]
    branch = [ports[k] for k in range(3) if k not in (i, j)][0]
    main = sorted(main, key=lambda p: p.angle)
    ordered = [main[0], main[1], branch]
    ordered[0].id = "P1"; ordered[0].role = "main_1"
    ordered[1].id = "P2"; ordered[1].role = "main_2"
    ordered[2].id = "P3"; ordered[2].role = "branch"
    return ordered


def infer_ports(geo: Geometry, center: Tuple[float, float], port_count: Optional[int] = None) -> List[Port]:
    """Infer ports from lt49 rays.

    Important for DT/SV style fittings: one lt49 segment can pass THROUGH the
    fitting center, so it represents two opposite ports.  If the center is on
    the segment and both endpoints are away from center, split it into 2 ports.
    If one endpoint is the center/common point, it represents 1 port.
    """
    cls = [s for s in geo.centerlines if s.length > 1e-6]
    ports: List[Port] = []
    center_eps = 0.05
    for s in cls:
        d1 = dist(s.p1, center)
        d2 = dist(s.p2, center)
        center_on_seg = _point_on_segment_tol(center, s, tol=0.08)
        if center_on_seg and d1 > center_eps and d2 > center_eps:
            _add_port_candidate(ports, center, s.p1, center, s, confidence=0.98)
            _add_port_candidate(ports, center, s.p2, center, s, confidence=0.98)
        else:
            far = s.p1 if d1 >= d2 else s.p2
            near = s.p2 if d1 >= d2 else s.p1
            _add_port_candidate(ports, center, far, near, s, confidence=1.0 if min(d1,d2) <= center_eps else 0.75)
    ports.sort(key=lambda p: p.angle)
    if port_count is None:
        port_count = min(3, len(ports)) if ports else 1
    return normalize_port_order_and_roles(ports, port_count)


def detect_port_count(geo: Geometry) -> Tuple[int, str, float]:
    center, center_source, center_conf = infer_center(geo.centerlines)
    ports = infer_ports(geo, center, None)
    n = len(ports)
    if 1 <= n <= 3:
        src = "auto_lt49_rays"
        conf = min(1.0, max(0.6, center_conf))
        return n, src, conf
    if n == 0:
        return 1, "default_no_lt49", 0.0
    return 3, "auto_lt49_rays_over_3_need_review", 0.45


def default_flow_port(ports: List[Port], flow_model: str = "directional") -> Optional[str]:
    if flow_model == "collector" or not ports:
        return None
    # Drainage fittings normally flow downward in the library editor.
    # Pick the port whose direction is closest to screen/model downward (0,-1).
    target = (0.0, -1.0)
    best = max(ports, key=lambda p: p.direction[0]*target[0] + p.direction[1]*target[1])
    return best.id



def point_on_outline_for_port(geo: Geometry, center: Tuple[float,float], port: Port) -> Optional[Tuple[float,float]]:
    """Find the real pipe-mouth point for a port.

    NEVIS convention: a port point is not merely the far endpoint of an lt49
    centerline.  It is the intersection between that pipe centerline ray and
    the OUTERMOST fitting edge in that direction.  This point is used later as
    the pipe cut/trim boundary.
    """
    ux, uy = port.direction
    ray_end = (center[0] + ux*100000.0, center[1] + uy*100000.0)
    candidates = []
    for s in geo.outlines:
        p = line_intersection_inf(center, ray_end, s.p1, s.p2)
        if p is None:
            continue
        # must lie on the finite outline segment
        if dist(closest_point_on_segment(p, s.p1, s.p2), p) > 0.03:
            continue
        t = (p[0]-center[0])*ux + (p[1]-center[1])*uy
        if t > 0.01:
            candidates.append((t, p))
    if candidates:
        # IMPORTANT: choose the farthest edge from the fitting center, not the
        # nearest internal body line.  The farthest one is the pipe contact mouth.
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]
    return None



def assign_roles_to_json_ports(data: Dict[str, Any]) -> None:
    pc = int(data.get("port_count", len(data.get("ports", [])) or 1))
    roles = ["single"] if pc == 1 else (["main_1", "main_2"] if pc == 2 else ["main_1", "main_2", "branch"])
    ports = data.setdefault("ports", [])
    for i, p in enumerate(ports[:pc]):
        p["id"] = f"P{i+1}"
        if i < len(roles):
            p["role"] = roles[i]


def port_convention_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate NEVIS 3-port convention: P1-P2 = main route, P3 = branch.

    Returns a small status dictionary saved into JSON and used for preview warnings.
    """
    ports = {p.get("id"): p for p in data.get("ports", []) if isinstance(p, dict)}
    pc = int(data.get("port_count", len(ports) or 1))
    if pc != 3 or not all(k in ports for k in ("P1", "P2", "P3")):
        return {"rule": "P1-P2 main, P3 branch", "ok": True, "note": "not_3_port"}
    d1 = ports["P1"].get("direction", [0, 0])
    d2 = ports["P2"].get("direction", [0, 0])
    d3 = ports["P3"].get("direction", [0, 0])
    a1, a2, a3 = angle_deg((float(d1[0]), float(d1[1]))), angle_deg((float(d2[0]), float(d2[1]))), angle_deg((float(d3[0]), float(d3[1])))
    main_opposite_error = _angle_diff_180(a1, a2)
    # branch angle against the undirected main axis, nearest to 45/90/135 is acceptable.
    rel = abs((a3 - a1 + 180.0) % 360.0 - 180.0)
    if rel > 90.0:
        rel = 180.0 - rel
    allowed = [45.0, 90.0, 135.0]
    branch_error = min(abs(rel - x) for x in allowed)
    ok = main_opposite_error <= 8.0 and branch_error <= 12.0
    return {
        "rule": "P1-P2 main, P3 branch",
        "ok": bool(ok),
        "main_opposite_error_deg": round(main_opposite_error, 3),
        "branch_angle_to_main_deg": round(rel, 3),
        "branch_angle_error_deg": round(branch_error, 3),
        "note": "P1-P2 must be collinear/opposite; P3 must be branch at about 45/90/135 deg"
    }


def name_rule_from_name(stem: str) -> Dict[str, Any]:
    """Infer expected fitting geometry from the file name.

    This is not a replacement for lt49 geometry.  It is a contract/QA rule:
    the filename says what the fitting SHOULD be, then lt49/ports prove whether
    the library actually matches it.
    """
    raw = stem.strip()
    s = raw.upper().replace("°", "").replace("＿", "_").replace("-", "_")
    first = re.split(r"[_\s]+", s)[0] if s else ""
    # Prefer the leading token because the user's library naming convention is
    # type_size_size, for example DT_65_50 or 45_40_40.
    ftype = first
    expected: Dict[str, Any] = {
        "source": "filename_prefix",
        "raw_prefix": first,
        "detected_type": "",
        "expected_port_count": None,
        "main_ports": [],
        "branch_port": None,
        "expected_main_angle_deg": None,
        "expected_branch_angles_deg": [],
        "expected_two_port_angles_deg": [],
        "flow_model_hint": "directional",
        "description": ""
    }

    def set_rule(t, count, desc, two=None, main=None, branch=None, collector=False):
        expected["detected_type"] = t
        expected["expected_port_count"] = count
        expected["description"] = desc
        if two is not None:
            expected["expected_two_port_angles_deg"] = list(two)
        if main is not None:
            expected["expected_main_angle_deg"] = main
        if branch is not None:
            expected["expected_branch_angles_deg"] = list(branch)
        if count == 3:
            expected["main_ports"] = ["P1", "P2"]
            expected["branch_port"] = "P3"
        elif count == 2:
            expected["main_ports"] = ["P1", "P2"]
        elif count == 1:
            expected["main_ports"] = ["P1"]
        if collector:
            expected["flow_model_hint"] = "collector"

    if ftype in ("LL", "DL", "90", "L", "L90"):
        set_rule(ftype, 2, "2 cửa vuông góc", two=[90])
    elif ftype in ("45", "45D", "L45"):
        set_rule("45°", 2, "2 cửa góc 135° theo hướng dòng chảy / 45° theo góc đổi hướng", two=[135, 45])
    elif ftype in ("4", "4D"):
        set_rule(ftype, 2, "2 cửa góc 45°", two=[45])
    elif ftype in ("IN", "INH", "DS"):
        set_rule(ftype, 2, "2 cửa thẳng hàng 180°", two=[180])
    elif ftype in ("DT", "T", "LT"):
        set_rule(ftype, 3, "3 cửa vuông góc: P1-P2 là tuyến chính, P3 là nhánh phụ", main=180, branch=[90])
    elif ftype in ("Y", "TY"):
        set_rule(ftype, 3, "3 cửa chạc Y: P1-P2 là tuyến chính, P3 là nhánh phụ chéo", main=180, branch=[45, 135])
    elif ftype in ("S", "SV", "集合管"):
        # S/SV can be 1/2/3 cửa depending on the specific library, so lt49 is
        # still allowed to decide the port count.  The important part is flow_model.
        set_rule(ftype, None, "Collector/S: nước hoặc nguồn tập trung về thân S; số cửa theo lt49 hoặc lựa chọn tay", collector=True)
    else:
        expected["description"] = "Không có quy tắc tên rõ ràng; dùng lt49/thiết lập tay để nhận diện"
    return expected


def _angle_between_dirs(d1: Any, d2: Any) -> float:
    try:
        a1 = angle_deg((float(d1[0]), float(d1[1])))
        a2 = angle_deg((float(d2[0]), float(d2[1])))
    except Exception:
        return 999.0
    diff = abs((a2 - a1 + 180.0) % 360.0 - 180.0)
    return diff


def name_rule_status(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate ports against filename-derived expectation."""
    rule = data.get("name_rule") if isinstance(data.get("name_rule"), dict) else name_rule_from_name(str(data.get("name", "")))
    ports = {p.get("id"): p for p in data.get("ports", []) if isinstance(p, dict)}
    pc = int(data.get("port_count", len(ports) or 0) or 0)
    warnings: List[str] = []
    ok = True
    exp_count = rule.get("expected_port_count")
    if exp_count in (1, 2, 3) and pc != exp_count:
        ok = False
        warnings.append(f"Tên file dự kiến {exp_count} cửa nhưng JSON đang là {pc} cửa")

    if exp_count == 2 and all(k in ports for k in ("P1", "P2")):
        ang = _angle_between_dirs(ports["P1"].get("direction", [1,0]), ports["P2"].get("direction", [1,0]))
        allowed = [float(x) for x in rule.get("expected_two_port_angles_deg", [])]
        if allowed:
            err = min(abs(ang - a) for a in allowed)
            # For elbow conventions 45 and 135 are often complementary.  The rule
            # stores both where useful, so this tolerance can stay tight enough.
            if err > 12.0:
                ok = False
                warnings.append(f"Góc P1-P2 = {round(ang,1)}°, không khớp quy tắc tên {allowed}")
    elif exp_count == 3 and all(k in ports for k in ("P1", "P2", "P3")):
        main_ang = _angle_between_dirs(ports["P1"].get("direction", [1,0]), ports["P2"].get("direction", [1,0]))
        main_target = rule.get("expected_main_angle_deg")
        if main_target is not None and abs(main_ang - float(main_target)) > 10.0:
            ok = False
            warnings.append(f"P1-P2 phải là tuyến chính {main_target}° nhưng hiện {round(main_ang,1)}°")
        # Branch angle is measured to the nearest main axis direction.
        b1 = _angle_between_dirs(ports["P3"].get("direction", [1,0]), ports["P1"].get("direction", [1,0]))
        b2 = _angle_between_dirs(ports["P3"].get("direction", [1,0]), ports["P2"].get("direction", [1,0]))
        branch_ang = min(b1, b2)
        allowed = [float(x) for x in rule.get("expected_branch_angles_deg", [])]
        if allowed:
            err = min(abs(branch_ang - a) for a in allowed)
            if err > 12.0:
                ok = False
                warnings.append(f"P3 nhánh phụ đang {round(branch_ang,1)}° so với tuyến chính, không khớp {allowed}")

    return {"ok": bool(ok), "rule": rule, "warnings": warnings}

def build_nevis_json(path: Path, geo: Geometry, port_count: Optional[int] = None, manual_port_count: bool = False,
                     flow_model: str = "directional", flow_port: str = "auto") -> Dict[str, Any]:
    detected_count, count_source, count_conf = detect_port_count(geo)
    name_rule = name_rule_from_name(path.stem)
    expected_count = name_rule.get("expected_port_count")
    if not manual_port_count and expected_count in (1, 2, 3):
        port_count = int(expected_count)
        count_source = "filename_rule_then_lt49"
        # Strong filename rule, but not absolute: QA will compare against lt49.
        count_conf = max(count_conf, 0.9)
    elif port_count is None:
        port_count = detected_count
        manual_port_count = False
    if flow_model == "directional" and name_rule.get("flow_model_hint") == "collector":
        flow_model = "collector"
    center, center_source, center_conf = infer_center(geo.centerlines)
    ports = infer_ports(geo, center, port_count)
    for p in ports:
        cp = point_on_outline_for_port(geo, center, p)
        if cp is not None:
            p.cut_point = cp
            # Display/save the port at the true mouth/cut position.
            p.center = cp
            p.centerline = (center, cp)
    material, ftype, size = infer_from_name(path.stem)
    need_review = center_conf < 0.8 or count_conf < 0.9 or len(ports) != port_count
    return {
        "schema": "NEVIS_LIBRARY_JSON_V2",
        "version": 2,
        "name": path.stem,
        "source_txt": path.name,
        "independent_json": True,
        "material": material,
        "type": ftype,
        "size": size,
        "name_rule": name_rule,
        "port_count": int(port_count),
        "port_count_source": "manual" if manual_port_count else count_source,
        "manual_override": bool(manual_port_count),
        "center": [center[0], center[1]],
        "center_source": center_source,
        "center_is_fitting_insert_point": True,
        "center_definition": "intersection/common point of lt49 pipe centerlines",
        "flow": {
            "model": flow_model,
            "port": None if flow_model == "collector" else (flow_port if flow_port != "auto" else default_flow_port(ports, flow_model)),
            "default_direction": [0, -1],
            "default_direction_name": "downward",
            "note": "collector is used for S/集合管; each port direction is still defined by lt49; directional defaults to the downward port."
        },
        "ports": [
            {
                "id": p.id,
                "role": p.role,
                "center": [p.center[0], p.center[1]],
                "direction": [p.direction[0], p.direction[1]],
                "angle_deg": p.angle,
                "centerline": [[p.centerline[0][0], p.centerline[0][1]], [p.centerline[1][0], p.centerline[1][1]]],
                "cut_point": None if p.cut_point is None else [p.cut_point[0], p.cut_point[1]],
                "source": p.source,
                "confidence": p.confidence
            } for p in ports
        ],
        "geometry": {
            "raw_lines": geo.raw_lines[:],
            "entities": {
                "centerlines": [asdict(s) for s in geo.centerlines],
                "outlines": [asdict(s) for s in geo.outlines],
                "circles": [asdict(c) for c in geo.circles]
            },
            "line_type_rule": {"lt49": "centerline", "others": "geometry_outline_or_auxiliary", "note": "Only lt49 is treated as pipe centerline; every other line type is drawable geometry."}
        },
        "port_convention": {
            "rule": "P1-P2 main, P3 branch",
            "main_ports": ["P1", "P2"] if int(port_count) >= 2 else ["P1"],
            "branch_port": "P3" if int(port_count) == 3 else None,
            "description": "For 3-port fittings such as T/DT/Y: P1 and P2 are the straight main route; P3 is the branch, usually 45/90/135 degrees from the main route."
        },
        "filename_rule_note": "Tên file tạo quy tắc kỳ vọng; lt49/port thực tế dùng để kiểm chứng. Nếu không khớp, QA sẽ tô cảnh báo.",
        "auto_detect": {
            "center_confidence": round(center_conf, 4),
            "port_count_confidence": round(count_conf, 4),
            "need_review": bool(need_review)
        }
    }


def infer_from_name(stem: str) -> Tuple[str, str, str]:
    name = stem.replace("°", "").replace("＿", "_")
    parts = [p for p in re.split(r"[_\-\s]+", name) if p]
    known_types = {"45", "45D", "DT", "DL", "LL", "LT", "Y", "T", "S", "SV", "IN", "INH", "GH", "CO", "COS", "ES", "ESS"}
    mat = ""
    ftype = ""
    sizes = []
    for p in parts:
        up = p.upper()
        if up in known_types or p in {"45"}:
            ftype = "45°" if up.startswith("45") else up
        elif re.fullmatch(r"\d+", p):
            sizes.append(p)
        elif re.fullmatch(r"\d+x\d+(?:x\d+)?", p, re.IGNORECASE):
            sizes.append(p.lower().replace("x", "x"))
        else:
            # likely material e.g. TMP/DV/VP
            if not mat and re.search(r"[A-Za-z一-龥ぁ-んァ-ン]", p):
                mat = p
    if not ftype and parts:
        ftype = "45°" if parts[0].startswith("45") else parts[0].upper()
    size = "x".join(sizes) if len(sizes) > 1 else (sizes[0] if sizes else "")
    return mat, ftype, size



def _round_obj_for_signature(obj: Any, ndigits: int = 3) -> Any:
    """Normalize file content for duplicate detection.

    Coordinates are rounded because JWW TXT often contains tiny floating noise.
    File identity fields are intentionally ignored so copied libraries with
    different names can still be detected.
    """
    ignore = {"name", "source_txt", "modified_at", "created_at"}
    if isinstance(obj, float):
        return round(obj, ndigits)
    if isinstance(obj, int) or obj is None or isinstance(obj, str) or isinstance(obj, bool):
        return obj
    if isinstance(obj, list):
        return [_round_obj_for_signature(x, ndigits) for x in obj]
    if isinstance(obj, tuple):
        return [_round_obj_for_signature(x, ndigits) for x in obj]
    if isinstance(obj, dict):
        return {k: _round_obj_for_signature(v, ndigits) for k, v in sorted(obj.items()) if k not in ignore}
    return str(obj)


def json_duplicate_signature(data: Dict[str, Any]) -> str:
    """Return a stable 99%-style signature for standalone JSON libraries."""
    core = {
        "schema": data.get("schema"),
        "version": data.get("version"),
        "material": data.get("material"),
        "type": data.get("type"),
        "size": data.get("size"),
        "port_count": data.get("port_count"),
        "center": data.get("center"),
        "flow": data.get("flow"),
        "ports": data.get("ports"),
        "geometry": data.get("geometry"),
    }
    blob = json.dumps(_round_obj_for_signature(core), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def txt_duplicate_signature(path: Path) -> str:
    """Return a stable signature for TXT libraries based on geometry and line types."""
    geo = parse_txt(path)
    core = {
        "segments": [{"x1": s.x1, "y1": s.y1, "x2": s.x2, "y2": s.y2, "lt": s.lt, "lc": s.lc, "ly": s.ly} for s in geo.segments],
        "circles": [{"cx": c.cx, "cy": c.cy, "r": c.r, "rest": c.rest, "lt": c.lt, "lc": c.lc, "ly": c.ly} for c in geo.circles],
    }
    blob = json.dumps(_round_obj_for_signature(core), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


STATUS_COLORS = {
    "ok": (218, 245, 226),
    "warn": (255, 237, 204),
    "error": (255, 218, 218),
    "unprocessed": (235, 239, 244),
    "duplicate": (255, 205, 205),
}
STATUS_LABELS = {
    "ok": "OK",
    "warn": "Cần kiểm tra",
    "error": "Lỗi",
    "unprocessed": "Chưa xử lý",
}


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except Exception:
        return default


def qa_analyze_data(path: Path, geo: Geometry, data: Dict[str, Any], duplicate: bool = False) -> Dict[str, Any]:
    """Return detailed QA status for one NEVIS library.

    The goal is not to block the operator.  It gives quick visual feedback:
    - ok: data is usable and convention is valid;
    - warn: usable but should be checked;
    - error: missing/broken critical data;
    - duplicate: content looks copied from another file.
    """
    messages: List[str] = []
    errors: List[str] = []
    warnings: List[str] = []
    ports = data.get("ports", []) if isinstance(data, dict) else []
    port_count = int(data.get("port_count", len(ports) or 0) or 0) if isinstance(data, dict) else 0
    auto = data.get("auto_detect", {}) if isinstance(data.get("auto_detect", {}), dict) else {}
    center = data.get("center") if isinstance(data, dict) else None
    center_conf = _safe_float(auto.get("center_confidence", 0.0), 0.0)
    port_conf = _safe_float(auto.get("port_count_confidence", 0.0), 0.0)
    if center_conf <= 0 and isinstance(center, list) and len(center) >= 2:
        center_conf = 0.85
    if port_conf <= 0 and port_count in (1, 2, 3) and len(ports) >= port_count:
        port_conf = 0.85

    if duplicate:
        warnings.append("File có nội dung/tọa độ gần như trùng với file khác")
    if not isinstance(data, dict):
        errors.append("Không đọc được JSON/data")
    if not geo.segments and not geo.circles:
        errors.append("Không có hình học line/ci")
    if not isinstance(center, list) or len(center) < 2:
        errors.append("Thiếu tâm cút center")
    if port_count not in (1, 2, 3):
        errors.append("Số cửa không hợp lệ")
    if len(ports) < port_count:
        errors.append(f"Thiếu port: cần {port_count}, hiện có {len(ports)}")
    if not geo.centerlines:
        warnings.append("Thiếu lt49/tim ống; nên tự tạo/vẽ tim hoặc kiểm tra tay")
    if auto.get("need_review"):
        warnings.append("Auto detect đánh dấu cần kiểm tra")
    if center_conf and center_conf < 0.8:
        warnings.append(f"Độ tin cậy tâm thấp: {round(center_conf*100)}%")
    if port_conf and port_conf < 0.9:
        warnings.append(f"Độ tin cậy số cửa thấp: {round(port_conf*100)}%")

    conv = data.get("port_convention_status") if isinstance(data.get("port_convention_status"), dict) else port_convention_status(data)
    if port_count == 3:
        if not conv.get("ok", False):
            warnings.append("Quy ước 3 cửa chưa đạt: P1–P2 phải là ống chính, P3 là nhánh phụ")
        else:
            messages.append("Quy ước 3 cửa OK: P1–P2 chính, P3 nhánh phụ")

    nr = name_rule_status(data)
    rule = nr.get("rule", {})
    if rule.get("detected_type"):
        messages.append("Quy tắc tên: " + str(rule.get("description", "")))
    for w in nr.get("warnings", []):
        warnings.append(w)
    flow = data.get("flow", {}) if isinstance(data.get("flow", {}), dict) else {}
    if flow.get("model") == "directional" and not flow.get("port"):
        warnings.append("Chưa có cửa chuẩn flow/hướng nước chảy")
    if flow.get("model") == "collector":
        messages.append("Flow collector: dùng cho S/集合管")

    # Each active port should have a cut point because it is the pipe contact boundary.
    missing_cut = []
    for i, p in enumerate(ports[:max(0, port_count)], 1):
        if not p.get("cut_point"):
            missing_cut.append(f"P{i}")
    if missing_cut:
        warnings.append("Thiếu điểm cắt/mép tiếp xúc: " + ", ".join(missing_cut))

    manual_approved = False
    approved = data.get("manual_approved") if isinstance(data, dict) else None
    if isinstance(approved, dict):
        manual_approved = bool(approved.get("approved"))
    elif isinstance(approved, bool):
        manual_approved = approved
    if manual_approved and not errors:
        messages.append("Đã được người dùng Đã kiểm tra sau khi kiểm tra thủ công")
        warnings = []
        center_conf = max(center_conf, 0.99)
        port_conf = max(port_conf, 0.99)

    confidence = 1.0
    vals = [v for v in (center_conf, port_conf) if v > 0]
    if vals:
        confidence = min(vals)
    if errors:
        status = "error"
        confidence = min(confidence, 0.35)
    elif warnings:
        status = "warn"
        confidence = min(confidence, 0.85)
    else:
        status = "ok"
        confidence = max(confidence, 0.95)

    return {
        "status": status,
        "label": STATUS_LABELS.get(status, status),
        "confidence": round(confidence, 4),
        "errors": errors,
        "warnings": warnings,
        "messages": messages,
        "port_count": port_count,
        "center_confidence": round(center_conf, 4),
        "port_count_confidence": round(port_conf, 4),
        "path": str(path),
    }


def qa_analyze_path(path: Path, duplicate: bool = False) -> Dict[str, Any]:
    try:
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            geo = geometry_from_json_data(data)
        else:
            geo = parse_txt(path)
            data = build_nevis_json(path, geo)
        return qa_analyze_data(path, geo, data, duplicate=duplicate)
    except Exception as e:
        return {
            "status": "error",
            "label": "Lỗi",
            "confidence": 0.0,
            "errors": [str(e)],
            "warnings": [],
            "messages": [],
            "port_count": 0,
            "center_confidence": 0.0,
            "port_count_confidence": 0.0,
            "path": str(path),
        }


class Canvas(QGraphicsView):
    pointPicked = Signal(float, float)
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.NoDrag)
        self._panning = False
        self._pan_last = None
        self.geo: Optional[Geometry] = None
        self.snap_mode = True
        self.last_rect = QRectF(-100, -100, 200, 200)

    def wheelEvent(self, ev):
        self.scale(1.15 if ev.angleDelta().y() > 0 else 1/1.15, 1.15 if ev.angleDelta().y() > 0 else 1/1.15)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._panning = True; self._pan_last = ev.pos(); ev.accept(); return
        if ev.button() == Qt.RightButton:
            p = self.mapToScene(ev.pos())
            x, y = p.x(), -p.y()
            if self.snap_mode and self.geo:
                x, y = self.snap_to_geometry(x, y)
            self.pointPicked.emit(x, y)
            ev.accept(); return
        super().mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._panning = False; self._pan_last = None; ev.accept(); return
        super().mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._panning and self._pan_last is not None:
            delta = ev.pos() - self._pan_last
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self._pan_last = ev.pos(); ev.accept(); return
        super().mouseMoveEvent(ev)

    def snap_to_geometry(self, x: float, y: float) -> Tuple[float,float]:
        if not self.geo:
            return x, y
        p = (x, y)
        scale = max(abs(self.transform().m11()), 1e-6)
        tol = 14.0 / scale
        tol_inter = 22.0 / scale

        # Priority 1: exact line-line intersections. This is the most stable
        # way to place ports/cut points on fitting mouths.
        inters: List[Tuple[float, Tuple[float,float]]] = []
        segs = self.geo.segments
        for i, a in enumerate(segs):
            for b in segs[i+1:]:
                ip = line_intersection_inf(a.p1, a.p2, b.p1, b.p2)
                if ip and dist(closest_point_on_segment(ip,a.p1,a.p2),ip) < 0.03 and dist(closest_point_on_segment(ip,b.p1,b.p2),ip) < 0.03:
                    inters.append((dist(p, ip), ip))
        if inters:
            best = min(inters, key=lambda z: z[0])
            if best[0] <= tol_inter:
                return best[1]

        # Priority 2: endpoints and midpoints.
        fixed: List[Tuple[float, Tuple[float,float]]] = []
        for s in self.geo.segments:
            for ep in (s.p1, s.p2):
                fixed.append((dist(p, ep), ep))
            mid = ((s.x1+s.x2)/2, (s.y1+s.y2)/2)
            fixed.append((dist(p, mid), mid))
        for c in self.geo.circles:
            fixed.append((dist(p, (c.cx, c.cy)), (c.cx, c.cy)))
        if fixed:
            best = min(fixed, key=lambda z: z[0])
            if best[0] <= tol:
                return best[1]

        # Priority 3: closest point on actual line/circle.
        nearest: List[Tuple[float, Tuple[float,float]]] = []
        for s in self.geo.segments:
            cp = closest_point_on_segment(p, s.p1, s.p2)
            nearest.append((dist(p, cp), cp))
        for c in self.geo.circles:
            vx, vy = x-c.cx, y-c.cy
            l = math.hypot(vx, vy)
            if l > 1e-9:
                cp = (c.cx + c.r*vx/l, c.cy + c.r*vy/l)
                nearest.append((dist(p, cp), cp))
        if nearest:
            best = min(nearest, key=lambda z: z[0])
            if best[0] <= tol:
                return best[1]
        return x, y


    def fit_all(self):
        self.fitInView(self.last_rect.adjusted(-30,-30,30,30), Qt.KeepAspectRatio)

    @staticmethod
    def cad_pen(color, width: float = 1.0, style=Qt.SolidLine) -> QPen:
        """CAD-style pen: line weight stays thin and constant while zooming."""
        pen = QPen(color, width, style)
        pen.setCosmetic(True)
        return pen

    @staticmethod
    def keep_screen_size(item):
        """Keep labels/markers readable like CAD annotations instead of scaling with zoom."""
        try:
            item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        except Exception:
            try:
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
            except Exception:
                pass
        return item

    def draw(self, geo: Geometry, json_data: Optional[Dict[str,Any]] = None, active_ports: int = 3, show_test=True):
        self.geo = geo
        sc = self.scene(); sc.clear()
        # CAD preview: cosmetic pens do not become thick when zooming.
        pen_solid = self.cad_pen(QColor(0, 105, 155), 1.0)
        pen_center = self.cad_pen(QColor(215, 65, 55), 1.0, Qt.DashLine)
        pen_arc = self.cad_pen(QColor(0, 105, 155), 1.0)
        pen_port = self.cad_pen(QColor(20, 80, 185), 1.0)
        brush_port = QBrush(QColor(70, 145, 255, 105))
        pts = []
        for s in geo.segments:
            pen = pen_center if s.lt == CENTER_LT else pen_solid
            sc.addLine(s.x1, -s.y1, s.x2, -s.y2, pen)
            pts += [(s.x1,-s.y1),(s.x2,-s.y2)]
        for c in geo.circles:
            pnts = arc_preview_points(c)
            if len(pnts) > 1:
                path = QPainterPath(QPointF(pnts[0][0], -pnts[0][1]))
                for x,y in pnts[1:]: path.lineTo(x, -y)
                sc.addPath(path, pen_arc if c.lt != CENTER_LT else pen_center)
                pts += [(x,-y) for x,y in pnts]
        if json_data:
            cx, cy = json_data.get("center", [0,0])[:2]
            sc.addLine(cx-8, -cy, cx+8, -cy, self.cad_pen(QColor(210,30,30), 1.2))
            sc.addLine(cx, -cy-8, cx, -cy+8, self.cad_pen(QColor(210,30,30), 1.2))
            self.keep_screen_size(sc.addEllipse(cx-3, -cy-3, 6, 6, self.cad_pen(QColor(210,30,30), 1.2), QBrush(QColor(255,70,70,95))))
            for p in json_data.get("ports", [])[:active_ports]:
                px, py = p.get("center", [cx,cy])[:2]
                role = str(p.get("role", ""))
                is_branch = (p.get("id") == "P3" or role == "branch") and int(json_data.get("port_count", active_ports) or active_ports) == 3
                if is_branch:
                    port_pen = self.cad_pen(QColor(170, 45, 165), 1.1)
                    port_brush = QBrush(QColor(220, 80, 220, 115))
                    line_pen = self.cad_pen(QColor(170, 45, 165), 1.0, Qt.DashDotLine)
                    label = f"{p.get('id','P')} nhánh phụ"
                else:
                    port_pen = pen_port
                    port_brush = brush_port
                    line_pen = self.cad_pen(QColor(45,105,205), 1.0, Qt.DotLine)
                    label = f"{p.get('id','P')} ống chính" if int(json_data.get("port_count", active_ports) or active_ports) >= 2 else p.get("id","P")
                self.keep_screen_size(sc.addEllipse(px-4, -py-4, 8, 8, port_pen, port_brush))
                tx = self.keep_screen_size(sc.addText(label))
                tx.setDefaultTextColor(QColor(170, 30, 160) if is_branch else QColor(20, 70, 150))
                tx.setPos(px+6, -py+3)
                if show_test:
                    sc.addLine(cx, -cy, px, -py, line_pen)
                cp = p.get("cut_point")
                if cp:
                    self.keep_screen_size(sc.addEllipse(cp[0]-3, -cp[1]-3, 6, 6, self.cad_pen(QColor(230,135,15), 1.0), QBrush(QColor(255,170,40,100))))
                pts += [(px,-py),(cx,-cy)]
            # Visual check of 3-port rule: P1-P2 is main route; P3 is branch.
            if int(json_data.get("port_count", active_ports) or active_ports) == 3 and show_test:
                ports_by_id = {pp.get("id"): pp for pp in json_data.get("ports", [])}
                if all(k in ports_by_id for k in ("P1", "P2", "P3")):
                    p1 = ports_by_id["P1"].get("center", [cx, cy])[:2]
                    p2 = ports_by_id["P2"].get("center", [cx, cy])[:2]
                    p3 = ports_by_id["P3"].get("center", [cx, cy])[:2]
                    sc.addLine(p1[0], -p1[1], p2[0], -p2[1], self.cad_pen(QColor(25, 85, 205), 1.1))
                    sc.addLine(cx, -cy, p3[0], -p3[1], self.cad_pen(QColor(170,45,165), 1.1, Qt.DashDotLine))
                    status = port_convention_status(json_data)
                    if not status.get("ok", True):
                        warn = self.keep_screen_size(sc.addText("⚠ P1-P2 chưa thẳng hàng / P3 chưa đúng góc nhánh"))
                        warn.setDefaultTextColor(QColor(220, 35, 35))
                        warn.setPos(cx + 10, -cy + 18)
            # Directional flow arrow: for drainage it points FROM fitting center TO the selected standard/downstream port.
            flow = json_data.get("flow", {}) if isinstance(json_data, dict) else {}
            fport = flow.get("port")
            if show_test and flow.get("model", "directional") != "collector" and fport:
                target = None
                for pp in json_data.get("ports", []):
                    if pp.get("id") == fport:
                        target = pp; break
                if target:
                    px, py = target.get("center", [cx, cy])[:2]
                    pen_flow = self.cad_pen(QColor(235, 80, 20), 1.2)
                    sc.addLine(cx, -cy, px, -py, pen_flow)
                    vx, vy = px-cx, (-py)-(-cy)
                    ll = math.hypot(vx, vy)
                    if ll > 1e-6:
                        ux, uy = vx/ll, vy/ll
                        bx, by = px - ux*12, -py - uy*12
                        nx, ny = -uy, ux
                        sc.addPolygon(QPolygonF([QPointF(px, -py), QPointF(bx+nx*5, by+ny*5), QPointF(bx-nx*5, by-ny*5)]), pen_flow, QBrush(QColor(240,80,20,105)))
        if not pts: pts = [(-100,-100),(100,100)]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        rect = QRectF(min(xs), min(ys), max(xs)-min(xs) or 100, max(ys)-min(ys) or 100)
        self.last_rect = rect.adjusted(-40,-40,40,40)
        sc.setSceneRect(self.last_rect)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEVIS JSON Library Editor FINAL 4 / Quy trình chuẩn hóa thư viện")
        self.resize(1360, 820)
        self.root = Path(os.environ.get("NEVIS_LIBRARY_ROOT", str(Path.cwd())))
        self.current_dir = self.root
        self.current_path: Optional[Path] = None
        self.geo = Geometry()
        self.json_data: Optional[Dict[str,Any]] = None
        self.mode = "view"
        self.pending_center: Optional[Tuple[float,float]] = None
        self.pending_line_start: Optional[Tuple[float,float]] = None
        self.pending_circle_center: Optional[Tuple[float,float]] = None
        self.qa_status_by_path: Dict[str, Dict[str, Any]] = {}
        self.qa_counts = {"ok":0, "warn":0, "error":0, "unprocessed":0}
        self.dirty = False
        self._loading = False
        self.duplicate_paths: set[str] = set()
        self.build_ui()
        self.apply_style()
        self.apply_nevis_language()
        self.refresh_folder_tree()
        self.refresh_files()
        QApplication.instance().installEventFilter(self)

    def apply_nevis_language(self):
        """Match editor language with NEVIS main window through NEVIS_LANG.

        The editor source was originally Vietnamese.  This lightweight layer
        translates the visible UI widgets after build_ui(), so the same editor
        can be opened from NEVIS in either Vietnamese or Japanese mode.
        """
        self.nevis_lang = os.environ.get("NEVIS_LANG", "vi").lower()
        if self.nevis_lang != "jp":
            return
        self.setWindowTitle("NEVIS JSON図庫編集 FINAL 4 / 図庫標準化")
        mp = {
            "📁 Chọn thư mục": "📁 フォルダ選択",
            "Tìm TXT/JSON trong folder đang chọn...": "選択フォルダ内のTXT/JSONを検索...",
            "Cây thư mục / Library": "フォルダツリー / Library",
            "Tất cả": "すべて",
            "Cần kiểm tra": "要確認",
            "Lỗi": "エラー",
            "Chưa xử lý": "未処理",
            "Quy trình thư viện": "図庫処理手順",
            "① TXT → JSON": "① TXT → JSON",
            "② Tự động hoàn thiện": "② 自動補完",
            "③ Kiểm tra thư viện": "③ 図庫チェック",
            "④ Dọn thư viện": "④ 図庫整理",
            "Chưa mở file": "ファイル未選択",
            "Thao tác": "操作",
            "Auto đọc lt49": "lt49自動読込",
            "Đặt tâm": "中心設定",
            "Nét vỏ lt1": "外形線 lt1",
            "Tim ống lt49": "中心線 lt49",
            "Vẽ Line H": "Line H作図",
            "Vẽ tròn E": "円E作図",
            "Xóa nét": "線削除",
            "Tự tạo tim": "中心線自動作成",
            "Xóa tim cuối": "最後の中心線削除",
            "Cửa nối / port": "接続口 / port",
            "Số cửa": "口数",
            "Kiểu 2 cửa": "2口タイプ",
            "Kiểu 3 cửa": "3口タイプ",
            "Áp dụng folder": "フォルダへ適用",
            "Cửa chuẩn": "基準口",
            "Hiển thị tim/cắt thử": "中心/カット表示",
            "Snap vào nét thật": "実線へスナップ",
            "P3 khóa": "P3固定",
            "Thông tin JSON": "JSON情報",
            "Tên": "名前",
            "Loại": "種類",
            "Dòng vật tư": "材質",
            "Vai trò": "役割",
            "Góc": "角度",
            "Cắt": "カット",
            "Đã kiểm tra": "チェック済み",
            "Chọn thư mục": "フォルダ選択",
            "Mỗi dòng là một mục. Size nên xếp từ lớn đến bé để quy tắc 'Giảm 1 bậc' chạy đúng.": "1行1項目です。サイズは大きい順に並べてください。",
        }
        def tx(v):
            return mp.get(v, v)
        widgets = self.findChildren(QWidget)
        for w in widgets:
            try:
                if isinstance(w, (QPushButton, QLabel, QCheckBox, QRadioButton, QGroupBox)):
                    if hasattr(w, 'text') and callable(w.text):
                        w.setText(tx(w.text()))
                    elif hasattr(w, 'title') and callable(w.title):
                        w.setTitle(tx(w.title()))
                if isinstance(w, QLineEdit):
                    w.setPlaceholderText(tx(w.placeholderText()))
                if isinstance(w, QTreeWidget):
                    try:
                        labels = [tx(w.headerItem().text(i)) for i in range(w.columnCount())]
                        w.setHeaderLabels(labels)
                    except Exception:
                        pass
            except Exception:
                pass
        try:
            for cb in self.findChildren(QComboBox):
                for i in range(cb.count()):
                    cb.setItemText(i, tx(cb.itemText(i)))
        except Exception:
            pass

    def eventFilter(self, obj, event):
        # Catch Space globally because child widgets/buttons often eat QAction shortcuts.
        # In this editor Space is reserved for rotating the fitting 45 degrees clockwise.
        try:
            if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Space and not event.isAutoRepeat():
                if self.current_path is not None and self.json_data is not None:
                    self.rotate_current_45_clockwise()
                    return True
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def build_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        main = QHBoxLayout(central); main.setContentsMargins(8,8,8,8); main.setSpacing(8)
        sp = QSplitter(Qt.Horizontal); main.addWidget(sp)

        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(6,6,6,6); ll.setSpacing(6)
        self.btn_folder = QPushButton("📁 Chọn thư mục")
        self.btn_folder.clicked.connect(self.choose_folder)
        self.search = QLineEdit(); self.search.setPlaceholderText("Tìm TXT/JSON trong folder đang chọn..."); self.search.textChanged.connect(self.refresh_files)
        self.folder_tree = QTreeWidget(); self.folder_tree.setHeaderLabel("Cây thư mục / Library")
        self.folder_tree.setMaximumHeight(210)
        self.folder_tree.itemClicked.connect(self.on_folder_tree_clicked)
        filter_box = QWidget(); filter_box.setObjectName("FilterBox"); filter_l = QHBoxLayout(filter_box); filter_l.setContentsMargins(6,4,6,4); filter_l.setSpacing(16)
        self.rb_all = QRadioButton("Tất cả"); self.rb_txt = QRadioButton("TXT"); self.rb_json = QRadioButton("JSON")
        self.rb_all.setChecked(True)
        self.file_filter_group = QButtonGroup(self)
        for rb in (self.rb_all, self.rb_txt, self.rb_json):
            self.file_filter_group.addButton(rb)
            filter_l.addWidget(rb)
            rb.toggled.connect(self.refresh_files)
        filter_l.addStretch()
        status_box = QWidget(); status_box.setObjectName("StatusFilterBox"); status_l = QHBoxLayout(status_box); status_l.setContentsMargins(6,4,6,4); status_l.setSpacing(8)
        self.rb_status_all = QRadioButton("Tất cả")
        self.rb_status_ok = QRadioButton("OK")
        self.rb_status_warn = QRadioButton("Cần kiểm tra")
        self.rb_status_error = QRadioButton("Lỗi")
        self.rb_status_unprocessed = QRadioButton("Chưa xử lý")
        self.rb_status_all.setChecked(True)
        self.status_filter_group = QButtonGroup(self)
        for rb in (self.rb_status_all, self.rb_status_ok, self.rb_status_warn, self.rb_status_error, self.rb_status_unprocessed):
            self.status_filter_group.addButton(rb)
            status_l.addWidget(rb)
            rb.toggled.connect(self.refresh_files)
        status_l.addStretch()
        self.listw = QListWidget(); self.listw.itemClicked.connect(self.open_item)
        ll.addWidget(self.btn_folder); ll.addWidget(self.folder_tree); ll.addWidget(self.search); ll.addWidget(filter_box); ll.addWidget(status_box); ll.addWidget(self.listw,1)
        batch = QGroupBox("Quy trình thư viện")
        bg = QGridLayout(batch); bg.setSpacing(6); bg.setContentsMargins(8,8,8,8)
        self.btn_step1_convert = QPushButton("① TXT → JSON")
        self.btn_step1_convert.setToolTip("Bước 1: Chuyển TXT trong folder/danh sách hiện tại sang JSON độc lập.")
        self.btn_step1_convert.clicked.connect(self.batch_convert)
        self.btn_step2_complete = QPushButton("② Tự động hoàn thiện")
        self.btn_step2_complete.setToolTip("Bước 2: Tự tạo lt49, port, flow cho toàn bộ file đang hiển thị rồi tự lưu JSON.")
        self.btn_step2_complete.clicked.connect(self.auto_complete_visible_libraries)
        self.btn_step3_check = QPushButton("③ Kiểm tra thư viện")
        self.btn_step3_check.setToolTip("Bước 3: Kiểm tra trùng, geometry, port, flow và quy tắc tên cho toàn bộ file đang hiển thị.")
        self.btn_step3_check.clicked.connect(self.check_visible_libraries)
        self.btn_step4_clean = QPushButton("④ Dọn thư viện")
        self.btn_step4_clean.setToolTip("Bước 4: Xóa TXT đã có JSON cùng tên và xóa file .bak trong folder đang chọn.")
        self.btn_step4_clean.clicked.connect(self.clean_visible_library_files)
        bg.addWidget(self.btn_step1_convert,0,0,1,2)
        bg.addWidget(self.btn_step2_complete,1,0,1,2)
        bg.addWidget(self.btn_step3_check,2,0,1,2)
        bg.addWidget(self.btn_step4_clean,3,0,1,2)
        ll.addWidget(batch)
        sp.addWidget(left)

        center = QWidget(); cl = QVBoxLayout(center); cl.setContentsMargins(0,0,0,0); cl.setSpacing(6)
        self.info = QLabel("Chưa mở file")
        self.info.setFrameShape(QFrame.StyledPanel)
        self.qa_legend = QLabel("")
        self.qa_legend.setObjectName("QALegend")
        self.qa_legend.setWordWrap(True)
        self.status_detail = QLabel("")
        self.status_detail.setObjectName("StatusDetail")
        self.status_detail.setWordWrap(True)
        self.canvas = Canvas(); self.canvas.pointPicked.connect(self.point_picked)
        cl.addWidget(self.info); cl.addWidget(self.qa_legend); cl.addWidget(self.status_detail); cl.addWidget(self.canvas,1)
        sp.addWidget(center)

        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(6,6,6,6); rl.setSpacing(7)
        gtop = QGroupBox("Thao tác")
        tg = QGridLayout(gtop); tg.setSpacing(5); tg.setContentsMargins(8,8,8,8)
        self.btn_fit = QPushButton("Fit")
        self.btn_fit.clicked.connect(self.canvas.fit_all)
        self.btn_auto = QPushButton("Auto đọc lt49")
        self.btn_auto.clicked.connect(self.auto_detect)
        self.btn_rotate45 = QPushButton("↻ 45°")
        self.btn_rotate45.setToolTip("Xoay cút 45° theo chiều kim đồng hồ quanh tâm cút. Phím tắt: Space")
        self.btn_rotate45.clicked.connect(self.rotate_current_45_clockwise)
        self.btn_center = QPushButton("Đặt tâm")
        self.btn_center.clicked.connect(self.toggle_center_mode)
        self.cmb_draw_lt = QComboBox()
        self.cmb_draw_lt.addItems(["Nét vỏ lt1", "Tim ống lt49"])
        self.cmb_draw_lt.setToolTip("Chọn loại nét trước khi vẽ Line/Circle. Line có thể là nét vỏ hoặc tim ống; Circle mặc định là nét vỏ.")
        self.btn_draw_line = QPushButton("Vẽ Line H")
        self.btn_draw_line.setToolTip("Vẽ đoạn thẳng bằng 2 lần chuột phải. Snap ưu tiên: giao điểm → đầu mút → trung điểm → điểm trên nét.")
        self.btn_draw_line.clicked.connect(self.toggle_draw_line_mode)
        self.btn_draw_circle = QPushButton("Vẽ tròn E")
        self.btn_draw_circle.setToolTip("Vẽ đường tròn bằng 2 lần chuột phải: tâm → điểm bán kính. Snap ưu tiên tuyệt đối.")
        self.btn_draw_circle.clicked.connect(self.toggle_draw_circle_mode)
        self.btn_undo_line = QPushButton("Xóa tim cuối")
        self.btn_undo_line.setToolTip("Xóa đoạn tim lt49 vừa vẽ thêm")
        self.btn_undo_line.clicked.connect(self.delete_last_centerline)
        self.btn_delete_entity = QPushButton("Xóa nét")
        self.btn_delete_entity.setToolTip("Bật chế độ xóa nét: chuột phải lên line/cung để xóa liên tiếp, bấm lại để kết thúc")
        self.btn_delete_entity.clicked.connect(self.toggle_delete_entity_mode)
        self.btn_make_cl = QPushButton("Tự tạo tim")
        self.btn_make_cl.setToolTip("Tạo nhanh lt49 theo số cửa đang chọn. Dùng khi TXT bị thiếu tim ống.")
        self.btn_make_cl.clicked.connect(self.auto_create_centerlines)
        self.btn_save = QPushButton("● LƯU JSON")
        self.btn_save.setObjectName("SaveButton")
        self.btn_save.clicked.connect(self.save_json)
        self.btn_approve = QPushButton("✓ Đã kiểm tra")
        self.btn_approve.setObjectName("ApproveButton")
        self.btn_approve.setToolTip("Đánh dấu thư viện đã được kiểm tra thủ công. QA sẽ nâng lên OK nếu không còn lỗi nghiêm trọng.")
        self.btn_approve.clicked.connect(self.approve_current_library)
        tg.addWidget(self.btn_fit,0,0); tg.addWidget(self.btn_auto,0,1)
        tg.addWidget(self.btn_rotate45,1,0); tg.addWidget(self.btn_center,1,1)
        tg.addWidget(self.btn_save,2,0); tg.addWidget(self.btn_approve,2,1)
        tg.addWidget(QLabel("Kiểu nét"),3,0); tg.addWidget(self.cmb_draw_lt,3,1)
        tg.addWidget(self.btn_draw_line,4,0); tg.addWidget(self.btn_draw_circle,4,1)
        tg.addWidget(self.btn_delete_entity,5,0); tg.addWidget(self.btn_make_cl,5,1)
        tg.addWidget(self.btn_undo_line,6,0,1,2)
        rl.addWidget(gtop)

        gport = QGroupBox("Cửa nối / port")
        pg = QGridLayout(gport); pg.setSpacing(4); pg.setContentsMargins(8,8,8,8)
        self.cmb_port_count = QComboBox(); self.cmb_port_count.addItems(["Auto", "1", "2", "3"])
        self.cmb_port_count.setMinimumWidth(62)
        self.cmb_port_count.setToolTip("Số cửa nối của fitting")
        self.cmb_port_count.currentTextChanged.connect(self.port_count_changed)
        self.cmb_2port_shape = QComboBox()
        self.cmb_2port_shape.addItems(["Auto", "Thẳng 180°", "Vuông 90°", "Chéo 45°", "Chéo 135°"])
        self.cmb_2port_shape.setToolTip("Chỉ dùng khi số cửa = 2. Tự tạo tim sẽ dựa theo kiểu này để sinh lt49 chính xác hơn.")
        self.cmb_2port_shape.currentTextChanged.connect(self.two_port_shape_changed)
        self.cmb_3port_shape = QComboBox()
        self.cmb_3port_shape.addItems(["Auto", "Nhánh 90°", "Nhánh 45°", "Nhánh 135°"])
        self.cmb_3port_shape.setToolTip("Chỉ dùng khi số cửa = 3. P1-P2 là tuyến chính, P3 là nhánh phụ; chọn góc nhánh để tự tạo tim/QA rõ hơn.")
        self.cmb_3port_shape.currentTextChanged.connect(self.three_port_shape_changed)
        self.btn_port_count_batch = QPushButton("Áp dụng folder")
        self.btn_port_count_batch.setToolTip("Áp dụng số cửa đang chọn cho toàn bộ TXT/JSON trong thư mục và tự lưu JSON")
        self.btn_port_count_batch.clicked.connect(self.batch_apply_port_count)
        self.cmb_flow = QComboBox(); self.cmb_flow.addItems(["directional - có hướng", "collector - S/集合管"])
        self.cmb_flow.currentTextChanged.connect(self.flow_changed)
        self.cmb_flow_port = QComboBox(); self.cmb_flow_port.addItems(["Auto", "P1", "P2", "P3"])
        self.cmb_flow_port.currentTextChanged.connect(self.flow_port_changed)
        self.chk_show_test = QCheckBox("Hiển thị tim/cắt thử"); self.chk_show_test.setChecked(True); self.chk_show_test.stateChanged.connect(self.redraw)
        self.chk_snap = QCheckBox("Snap vào nét thật"); self.chk_snap.setChecked(True); self.chk_snap.stateChanged.connect(lambda: setattr(self.canvas, 'snap_mode', self.chk_snap.isChecked()))
        pg.addWidget(QLabel("Số cửa"),0,0); pg.addWidget(self.cmb_port_count,0,1)
        pg.addWidget(QLabel("Kiểu 2 cửa"),0,2); pg.addWidget(self.cmb_2port_shape,0,3)
        pg.addWidget(QLabel("Kiểu 3 cửa"),1,0); pg.addWidget(self.cmb_3port_shape,1,1)
        pg.addWidget(self.btn_port_count_batch,1,2,1,2)
        self.role_rule_label = QLabel("3 cửa: P1–P2 là tuyến chính, P3 là nhánh phụ; chọn góc nhánh 90/45/135 để tự tạo tim.")
        self.role_rule_label.setObjectName("HintLabel")
        self.role_rule_label.setWordWrap(True)
        pg.addWidget(self.role_rule_label,2,0,1,4)
        pg.addWidget(QLabel("Flow"),3,0); pg.addWidget(self.cmb_flow,3,1,1,3)
        pg.addWidget(QLabel("Cửa chuẩn"),4,0); pg.addWidget(self.cmb_flow_port,4,1,1,3)
        pg.addWidget(self.chk_show_test,5,0,1,2); pg.addWidget(self.chk_snap,5,2,1,2)
        self.port_btns = []
        short_labels = ["P1 chính", "P2 chính", "P3 phụ"]
        for i in range(3):
            b = QPushButton(short_labels[i])
            b.setMinimumWidth(0)
            b.clicked.connect(lambda _=False, k=i: self.set_port_mode(k))
            self.port_btns.append(b); pg.addWidget(b,6,i)
        rl.addWidget(gport)

        gmeta = QGroupBox("Thông tin JSON")
        mg = QGridLayout(gmeta); mg.setSpacing(5); mg.setContentsMargins(8,8,8,8)
        self.ed_name = QLineEdit(); self.ed_type = QLineEdit(); self.ed_size = QLineEdit(); self.ed_mat = QLineEdit()
        for _ed in (self.ed_name, self.ed_type, self.ed_size, self.ed_mat):
            _ed.textChanged.connect(lambda _=None: self.mark_dirty(True))
        self.btn_mat_batch = QPushButton("Áp dụng folder")
        self.btn_mat_batch.setToolTip("Ghi dòng vật tư này vào toàn bộ JSON trong thư mục đang chọn")
        self.btn_mat_batch.clicked.connect(self.batch_apply_material)
        mg.addWidget(QLabel("Tên"),0,0); mg.addWidget(self.ed_name,0,1,1,2)
        mg.addWidget(QLabel("Loại"),1,0); mg.addWidget(self.ed_type,1,1,1,2)
        mg.addWidget(QLabel("Size"),2,0); mg.addWidget(self.ed_size,2,1,1,2)
        self.lbl_mat = QLabel("Dòng vật tư")
        self.lbl_mat.setToolTip("Ví dụ: DV, TMP, VP, HTVP... NEVIS dùng trường này để phân loại vật tư/thư viện.")
        self.ed_mat.setToolTip("Dòng vật tư: DV/TMP/VP/HTVP... không phải tên hệ thống thoát nước, mà là chủng loại thư viện.")
        mg.addWidget(self.lbl_mat,3,0); mg.addWidget(self.ed_mat,3,1); mg.addWidget(self.btn_mat_batch,3,2)
        rl.addWidget(gmeta)

        self.table = QTableWidget(3, 6)
        self.table.setHorizontalHeaderLabels(["Port", "Vai trò", "X", "Y", "Góc", "Cut"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMaximumHeight(145)
        rl.addWidget(self.table)

        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMaximumHeight(120)
        rl.addWidget(self.log)
        rl.addStretch()
        sp.addWidget(right)
        sp.setSizes([260,760,340])

        QAction("H", self, shortcut=QKeySequence("H"), triggered=self.toggle_draw_line_mode).setParent(self)
        QAction("E", self, shortcut=QKeySequence("E"), triggered=self.toggle_draw_circle_mode).setParent(self)
        QAction("T", self, shortcut=QKeySequence("T"), triggered=lambda: self.log_msg("T: trim/extend chưa bật ở bản tối giản này; ưu tiên Line/Circle + snap chuẩn trước.")).setParent(self)
        QAction("V", self, shortcut=QKeySequence("V"), triggered=lambda: self.log_msg("V: vát góc chưa bật ở bản tối giản này; ưu tiên Line/Circle + snap chuẩn trước.")).setParent(self)
        self.act_space_rotate = QAction("SpaceRotate45", self, shortcut=QKeySequence(Qt.Key_Space), triggered=self.rotate_current_45_clockwise)
        self.act_space_rotate.setShortcutContext(Qt.ApplicationShortcut)
        self.act_space_rotate.setParent(self)
        self.update_save_button()

    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#F4F7FA; color:#1F2D3D; font-family: Segoe UI, Meiryo; font-size: 9pt; }
            QGroupBox { border:1px solid #C9D6E2; border-radius:8px; margin-top:8px; padding-top:8px; background:#FFFFFF; font-weight:600; }
            QGroupBox::title { subcontrol-origin: margin; left:10px; padding:0 4px; color:#24547A; }
            QPushButton { background:#E7F0F8; border:1px solid #B6CADB; border-radius:6px; padding:5px 8px; }
            QPushButton:hover { background:#D9EAF7; }
            QPushButton:pressed { background:#C7DFF0; }
            QPushButton:disabled { background:#EEF1F4; color:#9AA7B2; border-color:#D5DCE3; }
            QPushButton#SaveButton { background:#FFE1E1; color:#B00000; border:2px solid #D64545; border-radius:8px; padding:7px 10px; font-weight:900; }
            QPushButton#ApproveButton { background:#E4F8EA; color:#087A2A; border:2px solid #2BA84A; border-radius:8px; padding:6px 10px; font-weight:800; }
            QPushButton#ApproveButton:hover { background:#D3F2DC; }
            QPushButton#SaveButton:hover { background:#FFD0D0; }
            QRadioButton { background:#E9F2FA; border:1px solid #AFC7DA; border-radius:10px; padding:4px 12px; spacing:6px; font-weight:700; color:#244C70; }
            QRadioButton:hover { background:#D8EAF8; }
            QRadioButton:checked { background:#2F80C9; color:white; border:1px solid #1F5F98; }
            QRadioButton::indicator { width:0px; height:0px; }
            QLabel#QALegend { background:#FFFFFF; border:1px solid #C9D6E2; border-radius:7px; padding:6px 8px; color:#243B53; }
            QLabel#StatusDetail { background:#F8FBFD; border:1px solid #D6E3EC; border-radius:7px; padding:6px 8px; color:#2B3A46; }
            QLineEdit, QComboBox, QTableWidget, QTextEdit { background:#FFFFFF; border:1px solid #C9D6E2; border-radius:5px; padding:3px; }
            QListWidget::item { padding:3px; }
            QTreeWidget { background:#FFFFFF; border:1px solid #C9D6E2; border-radius:6px; padding:2px; }
            QTreeWidget::item { padding:3px; }
            QTreeWidget::item:selected { background:#CFE7FA; color:#103A5A; }
            QLabel { color:#2B3A46; }
        """)

    def mark_dirty(self, value: bool = True):
        if getattr(self, '_loading', False):
            return
        self.dirty = bool(value)
        self.update_save_button()

    def update_save_button(self):
        if hasattr(self, 'btn_save'):
            self.btn_save.setVisible(bool(getattr(self, 'dirty', False)))
            self.btn_save.setEnabled(bool(getattr(self, 'dirty', False)))

    def choose_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Chọn thư mục gốc thư viện", str(self.root))
        if d:
            self.root = Path(d)
            self.current_dir = self.root
            self.refresh_folder_tree()
            self.refresh_files()

    def active_folder(self) -> Path:
        d = getattr(self, 'current_dir', None)
        if isinstance(d, Path) and d.exists():
            return d
        return self.root

    def refresh_folder_tree(self):
        if not hasattr(self, 'folder_tree'):
            return
        self.folder_tree.clear()
        root_item = QTreeWidgetItem([self.root.name or str(self.root)])
        root_item.setData(0, Qt.UserRole, str(self.root))
        self.folder_tree.addTopLevelItem(root_item)
        self._add_folder_items(root_item, self.root)
        root_item.setExpanded(True)
        self.folder_tree.setCurrentItem(root_item)

    def _add_folder_items(self, parent_item, folder: Path):
        try:
            dirs = sorted([p for p in folder.iterdir() if p.is_dir() and not p.name.startswith('.') and p.name != '__pycache__'], key=lambda p: p.name.lower())
        except Exception:
            dirs = []
        for d in dirs:
            it = QTreeWidgetItem([d.name])
            it.setData(0, Qt.UserRole, str(d))
            parent_item.addChild(it)
            self._add_folder_items(it, d)

    def on_folder_tree_clicked(self, item, column=0):
        try:
            p = Path(item.data(0, Qt.UserRole))
            if p.exists() and p.is_dir():
                self.current_dir = p
                self.refresh_files()
                self.log_msg(f"Folder đang chọn: {p.relative_to(self.root) if p != self.root else p.name}")
        except Exception:
            pass

    def refresh_files(self):
        self.listw.clear()
        q = self.search.text().lower().strip() if hasattr(self, 'search') else ""
        try:
            if hasattr(self, 'rb_txt') and self.rb_txt.isChecked():
                files = sorted(list(self.active_folder().glob("*.txt")), key=lambda p: str(p).lower())
            elif hasattr(self, 'rb_json') and self.rb_json.isChecked():
                files = sorted(list(self.active_folder().glob("*.json")), key=lambda p: str(p).lower())
            else:
                files = sorted(list(self.active_folder().glob("*.txt")) + list(self.active_folder().glob("*.json")), key=lambda p: str(p).lower())
        except Exception:
            files = []
        dup_set = getattr(self, 'duplicate_paths', set())
        wanted_status = "all"
        if hasattr(self, 'rb_status_ok'):
            if self.rb_status_ok.isChecked(): wanted_status = "ok"
            elif self.rb_status_warn.isChecked(): wanted_status = "warn"
            elif self.rb_status_error.isChecked(): wanted_status = "error"
            elif self.rb_status_unprocessed.isChecked(): wanted_status = "unprocessed"
        for p in files:
            rel = str(p.relative_to(self.root))
            if q and q not in rel.lower():
                continue
            pkey = str(p.resolve())
            qa = getattr(self, 'qa_status_by_path', {}).get(pkey)
            status = qa.get('status') if qa else 'unprocessed'
            if wanted_status != "all" and status != wanted_status:
                continue
            is_dup = pkey in dup_set
            if is_dup and status != 'error':
                status = 'warn'
            prefix = "[JSON] " if p.suffix.lower()==".json" else "[TXT] "
            icon = {"ok":"🟢 ", "warn":"🟠 ", "error":"🔴 ", "unprocessed":"⚪ "}.get(status, "⚪ ")
            conf_txt = ""
            if qa and qa.get('confidence') is not None:
                conf_txt = f"  {round(float(qa.get('confidence',0))*100)}%"
            item = QListWidgetItem(icon + prefix + rel + conf_txt)
            item.setData(Qt.UserRole, str(p))
            r,g,b = STATUS_COLORS.get(status, STATUS_COLORS['unprocessed'])
            item.setBackground(QColor(r,g,b))
            if status == 'error' or is_dup:
                item.setForeground(QColor(160, 0, 0))
            elif status == 'warn':
                item.setForeground(QColor(130, 80, 0))
            if qa:
                tip = []
                if qa.get('errors'): tip += ['Lỗi: ' + '; '.join(qa.get('errors', [])[:3])]
                if qa.get('warnings'): tip += ['Cần kiểm tra: ' + '; '.join(qa.get('warnings', [])[:4])]
                if qa.get('messages'): tip += qa.get('messages', [])[:2]
                item.setToolTip('\n'.join(tip) if tip else 'OK')
            elif is_dup:
                item.setToolTip("Có nội dung/tọa độ gần như trùng với file khác")
            self.listw.addItem(item)
        self.update_qa_legend()

    def open_item(self, item):
        self.open_file(Path(item.data(Qt.UserRole)))

    def open_file(self, path: Path):
        self.current_path = path
        self._loading = True
        try:
            if path.suffix.lower() == ".json":
                data = json.loads(path.read_text(encoding="utf-8-sig"))
                # Read standalone JSON directly. Do NOT create /tmp files; Windows has no /tmp by default.
                self.geo = geometry_from_json_data(data)
                self.json_data = data
            else:
                self.geo = parse_txt(path)
                self.json_data = build_nevis_json(path, self.geo)
            self.load_meta_to_ui()
            self.info.setText(f"{path.name} | line={len(self.geo.segments)} lt49={len(self.geo.centerlines)} ci={len(self.geo.circles)}")
            self.update_current_status_detail(path)
            self.redraw(); self.canvas.fit_all()
            self._loading = False
            # TXT opened for editing/conversion should clearly show that JSON can be saved.
            self.dirty = path.suffix.lower() != ".json"
            self.update_save_button()
            self.log_msg(f"Đã mở: {path.name}")
        except Exception as e:
            self._loading = False
            QMessageBox.critical(self, "Lỗi", str(e))


    def _empty_port_dict(self, idx: int) -> Dict[str, Any]:
        cx, cy = (self.json_data or {}).get("center", [0, 0])[:2]
        roles = ["main_1", "main_2", "branch"] if self.current_port_count() == 3 else (["main_1", "main_2", ""] if self.current_port_count() == 2 else ["single", "", ""])
        role = roles[idx] if idx < len(roles) and roles[idx] else "manual"
        return {
            "id": f"P{idx+1}",
            "role": role,
            "center": [cx, cy],
            "direction": [0.0, -1.0],
            "angle_deg": 270.0,
            "centerline": [[cx, cy], [cx, cy]],
            "cut_point": None,
            "source": "manual_pending",
            "confidence": 0.0,
        }

    def ensure_port_slots(self):
        if not self.json_data:
            return
        pc = self.current_port_count()
        ports = self.json_data.setdefault("ports", [])
        while len(ports) < pc:
            ports.append(self._empty_port_dict(len(ports)))
        # Do not show/use ports beyond selected count, but keep data if user switches back.
        roles3 = ["main_1", "main_2", "branch"]
        roles2 = ["main_1", "main_2"]
        for i, p in enumerate(ports[:pc]):
            p["id"] = f"P{i+1}"
            if p.get("source") == "manual_pending" or not p.get("role") or p.get("role") == "single":
                if pc == 3:
                    p["role"] = roles3[i]
                elif pc == 2:
                    p["role"] = roles2[i]
                else:
                    p["role"] = "single"

    def ensure_json_ports(self, force_rebuild: bool = False):
        """Keep JSON ports synchronized with the selected 1/2/3-port count.

        This fixes stale JSON files made by older builds: for DT/SV a through
        lt49 centerline must become two opposite ports, plus the branch port.
        """
        if not self.current_path or not self.json_data:
            return
        pc = self.current_port_count()
        ports = self.json_data.get("ports", []) or []
        manual_count = hasattr(self, 'cmb_port_count') and not self.cmb_port_count.currentText().startswith("Auto")
        if (not force_rebuild) and manual_count:
            self.ensure_port_slots()
            self.json_data["port_count"] = pc
            self.json_data.setdefault("flow", {})["model"] = self.flow_model()
            return
        if force_rebuild or len(ports) < pc:
            old_flow = (self.json_data.get("flow", {}) or {}).get("model", self.flow_model())
            old_mat = self.json_data.get("material", "")
            old_name = self.json_data.get("name", "")
            old_type = self.json_data.get("type", "")
            old_size = self.json_data.get("size", "")
            self.json_data = build_nevis_json(
                self.current_path, self.geo, pc,
                manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"),
                flow_model=old_flow or self.flow_model()
            )
            # Preserve user-edited metadata when rebuilding ports.
            if old_mat: self.json_data["material"] = old_mat
            if old_name: self.json_data["name"] = old_name
            if old_type: self.json_data["type"] = old_type
            if old_size: self.json_data["size"] = old_size
        self.ensure_port_slots()
        self.json_data["port_count"] = pc
        self.json_data.setdefault("flow", {})["model"] = self.flow_model()
        if self.flow_model() == "collector":
            self.json_data["flow"]["port"] = None
        elif not self.json_data["flow"].get("port"):
            self.json_data["flow"]["port"] = default_flow_port([Port(
                id=p.get("id", "P"),
                center=tuple(p.get("center", [0,0])),
                direction=tuple(p.get("direction", [1,0])),
                angle=float(p.get("angle_deg", 0))
            ) for p in self.json_data.get("ports", [])], self.flow_model())

    def load_meta_to_ui(self):
        d = self.json_data or {}
        self.ed_name.setText(str(d.get("name", "")))
        self.ed_type.setText(str(d.get("type", "")))
        self.ed_size.setText(str(d.get("size", "")))
        self.ed_mat.setText(str(d.get("material", "")))
        pc = d.get("port_count", 0)
        self.cmb_port_count.blockSignals(True)
        self.cmb_port_count.setCurrentText(str(pc) if pc in (1,2,3) else "Auto")
        self.cmb_port_count.blockSignals(False)
        if hasattr(self, 'cmb_2port_shape'):
            val2 = str(d.get("two_port_shape", "Auto"))
            self.cmb_2port_shape.blockSignals(True)
            if val2 in [self.cmb_2port_shape.itemText(i) for i in range(self.cmb_2port_shape.count())]:
                self.cmb_2port_shape.setCurrentText(val2)
            else:
                self.cmb_2port_shape.setCurrentText("Auto")
            self.cmb_2port_shape.blockSignals(False)
        if hasattr(self, 'cmb_3port_shape'):
            val3 = str(d.get("three_port_shape", d.get("expected_branch_angle_rule", "Auto")))
            self.cmb_3port_shape.blockSignals(True)
            if val3 in [self.cmb_3port_shape.itemText(i) for i in range(self.cmb_3port_shape.count())]:
                self.cmb_3port_shape.setCurrentText(val3)
            else:
                self.cmb_3port_shape.setCurrentText("Auto")
            self.cmb_3port_shape.blockSignals(False)
        flow_model = d.get("flow",{}).get("model", "directional")
        self.cmb_flow.blockSignals(True)
        self.cmb_flow.setCurrentIndex(1 if flow_model == "collector" else 0)
        self.cmb_flow.blockSignals(False)
        fport = d.get("flow",{}).get("port") or "Auto"
        if hasattr(self, 'cmb_flow_port'):
            self.cmb_flow_port.blockSignals(True)
            self.cmb_flow_port.setCurrentText(fport if fport in ("P1","P2","P3") else "Auto")
            self.cmb_flow_port.blockSignals(False)
        # If this JSON was created by an older build and is missing a DT/SV port, rebuild now.
        self.ensure_json_ports(force_rebuild=(len(d.get("ports", []) or []) < self.current_port_count()))
        self.update_port_buttons()
        self.rebuild_table()

    def current_port_count(self) -> int:
        txt = self.cmb_port_count.currentText().strip()
        if txt.startswith("1"): return 1
        if txt.startswith("2"): return 2
        if txt.startswith("3"): return 3
        return detect_port_count(self.geo)[0]

    def two_port_shape(self) -> str:
        if not hasattr(self, 'cmb_2port_shape'):
            return "Auto"
        return self.cmb_2port_shape.currentText().strip()

    def two_port_shape_changed(self):
        if self.current_port_count() == 2:
            self.mark_dirty(True)
            self.log_msg(f"Kiểu 2 cửa: {self.two_port_shape()}")

    def three_port_shape(self) -> str:
        if not hasattr(self, 'cmb_3port_shape'):
            return "Auto"
        return self.cmb_3port_shape.currentText().strip()

    def three_port_shape_changed(self):
        if self.current_port_count() == 3:
            if self.json_data is not None:
                self.json_data["three_port_shape"] = self.three_port_shape()
                self.json_data["expected_branch_angle_rule"] = self.three_port_shape()
            self.mark_dirty(True)
            self.log_msg(f"Kiểu 3 cửa: {self.three_port_shape()}")

    def port_count_changed(self):
        if not self.current_path: return
        pc = self.current_port_count()
        # Rebuild all ports from lt49 whenever the operator changes 1/2/3 cửa.
        self.json_data = build_nevis_json(
            self.current_path, self.geo, pc,
            manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"),
            flow_model=self.flow_model()
        )
        self.load_meta_to_ui(); self.redraw(); self.mark_dirty(True); self.log_msg(f"Số cửa: {pc}")

    def flow_model(self):
        return "collector" if self.cmb_flow.currentIndex() == 1 else "directional"

    def flow_changed(self):
        if self.json_data:
            self.ensure_json_ports(force_rebuild=False)
            self.json_data.setdefault("flow", {})["model"] = self.flow_model()
            if self.flow_model() == "collector":
                self.json_data["flow"]["port"] = None
            elif self.cmb_flow_port.currentText() == "Auto":
                self.json_data["flow"]["port"] = default_flow_port([Port(
                    id=p.get("id", "P"), center=tuple(p.get("center", [0,0])),
                    direction=tuple(p.get("direction", [1,0])), angle=float(p.get("angle_deg", 0))
                ) for p in self.json_data.get("ports", [])], self.flow_model())
            self.update_port_buttons()
            self.redraw()
            self.mark_dirty(True)

    def flow_port_changed(self):
        if not self.json_data:
            return
        self.ensure_json_ports(force_rebuild=False)
        self.json_data.setdefault("flow", {})["model"] = self.flow_model()
        if self.flow_model() == "collector":
            self.json_data["flow"]["port"] = None
        elif self.cmb_flow_port.currentText() == "Auto":
            self.json_data["flow"]["port"] = default_flow_port([Port(
                id=p.get("id", "P"), center=tuple(p.get("center", [0,0])),
                direction=tuple(p.get("direction", [1,0])), angle=float(p.get("angle_deg", 0))
            ) for p in self.json_data.get("ports", [])], self.flow_model())
        else:
            self.json_data["flow"]["port"] = self.cmb_flow_port.currentText()
        self.redraw()
        self.mark_dirty(True)
        self.log_msg(f"Cửa chuẩn flow: {self.json_data.get('flow',{}).get('port')}")

    def update_port_buttons(self):
        pc = self.current_port_count()
        collector = self.flow_model() == "collector"
        labels3 = ["P1 chính", "P2 chính", "P3 phụ"]
        labels2 = ["P1", "P2", "P3 khóa"]
        labels1 = ["P1", "P2 khóa", "P3 khóa"]
        labels = labels3 if pc == 3 else (labels2 if pc == 2 else labels1)
        for i,b in enumerate(self.port_btns):
            b.setEnabled(i < pc)
            b.setText(labels[i])
        if hasattr(self, 'cmb_2port_shape'):
            self.cmb_2port_shape.setEnabled(pc == 2)
        if hasattr(self, 'cmb_3port_shape'):
            self.cmb_3port_shape.setEnabled(pc == 3)
        if hasattr(self, 'cmb_flow_port'):
            self.cmb_flow_port.setEnabled(not collector)
            cur = self.cmb_flow_port.currentText()
            if cur in ("P1", "P2", "P3") and int(cur[1]) > pc:
                self.cmb_flow_port.blockSignals(True)
                self.cmb_flow_port.setCurrentText("Auto")
                self.cmb_flow_port.blockSignals(False)

    def rebuild_table(self):
        d = self.json_data or {}
        ports = d.get("ports", [])
        self.table.blockSignals(True)
        self.table.setRowCount(3)
        for r in range(3):
            p = ports[r] if r < len(ports) else {}
            vals = [p.get("id", f"P{r+1}"), p.get("role", ""),
                    fmt(p.get("center", [0,0])[0]) if p else "", fmt(p.get("center", [0,0])[1]) if p else "",
                    fmt(p.get("angle_deg", 0)) if p else "", "OK" if p.get("cut_point") else ""]
            for c,v in enumerate(vals):
                self.table.setItem(r,c,QTableWidgetItem(str(v)))
        self.table.blockSignals(False)

    def redraw(self):
        if self.json_data:
            self.ensure_json_ports(force_rebuild=False)
        self.update_port_buttons()
        self.canvas.draw(self.geo, self.json_data, active_ports=self.current_port_count(), show_test=self.chk_show_test.isChecked())

    def auto_detect(self):
        if not self.current_path: return
        pc = detect_port_count(self.geo)[0]
        self.json_data = build_nevis_json(self.current_path, self.geo, pc, manual_port_count=False, flow_model=self.flow_model())
        self.load_meta_to_ui(); self.redraw(); self.mark_dirty(True)
        c = self.json_data.get("center")
        self.log_msg(f"Auto lt49: center=({fmt(c[0])},{fmt(c[1])}), port={pc}, source={self.json_data.get('center_source')}")


    def toggle_delete_entity_mode(self):
        """Toggle continuous delete mode for library drawing entities.

        Right-click deletes the nearest line/arc/circle. Press the same button again
        to finish deleting and return to normal view mode.
        """
        if self.mode == "delete_entity":
            self.mode = "view"
            self.btn_delete_entity.setText("Xóa nét")
            self.btn_delete_entity.setStyleSheet("")
            self.log_msg("Đã kết thúc chế độ xóa nét.")
        else:
            self.mode = "delete_entity"
            self.pending_line_start = None
            self.btn_delete_entity.setText("Kết thúc xóa")
            self.btn_delete_entity.setStyleSheet("font-weight:700; color:#B00020; background:#FFE1E1; border:1px solid #D33;")
            self.log_msg("Chế độ xóa nét: chuột phải vào line/cung muốn xóa. Có thể xóa liên tiếp, bấm 'Kết thúc xóa' để thoát.")

    def _delete_entity_near(self, x: float, y: float) -> bool:
        """Delete nearest visible entity around a picked point in TXT coordinates."""
        pnt = (x, y)
        best = None
        best_d = 1e100
        # tolerance in drawing units; snap already puts user near a real entity, but keep it modest
        scale = max(abs(self.canvas.transform().m11()), 1e-6)
        tol = max(1.0, 16.0 / scale)

        for seg in list(self.geo.segments):
            cp = closest_point_on_segment(pnt, seg.p1, seg.p2)
            d = dist(pnt, cp)
            # give centerlines a small priority because accidental centerline repair often needs deletion
            if seg.lt == CENTER_LT:
                d *= 0.85
            if d < best_d:
                best_d = d
                best = ("segment", seg)

        for cir in list(self.geo.circles):
            # circle/arc distance, good enough for deletion because user clicks visible curve
            dcen = math.hypot(x - cir.cx, y - cir.cy)
            d = abs(dcen - cir.r)
            if d < best_d:
                best_d = d
                best = ("circle", cir)

        if best is None or best_d > tol:
            self.log_msg("Không bắt được nét gần điểm bấm. Hãy bấm sát line/cung hơn.")
            return False

        kind, ent = best
        try:
            if kind == "segment":
                self.geo.segments.remove(ent)
                msg = f"Đã xóa line lt{ent.lt}: ({fmt(ent.x1)},{fmt(ent.y1)}) → ({fmt(ent.x2)},{fmt(ent.y2)})"
            else:
                self.geo.circles.remove(ent)
                msg = f"Đã xóa ci lt{ent.lt}: tâm ({fmt(ent.cx)},{fmt(ent.cy)}), r={fmt(ent.r)}"
        except ValueError:
            return False

        if 0 <= ent.index < len(self.geo.raw_lines):
            self.geo.raw_lines[ent.index] = ""

        pc = self.current_port_count()
        # Rebuild JSON from edited geometry, keep chosen port count and flow mode.
        self.json_data = build_nevis_json(
            self.current_path or Path(self.ed_name.text() or "library"),
            self.geo, pc,
            manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"),
            flow_model=self.flow_model()
        )
        assign_roles_to_json_ports(self.json_data)
        self.json_data["name_rule"] = name_rule_from_name(self.json_data.get("name") or (self.current_path.stem if self.current_path else ""))
        self.json_data["port_convention_status"] = port_convention_status(self.json_data)
        self.json_data["name_rule_status"] = name_rule_status(self.json_data)
        self.load_meta_to_ui()
        self.redraw()
        self.mark_dirty(True)
        self.log_msg(msg)
        return True


    def _selected_draw_lt(self) -> str:
        """Return selected line type for manual drawing."""
        if hasattr(self, "cmb_draw_lt") and "49" in self.cmb_draw_lt.currentText():
            return CENTER_LT
        return SOLID_LT

    def toggle_draw_line_mode(self):
        if self.mode == "draw_line":
            self.mode = "view"
            self.pending_line_start = None
            self.btn_draw_line.setText("Vẽ Line H")
            self.btn_draw_line.setStyleSheet("")
            self.log_msg("Đã kết thúc chế độ vẽ Line.")
        else:
            self.mode = "draw_line"
            self.pending_line_start = None
            self.btn_draw_line.setText("Đang vẽ Line...")
            self.btn_draw_line.setStyleSheet("font-weight:700; color:#0B5CAD; background:#D9ECFF; border:1px solid #2F80C9;")
            self.log_msg("Vẽ Line: chuột phải điểm đầu, chuột phải điểm cuối. Snap ưu tiên: giao điểm → đầu mút → trung điểm → điểm trên nét.")

    def toggle_draw_centerline_mode(self):
        """Backward compatible shortcut: switch draw type to lt49 and draw a line."""
        if hasattr(self, "cmb_draw_lt"):
            self.cmb_draw_lt.setCurrentText("Tim ống lt49")
        self.toggle_draw_line_mode()

    def toggle_draw_circle_mode(self):
        if self.mode == "draw_circle":
            self.mode = "view"
            self.pending_circle_center = None
            self.btn_draw_circle.setText("Vẽ tròn E")
            self.btn_draw_circle.setStyleSheet("")
            self.log_msg("Đã kết thúc chế độ vẽ đường tròn.")
        else:
            self.mode = "draw_circle"
            self.pending_line_start = None
            self.pending_circle_center = None
            self.btn_draw_circle.setText("Đang vẽ tròn...")
            self.btn_draw_circle.setStyleSheet("font-weight:700; color:#0B5CAD; background:#D9ECFF; border:1px solid #2F80C9;")
            self.log_msg("Vẽ tròn: chuột phải chọn tâm, chuột phải chọn điểm bán kính. Tâm/bán kính đều snap vào điểm thật.")

    def delete_last_centerline(self):
        cls = [s for s in self.geo.segments if s.lt == CENTER_LT]
        if not cls:
            self.log_msg("Không có tim lt49 để xóa.")
            return
        last = cls[-1]
        try:
            self.geo.segments.remove(last)
        except ValueError:
            return
        # remove raw line if possible
        if 0 <= last.index < len(self.geo.raw_lines):
            self.geo.raw_lines[last.index] = ""
        self.json_data = build_nevis_json(self.current_path or Path(self.ed_name.text() or "library"), self.geo, self.current_port_count(), manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"), flow_model=self.flow_model())
        self.ensure_port_slots()
        self.load_meta_to_ui(); self.redraw(); self.mark_dirty(True)
        self.log_msg("Đã xóa tim lt49 cuối cùng.")

    def _rebuild_json_after_geometry_edit(self, message: str = "Đã cập nhật hình học."):
        pc = self.current_port_count()
        self.json_data = build_nevis_json(
            self.current_path or Path(self.ed_name.text() or "library"),
            self.geo, pc,
            manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"),
            flow_model=self.flow_model()
        )
        self.ensure_port_slots()
        assign_roles_to_json_ports(self.json_data)
        self.json_data["port_convention_status"] = port_convention_status(self.json_data)
        self.load_meta_to_ui(); self.redraw(); self.mark_dirty(True)
        self.log_msg(message)

    def add_manual_line_segment(self, a: Tuple[float,float], b: Tuple[float,float], lt: Optional[str] = None):
        if dist(a, b) < 1e-6:
            self.log_msg("Đoạn line quá ngắn, bỏ qua.")
            return
        lt = lt or self._selected_draw_lt()
        self.geo.raw_lines.append(f"lt{lt}")
        self.geo.raw_lines.append(f" {fmt(a[0])} {fmt(a[1])} {fmt(b[0])} {fmt(b[1])}")
        seg = Segment(a[0], a[1], b[0], b[1], lt=lt, lc="", ly="", raw=self.geo.raw_lines[-1], index=len(self.geo.raw_lines)-1)
        self.geo.segments.append(seg)
        label = "tim ống lt49" if lt == CENTER_LT else "nét vỏ lt1"
        self._rebuild_json_after_geometry_edit(f"Đã thêm {label}: ({fmt(a[0])},{fmt(a[1])}) → ({fmt(b[0])},{fmt(b[1])})")

    def add_manual_circle(self, center: Tuple[float,float], radius_point: Tuple[float,float]):
        r = dist(center, radius_point)
        if r < 1e-6:
            self.log_msg("Bán kính quá nhỏ, bỏ qua.")
            return
        # Circle belongs to solid outline by default. Centerline circles are not useful for fitting ports.
        self.geo.raw_lines.append(f"lt{SOLID_LT}")
        self.geo.raw_lines.append(f"ci {fmt(center[0])} {fmt(center[1])} {fmt(r)}")
        cir = CircleArc(center[0], center[1], r, rest="", lt=SOLID_LT, lc="", ly="", raw=self.geo.raw_lines[-1], index=len(self.geo.raw_lines)-1)
        self.geo.circles.append(cir)
        self._rebuild_json_after_geometry_edit(f"Đã thêm đường tròn lt1: tâm ({fmt(center[0])},{fmt(center[1])}), r={fmt(r)}")

    def add_centerline_segment(self, a: Tuple[float,float], b: Tuple[float,float]):
        if dist(a, b) < 1e-6:
            self.log_msg("Đoạn tim quá ngắn, bỏ qua.")
            return
        # Append a clean lt49 block so JSON/raw_lines remain self-contained.
        start_idx = len(self.geo.raw_lines)
        self.geo.raw_lines.append("lt49")
        self.geo.raw_lines.append(f" {fmt(a[0])} {fmt(a[1])} {fmt(b[0])} {fmt(b[1])}")
        seg = Segment(a[0], a[1], b[0], b[1], lt=CENTER_LT, lc="", ly="", raw=self.geo.raw_lines[-1], index=start_idx+1)
        self.geo.segments.append(seg)
        # Rebuild JSON from new lt49, then keep manual port count if selected.
        pc = self.current_port_count()
        self.json_data = build_nevis_json(self.current_path or Path(self.ed_name.text() or "library"), self.geo, pc, manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"), flow_model=self.flow_model())
        self.ensure_port_slots()
        self.load_meta_to_ui(); self.redraw(); self.mark_dirty(True)
        self.log_msg(f"Đã thêm tim lt49: ({fmt(a[0])},{fmt(a[1])}) → ({fmt(b[0])},{fmt(b[1])})")

    def _bbox_for_geometry(self) -> Tuple[float, float, float, float]:
        pts = []
        for seg in self.geo.outlines or self.geo.segments:
            pts.extend([seg.p1, seg.p2])
        for c in self.geo.circles:
            pts.extend([(c.cx - c.r, c.cy - c.r), (c.cx + c.r, c.cy + c.r)])
        if not pts:
            return -100.0, -100.0, 100.0, 100.0
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def _ray_to_farthest_outline_or_bbox(self, center: Tuple[float, float], direction: Tuple[float, float]) -> Tuple[float, float]:
        dummy = Port(id="TMP", center=center, direction=norm_vec(direction[0], direction[1]))
        cp = point_on_outline_for_port(self.geo, center, dummy)
        if cp is not None:
            return cp
        # fallback: intersect with bounding box in that direction
        x0, y0 = center; ux, uy = dummy.direction
        xmin, ymin, xmax, ymax = self._bbox_for_geometry()
        ts = []
        if abs(ux) > 1e-9:
            ts += [(xmin - x0) / ux, (xmax - x0) / ux]
        if abs(uy) > 1e-9:
            ts += [(ymin - y0) / uy, (ymax - y0) / uy]
        ts = [t for t in ts if t > 1e-6]
        if not ts:
            return (x0 + ux * 50.0, y0 + uy * 50.0)
        t = min(ts)
        return (x0 + ux * t, y0 + uy * t)

    def auto_create_centerlines(self):
        """Create lt49 centerlines from current port count when a TXT has no centerlines.

        This is a fast repair tool, not a final authority.  It uses the current
        fitting center and creates rays to the farthest outline/bbox in standard
        directions.  The operator can then drag/replace P1-P3 if needed.
        """
        if not self.current_path and not self.json_data:
            return
        pc = self.current_port_count()
        center = tuple((self.json_data or {}).get("center", [0.0, 0.0])[:2]) if self.json_data else (0.0, 0.0)
        ftype = (self.ed_type.text().strip() or (self.json_data or {}).get("type", "")).upper()
        # Default directions: 3-port DT/T uses vertical main + right branch;
        # 2-port 45 uses down + 45deg; otherwise opposite main.
        if pc == 1:
            dirs = [(0.0, -1.0)]
        elif pc == 2:
            shape = self.two_port_shape()
            if "Vuông" in shape:
                dirs = [(0.0, -1.0), (1.0, 0.0)]
            elif "45" in shape:
                dirs = [(0.0, -1.0), (1.0, -1.0)]
            elif "135" in shape:
                dirs = [(0.0, -1.0), (1.0, 1.0)]
            elif "Thẳng" in shape:
                dirs = [(0.0, -1.0), (0.0, 1.0)]
            elif "45" in ftype or ftype == "4":
                dirs = [(0.0, -1.0), (1.0, 1.0)]
            elif ftype in ("LL", "DL", "90"):
                dirs = [(0.0, -1.0), (1.0, 0.0)]
            else:
                dirs = [(0.0, -1.0), (0.0, 1.0)]
        else:
            # 3 cửa: P1-P2 là tuyến chính thẳng hàng; P3 là nhánh phụ.
            # Kiểu 3 cửa chỉ quyết định góc nhánh phụ để tự sinh lt49 khi thiếu tim.
            shape3 = self.three_port_shape() if hasattr(self, 'three_port_shape') else "Auto"
            dirs = [(0.0, 1.0), (0.0, -1.0)]
            if "45" in shape3:
                dirs.append((1.0, 1.0))
            elif "135" in shape3:
                dirs.append((1.0, -1.0))
            elif "90" in shape3:
                dirs.append((1.0, 0.0))
            elif ftype == "Y":
                dirs.append((1.0, 1.0))
            else:
                dirs.append((1.0, 0.0))
        # Remove old auto-created lt49 only if there are no useful centerlines.
        if len(self.geo.centerlines) == 0:
            self.geo.raw_lines.append("lt49")
        for d in dirs:
            end = self._ray_to_farthest_outline_or_bbox(center, d)
            self.geo.raw_lines.append(f" {fmt(center[0])} {fmt(center[1])} {fmt(end[0])} {fmt(end[1])}")
            self.geo.segments.append(Segment(center[0], center[1], end[0], end[1], lt=CENTER_LT, lc="", ly="", raw=self.geo.raw_lines[-1], index=len(self.geo.raw_lines)-1))
        self.json_data = build_nevis_json(self.current_path or Path(self.ed_name.text() or "library"), self.geo, pc, manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"), flow_model=self.flow_model())
        if pc == 2:
            self.json_data["two_port_shape"] = self.two_port_shape()
        if pc == 3:
            self.json_data["three_port_shape"] = self.three_port_shape()
            self.json_data["expected_branch_angle_rule"] = self.three_port_shape()
        assign_roles_to_json_ports(self.json_data)
        self.json_data["port_convention_status"] = port_convention_status(self.json_data)
        self.load_meta_to_ui(); self.redraw(); self.mark_dirty(True)
        self.log_msg(f"Đã tự tạo {pc} tim lt49 theo số cửa đang chọn. Hãy kiểm tra P1/P2/P3 trước khi lưu.")

    def toggle_center_mode(self):
        if self.mode == "set_center":
            if self.pending_center and self.json_data:
                self.json_data["center"] = [self.pending_center[0], self.pending_center[1]]
                self.json_data["center_source"] = "manual_snap"
                pc = self.current_port_count()
                # Rebuild ports using manual center
                ports = infer_ports(self.geo, self.pending_center, pc)
                for p in ports:
                    cp = point_on_outline_for_port(self.geo, self.pending_center, p)
                    if cp is not None:
                        p.cut_point = cp
                        p.center = cp
                        p.centerline = (self.pending_center, cp)
                self.json_data["ports"] = [
                    {
                        "id": p.id, "role": p.role,
                        "center": [p.center[0], p.center[1]],
                        "direction": [p.direction[0], p.direction[1]],
                        "angle_deg": p.angle,
                        "centerline": [[p.centerline[0][0], p.centerline[0][1]], [p.centerline[1][0], p.centerline[1][1]]],
                        "cut_point": None if p.cut_point is None else [p.cut_point[0], p.cut_point[1]],
                        "source": "manual_center_lt49",
                        "confidence": p.confidence
                    } for p in ports
                ]
                self.json_data["center"] = [self.pending_center[0], self.pending_center[1]]
                self.json_data["center_source"] = "manual_snap"
            self.mode = "view"; self.btn_center.setText("Đặt tâm"); self.pending_center = None
            self.rebuild_table(); self.redraw(); self.mark_dirty(True); self.log_msg("Đã xác nhận tâm.")
        else:
            self.mode = "set_center"; self.btn_center.setText("Xác nhận tâm")
            self.log_msg("Chuột phải vào giao tim/mép thật để chọn tâm, rồi bấm Xác nhận tâm.")

    def set_port_mode(self, idx: int):
        self.mode = f"set_port_{idx}"; self.log_msg(f"Chuột phải vào điểm cửa/cắt mép thật để đặt P{idx+1}.")

    def point_picked(self, x: float, y: float):
        if not self.json_data: return
        if self.mode == "delete_entity":
            self._delete_entity_near(x, y)
            return
        if self.mode == "draw_line":
            if self.pending_line_start is None:
                self.pending_line_start = (x, y)
                lt_label = "tim ống lt49" if self._selected_draw_lt() == CENTER_LT else "nét vỏ lt1"
                self.log_msg(f"Điểm đầu {lt_label}: {fmt(x)}, {fmt(y)}. Chọn điểm cuối.")
            else:
                a = self.pending_line_start
                self.pending_line_start = None
                self.add_manual_line_segment(a, (x, y), self._selected_draw_lt())
            return
        if self.mode == "draw_circle":
            if getattr(self, "pending_circle_center", None) is None:
                self.pending_circle_center = (x, y)
                self.log_msg(f"Tâm tròn: {fmt(x)}, {fmt(y)}. Chọn điểm bán kính.")
            else:
                c = self.pending_circle_center
                self.pending_circle_center = None
                self.add_manual_circle(c, (x, y))
            return
        if self.mode == "set_center":
            self.pending_center = (x,y)
            self.log_msg(f"Tâm tạm: {fmt(x)}, {fmt(y)}. Bấm Xác nhận tâm để lưu.")
            d = dict(self.json_data); d["center"] = [x,y]
            self.canvas.draw(self.geo, d, self.current_port_count(), self.chk_show_test.isChecked())
            return
        if self.mode.startswith("set_port_"):
            idx = int(self.mode.rsplit("_",1)[1])
            self.ensure_port_slots()
            ports = self.json_data.setdefault("ports", [])
            while len(ports) <= idx:
                ports.append(self._empty_port_dict(len(ports)))
            cx, cy = self.json_data.get("center", [0,0])[:2]
            ux, uy = norm_vec(x-cx, y-cy)
            role = ports[idx].get("role") or (["main_1","main_2","branch"][idx] if self.current_port_count()==3 and idx<3 else "manual")
            ports[idx].update({"id": f"P{idx+1}", "role":role, "center":[x,y], "direction":[ux,uy], "angle_deg":angle_deg((ux,uy)), "centerline":[self.json_data.get("center", [0,0])[:2], [x,y]], "cut_point":[x,y], "source":"manual_snap", "confidence":1.0})
            self.mode = "view"
            assign_roles_to_json_ports(self.json_data)
            self.json_data["port_convention_status"] = port_convention_status(self.json_data)
            self.rebuild_table(); self.redraw(); self.mark_dirty(True); self.log_msg(f"Đã đặt P{idx+1}: {fmt(x)}, {fmt(y)}")


    def _rotate_point_about(self, p: Tuple[float, float], center: Tuple[float, float], deg: float) -> Tuple[float, float]:
        a = math.radians(deg)
        ca, sa = math.cos(a), math.sin(a)
        x, y = p[0] - center[0], p[1] - center[1]
        return (center[0] + x * ca - y * sa, center[1] + x * sa + y * ca)

    def _rotate_ci_rest(self, rest: str, deg: float) -> str:
        nums = re.findall(NUM, rest or "")
        if len(nums) < 2:
            return rest or ""
        try:
            a1 = float(nums[0]) + deg
            a2 = float(nums[1]) + deg
            tail = nums[2:]
            parts = [fmt(a1), fmt(a2)] + [fmt(float(x)) for x in tail]
            return " " + " ".join(parts)
        except Exception:
            return rest or ""

    def _refresh_json_geometry_from_geo_keep_meta(self):
        if not self.current_path:
            base = Path(self.ed_name.text() or "library")
        else:
            base = self.current_path
        old = self.json_data or {}
        pc = self.current_port_count()
        new_data = build_nevis_json(
            base, self.geo, pc,
            manual_port_count=not self.cmb_port_count.currentText().startswith("Auto"),
            flow_model=self.flow_model()
        )
        for key in ("name", "type", "size", "material", "flow", "manual_approved"):
            if key in old:
                new_data[key] = old[key]
        # Preserve explicit flow port if user chose one.
        if isinstance(old.get("flow"), dict):
            new_data["flow"] = dict(old.get("flow", {}))
        self.json_data = new_data
        self.ensure_port_slots()
        assign_roles_to_json_ports(self.json_data)
        self.json_data["port_convention_status"] = port_convention_status(self.json_data)
        self.json_data["name_rule"] = name_rule_from_name(self.ed_name.text().strip() or (base.stem if base else ""))
        self.json_data["name_rule_status"] = name_rule_status(self.json_data)

    def rotate_current_45_clockwise(self):
        """Space key: rotate the fitting 45 degrees clockwise around current fitting center."""
        if not self.json_data or not self.geo:
            return
        try:
            c = self.json_data.get("center", [0, 0])
            center = (float(c[0]), float(c[1]))
        except Exception:
            center = (0.0, 0.0)
        deg = -45.0  # clockwise in the TXT coordinate system
        # Rotate segments and update raw line records in place.
        for seg in self.geo.segments:
            p1 = self._rotate_point_about(seg.p1, center, deg)
            p2 = self._rotate_point_about(seg.p2, center, deg)
            seg.x1, seg.y1, seg.x2, seg.y2 = p1[0], p1[1], p2[0], p2[1]
            seg.raw = f" {fmt(seg.x1)} {fmt(seg.y1)} {fmt(seg.x2)} {fmt(seg.y2)}"
            if 0 <= seg.index < len(self.geo.raw_lines):
                self.geo.raw_lines[seg.index] = seg.raw
        # Rotate circle/arc centers. Arc angle records are also rotated when available.
        for cir in self.geo.circles:
            cp = self._rotate_point_about((cir.cx, cir.cy), center, deg)
            cir.cx, cir.cy = cp[0], cp[1]
            cir.rest = self._rotate_ci_rest(cir.rest, deg)
            cir.raw = f"ci {fmt(cir.cx)} {fmt(cir.cy)} {fmt(cir.r)}{cir.rest}"
            if 0 <= cir.index < len(self.geo.raw_lines):
                self.geo.raw_lines[cir.index] = cir.raw
        # This is a manual geometry transform, so previous manual approval is no longer valid.
        if isinstance(self.json_data.get("manual_approved"), dict):
            self.json_data["manual_approved"]["approved"] = False
        self._refresh_json_geometry_from_geo_keep_meta()
        self.load_meta_to_ui()
        self.redraw()
        self.mark_dirty(True)
        self.log_msg(f"Đã xoay cút 45° theo chiều kim đồng hồ quanh tâm ({fmt(center[0])}, {fmt(center[1])}). Bấm Space để xoay tiếp.")

    def approve_current_library(self):
        """Manual final approval: raise QA confidence after the operator checks the library."""
        if not self.json_data:
            return
        self.apply_ui_to_json()
        self.json_data["manual_approved"] = {
            "approved": True,
            "note": "User manually verified this library in NEVIS Library Editor",
        }
        self.json_data.setdefault("auto_detect", {})["center_confidence"] = 1.0
        self.json_data.setdefault("auto_detect", {})["port_count_confidence"] = 1.0
        self.json_data.setdefault("auto_detect", {})["need_review"] = False
        self.update_qa_for_current_file(self.current_path)
        self.update_current_status_detail(self.current_path)
        self.refresh_files()
        self.mark_dirty(True)
        self.log_msg("Đã Đã kiểm tra: QA sẽ tính file này là đã kiểm tra thủ công. Hãy LƯU JSON để ghi vào file.")

    def apply_ui_to_json(self):
        if not self.json_data: return
        self.json_data["name"] = self.ed_name.text().strip()
        self.json_data["type"] = self.ed_type.text().strip()
        self.json_data["size"] = self.ed_size.text().strip()
        self.json_data["material"] = self.ed_mat.text().strip()
        self.json_data["port_count"] = self.current_port_count()
        if hasattr(self, 'cmb_2port_shape'):
            self.json_data["two_port_shape"] = self.two_port_shape()
        if hasattr(self, 'cmb_3port_shape'):
            self.json_data["three_port_shape"] = self.three_port_shape()
            self.json_data["expected_branch_angle_rule"] = self.three_port_shape()
        self.json_data["name_rule"] = name_rule_from_name(self.ed_name.text().strip() or (self.current_path.stem if self.current_path else ""))
        assign_roles_to_json_ports(self.json_data)
        self.json_data["port_convention_status"] = port_convention_status(self.json_data)
        self.json_data["name_rule_status"] = name_rule_status(self.json_data)
        self.json_data.setdefault("flow", {})["model"] = self.flow_model()
        if self.flow_model() == "collector":
            self.json_data["flow"]["port"] = None
        elif hasattr(self, 'cmb_flow_port') and self.cmb_flow_port.currentText() in ("P1", "P2", "P3"):
            self.json_data["flow"]["port"] = self.cmb_flow_port.currentText()
        else:
            self.json_data["flow"]["port"] = default_flow_port([Port(
                id=p.get("id", "P"), center=tuple(p.get("center", [0,0])),
                direction=tuple(p.get("direction", [1,0])), angle=float(p.get("angle_deg", 0))
            ) for p in self.json_data.get("ports", [])], self.flow_model())

    def save_json(self):
        if not self.current_path or not self.json_data: return
        self.apply_ui_to_json()
        out = self.current_path.with_suffix(".json") if self.current_path.suffix.lower() != ".json" else self.current_path

        # Before writing, refresh convention/QA-related metadata so the saved JSON
        # contains the latest manual edits, port count, port roles, flow and cut points.
        assign_roles_to_json_ports(self.json_data)
        self.json_data["port_convention_status"] = port_convention_status(self.json_data)
        self.json_data.setdefault("auto_detect", {})["need_review"] = bool(
            self.json_data.get("auto_detect", {}).get("need_review", False)
            or not self.json_data.get("port_convention_status", {}).get("ok", True)
        )

        out.write_text(json.dumps(self.json_data, ensure_ascii=False, indent=2), encoding="utf-8")

        # A saved TXT becomes an independent JSON library from this point.  Switch
        # the current target to the JSON and immediately re-run QA for this file.
        self.current_path = out
        self.update_qa_for_current_file(out)
        self.dirty = False
        self.update_save_button()
        self.refresh_files()
        self.update_current_status_detail(out)
        self.log_msg(f"Đã lưu JSON và cập nhật đánh giá: {out.name}")
        QMessageBox.information(self, "OK", f"Đã lưu và cập nhật đánh giá:\n{out}")

    def update_qa_for_current_file(self, path: Optional[Path] = None):
        """Recalculate QA after saving/editing the current library.

        This keeps the left file list color, the legend counts, and the status
        panel in sync immediately after the operator fixes a library.
        """
        if not self.json_data:
            return
        path = path or self.current_path
        if not path:
            return
        dup = str(path.resolve()) in getattr(self, 'duplicate_paths', set())
        qa = qa_analyze_data(path, self.geo, self.json_data, duplicate=dup)
        if not hasattr(self, 'qa_status_by_path') or self.qa_status_by_path is None:
            self.qa_status_by_path = {}
        self.qa_status_by_path[str(path.resolve())] = qa
        self.recalculate_qa_counts_from_cache()


    def visible_library_paths(self) -> List[Path]:
        """Return the exact files currently shown in the left list.

        All 4 process buttons work on this visible list.  To process a whole
        library, select the root folder and show all files first.
        """
        paths: List[Path] = []
        if not hasattr(self, 'listw'):
            return paths
        for i in range(self.listw.count()):
            item = self.listw.item(i)
            try:
                p = Path(item.data(Qt.UserRole))
                if p.exists() and p.suffix.lower() in ('.txt', '.json'):
                    paths.append(p)
            except Exception:
                pass
        return paths

    def _unique_libraries_from_paths(self, paths: List[Path]) -> List[Path]:
        """Prefer TXT when TXT/JSON with the same name are both visible."""
        out: List[Path] = []
        seen_json = set()
        for p in sorted(paths, key=lambda x: (str(x.with_suffix('')).lower(), x.suffix.lower())):
            if p.suffix.lower() == '.txt':
                out.append(p)
                seen_json.add(str(p.with_suffix('.json').resolve()))
        for p in sorted(paths, key=lambda x: str(x).lower()):
            if p.suffix.lower() == '.json' and str(p.resolve()) not in seen_json:
                out.append(p)
        return out

    def auto_complete_visible_libraries(self):
        """Step ②: auto-complete every currently visible library and save JSON."""
        libs = self._unique_libraries_from_paths(self.visible_library_paths())
        if not libs:
            QMessageBox.information(self, "② Tự động hoàn thiện", "Không có TXT/JSON nào đang hiển thị để xử lý.")
            return
        ret = QMessageBox.question(
            self, "② Tự động hoàn thiện",
            f"Sẽ tự tạo/cập nhật tim ống lt49, P1/P2/P3, flow và tự lưu JSON cho {len(libs)} file đang hiển thị.\n\nTiếp tục?"
        )
        if ret != QMessageBox.Yes:
            return
        ok = warn = err = 0
        for p in libs:
            try:
                old_data: Dict[str, Any] = {}
                if p.suffix.lower() == '.json':
                    old_data = json.loads(p.read_text(encoding='utf-8-sig'))
                    geo = geometry_from_json_data(old_data)
                    out = p
                else:
                    geo = parse_txt(p)
                    out = p.with_suffix('.json')
                    if out.exists():
                        try:
                            old_data = json.loads(out.read_text(encoding='utf-8-sig'))
                        except Exception:
                            old_data = {}
                new_geo, data = self._auto_create_centerlines_for_geometry(out if out.suffix.lower()=='.json' else p, geo, old_data)
                # Do not create .bak by default to keep the official library clean.
                # The old .bak files can be removed by step ④.
                out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                qa = qa_analyze_data(out, new_geo, data, duplicate=str(out.resolve()) in getattr(self, 'duplicate_paths', set()))
                self.qa_status_by_path[str(out.resolve())] = qa
                status = qa.get('status')
                if status == 'ok': ok += 1
                elif status == 'error': err += 1
                else: warn += 1
            except Exception as e:
                err += 1
                self.log_msg(f"ERR ② tự động hoàn thiện {p.name}: {e}")
        self.recalculate_qa_counts_from_cache()
        self.refresh_files()
        self.update_current_status_detail(self.current_path)
        self.log_msg(f"② Tự động hoàn thiện: OK {ok}, cần kiểm tra {warn}, lỗi {err}")
        QMessageBox.information(self, "② Tự động hoàn thiện", f"OK: {ok}\nCần kiểm tra: {warn}\nLỗi: {err}")

    def _scan_duplicates_for_paths(self, paths: List[Path]) -> Tuple[set, List[str], int]:
        groups: Dict[str, List[Path]] = {}
        errors: List[str] = []
        for fp in paths:
            try:
                if fp.suffix.lower() == '.json':
                    data = json.loads(fp.read_text(encoding='utf-8-sig'))
                    sig = 'json:' + json_duplicate_signature(data)
                elif fp.suffix.lower() == '.txt':
                    sig = 'txt:' + txt_duplicate_signature(fp)
                else:
                    continue
                groups.setdefault(sig, []).append(fp)
            except Exception as e:
                errors.append(f'{fp.name}: {e}')
        dups = [lst for lst in groups.values() if len(lst) >= 2]
        dup_paths = {str(fp.resolve()) for lst in dups for fp in lst}
        return dup_paths, errors, len(dups)

    def check_visible_libraries(self, silent: bool = False):
        """Step ③: check duplicate + QA for the exact files currently visible."""
        paths = self.visible_library_paths()
        if not paths:
            if not silent:
                QMessageBox.information(self, '③ Kiểm tra thư viện', 'Không có TXT/JSON nào đang hiển thị.')
            return
        dup_paths, dup_errors, dup_group_count = self._scan_duplicates_for_paths(paths)
        # Keep duplicate marks only for this checked scope.
        self.duplicate_paths = dup_paths
        self.qa_status_by_path = {}
        counts = {"ok":0, "warn":0, "error":0, "unprocessed":0}
        for p in paths:
            qa = qa_analyze_path(p, duplicate=str(p.resolve()) in dup_paths)
            self.qa_status_by_path[str(p.resolve())] = qa
            counts[qa.get('status', 'error')] = counts.get(qa.get('status','error'), 0) + 1
        self.qa_counts = counts
        self.refresh_files()
        self.update_current_status_detail(self.current_path)
        self.log_msg(
            f"③ Kiểm tra thư viện: OK {counts['ok']} | Cần kiểm tra {counts['warn']} | "
            f"Lỗi {counts['error']} | Trùng {len(dup_paths)} file/{dup_group_count} nhóm"
        )
        if not silent:
            extra = f"\nFile trùng: {len(dup_paths)} ({dup_group_count} nhóm)"
            if dup_errors:
                extra += f"\nLỗi đọc khi kiểm trùng: {len(dup_errors)}"
            QMessageBox.information(
                self, '③ Kiểm tra thư viện',
                f"Tổng file đang hiển thị: {len(paths)}\nOK: {counts['ok']}\nCần kiểm tra: {counts['warn']}\nLỗi: {counts['error']}{extra}"
            )

    def clean_visible_library_files(self):
        """Step ④: clean only the current visible/current-folder working area."""
        visible = self.visible_library_paths()
        txts = [p for p in visible if p.suffix.lower() == '.txt' and p.with_suffix('.json').exists()]
        missing_json = [p for p in visible if p.suffix.lower() == '.txt' and not p.with_suffix('.json').exists()]
        bak_files = sorted(self.active_folder().glob('*.bak')) + sorted(self.active_folder().glob('*.json.bak'))
        # Remove duplicates while preserving order.
        seen = set(); bak_unique = []
        for p in bak_files:
            key = str(p.resolve())
            if key not in seen:
                seen.add(key); bak_unique.append(p)
        if not txts and not bak_unique:
            msg = "Không có TXT đã có JSON hoặc file .bak để dọn trong phạm vi hiện tại."
            if missing_json:
                msg += f"\n\nCó {len(missing_json)} TXT chưa có JSON nên được giữ lại."
            QMessageBox.information(self, "④ Dọn thư viện", msg)
            return
        warn = f"\n\n⚠ {len(missing_json)} TXT chưa có JSON sẽ được giữ lại." if missing_json else ""
        ret = QMessageBox.question(
            self, "④ Dọn thư viện",
            f"Sẽ xóa hẳn:\n- TXT đã có JSON: {len(txts)} file\n- Backup .bak trong folder đang chọn: {len(bak_unique)} file{warn}\n\nTiếp tục?"
        )
        if ret != QMessageBox.Yes:
            return
        ok_txt = ok_bak = err = 0
        for fp in txts:
            try:
                fp.unlink(); ok_txt += 1
            except Exception as e:
                err += 1; self.log_msg(f"ERR xóa TXT {fp.name}: {e}")
        for fp in bak_unique:
            try:
                fp.unlink(); ok_bak += 1
            except Exception as e:
                err += 1; self.log_msg(f"ERR xóa BAK {fp.name}: {e}")
        self.refresh_files()
        self.log_msg(f"④ Dọn thư viện: xóa TXT {ok_txt}, xóa BAK {ok_bak}, giữ TXT chưa có JSON {len(missing_json)}, lỗi {err}")
        QMessageBox.information(self, "④ Dọn thư viện", f"Đã xóa TXT: {ok_txt}\nĐã xóa BAK: {ok_bak}\nGiữ TXT chưa có JSON: {len(missing_json)}\nLỗi: {err}")

    def recalculate_qa_counts_from_cache(self):
        counts = {"ok": 0, "warn": 0, "error": 0, "unprocessed": 0}
        try:
            paths = sorted(list(self.root.rglob('*.txt')) + list(self.root.rglob('*.json')), key=lambda p: str(p).lower())
        except Exception:
            paths = []
        cache = getattr(self, 'qa_status_by_path', {}) or {}
        dup_set = getattr(self, 'duplicate_paths', set())
        for p in paths:
            key = str(p.resolve())
            qa = cache.get(key)
            status = qa.get('status') if qa else 'unprocessed'
            if key in dup_set and status not in ('error',):
                status = 'warn'
            counts[status] = counts.get(status, 0) + 1
        self.qa_counts = counts
        self.update_qa_legend()

    def batch_convert(self):
        base = self.active_folder()
        files = sorted(base.glob("*.txt"))
        if not files:
            QMessageBox.information(self, "NEVIS", "Không có TXT trong thư mục."); return
        ok = warn = err = 0
        for p in files:
            try:
                geo = parse_txt(p)
                data = build_nevis_json(p, geo)
                p.with_suffix(".json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                if data.get("auto_detect",{}).get("need_review"): warn += 1
                else: ok += 1
            except Exception as e:
                err += 1; self.log_msg(f"ERR {p.name}: {e}")
        self.refresh_files()
        QMessageBox.information(self, "Batch TXT → JSON", f"OK: {ok}\nCần kiểm tra: {warn}\nLỗi: {err}")

    def delete_txt_with_json(self):
        base = self.active_folder()
        all_txt = sorted(base.glob("*.txt"))
        txts = [p for p in all_txt if p.with_suffix(".json").exists()]
        missing = [p for p in all_txt if not p.with_suffix(".json").exists()]
        if not txts:
            msg = "Không có TXT nào đã có JSON cùng tên trong folder đang chọn."
            if missing:
                msg += f"\n\nCó {len(missing)} TXT chưa có JSON nên không được xóa."
            QMessageBox.information(self, "NEVIS", msg)
            return
        warn = f"\n\n⚠ {len(missing)} TXT chưa có JSON sẽ được giữ lại." if missing else ""
        ret = QMessageBox.question(self, "Xóa TXT an toàn", f"Sẽ XÓA HẲN {len(txts)} TXT đã có JSON cùng tên trong folder đang chọn.{warn}\n\nTiếp tục?")
        if ret != QMessageBox.Yes:
            return
        ok = err = 0
        for p in txts:
            try:
                p.unlink()
                ok += 1
            except Exception as e:
                err += 1
                self.log_msg(f"ERR xóa TXT {p.name}: {e}")
        self.refresh_files()
        self.log_msg(f"Đã xóa hẳn {ok} TXT đã có JSON. Giữ lại {len(missing)} TXT chưa có JSON. Lỗi {err}.")
        QMessageBox.information(self, "Xóa TXT an toàn", f"Đã xóa: {ok}\nGiữ lại vì chưa có JSON: {len(missing)}\nLỗi: {err}")

    def batch_apply_port_count(self):
        """Apply the selected port count to every library in the current folder and save JSON immediately."""
        txt = self.cmb_port_count.currentText() if hasattr(self, 'cmb_port_count') else "Auto"
        if txt.startswith("1"):
            pc = 1
        elif txt.startswith("2"):
            pc = 2
        elif txt.startswith("3"):
            pc = 3
        else:
            QMessageBox.warning(self, "NEVIS", "Hãy chọn rõ 1 cửa / 2 cửa / 3 cửa trước khi áp dụng folder.")
            return

        unique = []
        seen_json_from_txt = set()
        for f in sorted(self.active_folder().glob("*.txt")):
            unique.append(f)
            seen_json_from_txt.add(str(f.with_suffix(".json").resolve()))
        for f in sorted(self.active_folder().glob("*.json")):
            if str(f.resolve()) not in seen_json_from_txt:
                unique.append(f)
        if not unique:
            QMessageBox.information(self, "NEVIS", "Không có TXT/JSON trong thư mục.")
            return

        label = {1: "1 cửa", 2: "2 cửa", 3: "3 cửa"}[pc]
        ret = QMessageBox.question(
            self, "Áp dụng số cửa",
            f"Sẽ đặt toàn bộ {len(unique)} thư viện trong folder hiện tại thành {label} và tự lưu JSON.\n\nTiếp tục?"
        )
        if ret != QMessageBox.Yes:
            return

        ok = warn = err = 0
        for path in unique:
            try:
                old_data = {}
                if path.suffix.lower() == ".json":
                    old_data = json.loads(path.read_text(encoding="utf-8-sig"))
                    geo = geometry_from_json_data(old_data)
                    out = path
                else:
                    geo = parse_txt(path)
                    out = path.with_suffix(".json")
                    if out.exists():
                        try:
                            old_data = json.loads(out.read_text(encoding="utf-8-sig"))
                        except Exception:
                            old_data = {}

                flow_model = (old_data.get("flow", {}) or {}).get("model", self.flow_model()) if isinstance(old_data, dict) else self.flow_model()
                data = build_nevis_json(out if out.suffix.lower() == ".json" else path, geo, pc, manual_port_count=True, flow_model=flow_model)

                # Preserve user-entered metadata. Port count and ports are intentionally rebuilt.
                for key in ("material", "type", "size", "name"):
                    val = old_data.get(key) if isinstance(old_data, dict) else None
                    if val not in (None, ""):
                        data[key] = val
                data["port_count"] = pc
                if pc == 2 and hasattr(self, 'two_port_shape'):
                    data["two_port_shape"] = self.two_port_shape()
                if pc == 3 and hasattr(self, 'three_port_shape'):
                    data["three_port_shape"] = self.three_port_shape()
                    data["expected_branch_angle_rule"] = self.three_port_shape()
                data["port_count_source"] = "folder_manual"
                data["manual_override"] = True
                assign_roles_to_json_ports(data)
                data["port_convention_status"] = port_convention_status(data)
                out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                if data.get("auto_detect", {}).get("need_review") or not data.get("port_convention_status", {}).get("ok", True):
                    warn += 1
                else:
                    ok += 1
            except Exception as e:
                err += 1
                self.log_msg(f"ERR áp dụng số cửa {path.name}: {e}")

        if self.current_path:
            candidate = self.current_path if self.current_path.suffix.lower() == ".json" else self.current_path.with_suffix(".json")
            if candidate.exists():
                try:
                    self.open_file(candidate)
                except Exception:
                    pass
        self.refresh_files()
        self.log_msg(f"Áp dụng {label}: OK {ok}, cần kiểm tra {warn}, lỗi {err}")
        QMessageBox.information(self, "Áp dụng số cửa", f"{label}\nOK: {ok}\nCần kiểm tra: {warn}\nLỗi: {err}")


    def _filter_raw_lines_without_centerlines(self, raw_lines: List[str]) -> List[str]:
        """Remove existing lt49 geometry from raw lines before regenerating centerlines.

        This avoids duplicated or contradictory centerlines when running batch auto-create.
        Non-centerline geometry and all layer/color records are preserved.
        """
        out: List[str] = []
        cur_lt = ""
        for line in raw_lines or []:
            m = LT_RE.match(str(line))
            if m:
                cur_lt = m.group(1)
                if cur_lt == CENTER_LT:
                    # Drop the lt49 command itself. A clean lt49 block is appended later.
                    continue
                out.append(str(line))
                continue
            if cur_lt == CENTER_LT and (LINE_RE.match(str(line)) or CI_RE.match(str(line))):
                continue
            out.append(str(line))
        return out

    def _directions_for_auto_centerlines(self, pc: int, ftype: str) -> List[Tuple[float, float]]:
        """Return standard centerline directions using current UI shape rules."""
        ftype = (ftype or "").upper()
        if pc == 1:
            return [(0.0, -1.0)]
        if pc == 2:
            shape = self.two_port_shape() if hasattr(self, 'two_port_shape') else "Auto"
            if "Vuông" in shape:
                return [(0.0, -1.0), (1.0, 0.0)]
            if "45" in shape:
                return [(0.0, -1.0), (1.0, -1.0)]
            if "135" in shape:
                return [(0.0, -1.0), (1.0, 1.0)]
            if "Thẳng" in shape:
                return [(0.0, -1.0), (0.0, 1.0)]
            if "45" in ftype or ftype == "4":
                return [(0.0, -1.0), (1.0, 1.0)]
            if ftype in ("LL", "DL", "90"):
                return [(0.0, -1.0), (1.0, 0.0)]
            return [(0.0, -1.0), (0.0, 1.0)]
        # 3 ports: P1-P2 is main line, P3 is branch.
        shape3 = self.three_port_shape() if hasattr(self, 'three_port_shape') else "Auto"
        dirs = [(0.0, 1.0), (0.0, -1.0)]
        if "45" in shape3:
            dirs.append((1.0, 1.0))
        elif "135" in shape3:
            dirs.append((1.0, -1.0))
        elif "90" in shape3:
            dirs.append((1.0, 0.0))
        elif ftype == "Y":
            dirs.append((1.0, 1.0))
        else:
            dirs.append((1.0, 0.0))
        return dirs

    def _auto_create_centerlines_for_geometry(self, path: Path, geo: Geometry, old_data: Optional[Dict[str, Any]] = None) -> Tuple[Geometry, Dict[str, Any]]:
        """Regenerate lt49 centerlines for one TXT/JSON library and return new geometry + JSON.

        The function uses the current UI settings for number of ports and 2/3-port shape.
        Existing non-centerline geometry is preserved. Old user metadata is preserved.
        """
        old_data = old_data if isinstance(old_data, dict) else {}
        pc = self.current_port_count()
        # If Auto is still selected, use filename rule/lt49 detection first.
        if hasattr(self, 'cmb_port_count') and self.cmb_port_count.currentText().startswith('Auto'):
            rule = name_rule_from_name(path.stem)
            pc = int(rule.get('expected_port_count') or detect_port_count(geo)[0] or 1)
            pc = max(1, min(3, pc))

        # Prefer existing/manual center; otherwise infer from old lt49; otherwise 0,0.
        center = (0.0, 0.0)
        if isinstance(old_data.get('center'), list) and len(old_data.get('center')) >= 2:
            center = (float(old_data['center'][0]), float(old_data['center'][1]))
        elif geo.centerlines:
            center = infer_center(geo.centerlines)[0]

        material, ftype, _size = infer_from_name(path.stem)
        if old_data.get('type'):
            ftype = str(old_data.get('type'))
        clean_lines = self._filter_raw_lines_without_centerlines(geo.raw_lines)
        new_geo = geometry_from_json_data({"geometry": {"raw_lines": clean_lines}})
        raw = clean_lines[:]
        raw.append("lt49")
        for d in self._directions_for_auto_centerlines(pc, ftype):
            # Temporarily use the new geometry so _ray_to_farthest_outline_or_bbox can find the mouth/cut point.
            old_geo = self.geo
            self.geo = new_geo
            try:
                end = self._ray_to_farthest_outline_or_bbox(center, d)
            finally:
                self.geo = old_geo
            raw.append(f" {fmt(center[0])} {fmt(center[1])} {fmt(end[0])} {fmt(end[1])}")
        new_geo = geometry_from_json_data({"geometry": {"raw_lines": raw}})

        flow_model = (old_data.get('flow', {}) or {}).get('model', self.flow_model()) if isinstance(old_data, dict) else self.flow_model()
        data = build_nevis_json(path, new_geo, pc, manual_port_count=not (hasattr(self, 'cmb_port_count') and self.cmb_port_count.currentText().startswith('Auto')), flow_model=flow_model)
        # Preserve user-entered metadata.
        for key in ("material", "type", "size", "name"):
            val = old_data.get(key)
            if val not in (None, ""):
                data[key] = val
        if pc == 2 and hasattr(self, 'two_port_shape'):
            data["two_port_shape"] = self.two_port_shape()
        if pc == 3 and hasattr(self, 'three_port_shape'):
            data["three_port_shape"] = self.three_port_shape()
            data["expected_branch_angle_rule"] = self.three_port_shape()
        data["center"] = [center[0], center[1]]
        data["center_source"] = old_data.get("center_source") or "batch_auto_centerline"
        data["centerline_generated"] = True
        data["centerline_generated_mode"] = "folder_batch"
        assign_roles_to_json_ports(data)
        data["port_convention_status"] = port_convention_status(data)
        data["name_rule_status"] = name_rule_status(data)
        return new_geo, data

    def _collect_libraries_for_batch(self, base: Path, recursive: bool = False) -> List[Path]:
        """Collect TXT/JSON libraries, preferring TXT when a TXT and JSON have the same basename."""
        pattern = '**/*' if recursive else '*'
        paths: List[Path] = []
        txts = sorted(base.glob(pattern + '.txt')) if recursive else sorted(base.glob('*.txt'))
        jsons = sorted(base.glob(pattern + '.json')) if recursive else sorted(base.glob('*.json'))
        seen_json = set()
        for p in txts:
            paths.append(p)
            seen_json.add(str(p.with_suffix('.json').resolve()))
        for p in jsons:
            if str(p.resolve()) not in seen_json:
                paths.append(p)
        return paths

    def _batch_auto_create_centerlines(self, base: Path, recursive: bool = False):
        libs = self._collect_libraries_for_batch(base, recursive=recursive)
        if not libs:
            QMessageBox.information(self, "NEVIS", "Không có TXT/JSON để tự tạo tim.")
            return
        scope = "toàn bộ thư viện" if recursive else "folder đang chọn"
        ret = QMessageBox.question(
            self, "Tự tạo tim hàng loạt",
            f"Sẽ tự tạo lại lt49 cho {len(libs)} thư viện trong {scope}, tự lưu JSON và QA lại.\n\nTiếp tục?"
        )
        if ret != QMessageBox.Yes:
            return
        ok = warn = err = 0
        for p in libs:
            try:
                old_data: Dict[str, Any] = {}
                if p.suffix.lower() == '.json':
                    old_data = json.loads(p.read_text(encoding='utf-8-sig'))
                    geo = geometry_from_json_data(old_data)
                    out = p
                else:
                    geo = parse_txt(p)
                    out = p.with_suffix('.json')
                    if out.exists():
                        try:
                            old_data = json.loads(out.read_text(encoding='utf-8-sig'))
                        except Exception:
                            old_data = {}
                new_geo, data = self._auto_create_centerlines_for_geometry(out if out.suffix.lower()=='.json' else p, geo, old_data)
                # Backup only existing JSON before overwriting.
                if out.exists():
                    bak = out.with_suffix(out.suffix + '.bak')
                    try:
                        shutil.copy2(out, bak)
                    except Exception:
                        pass
                out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
                qa = qa_analyze_data(out, new_geo, data, duplicate=str(out.resolve()) in getattr(self, 'duplicate_paths', set()))
                self.qa_status_by_path[str(out.resolve())] = qa
                if qa.get('status') == 'ok':
                    ok += 1
                elif qa.get('status') == 'error':
                    err += 1
                else:
                    warn += 1
            except Exception as e:
                err += 1
                self.log_msg(f"ERR tự tạo tim {p.name}: {e}")
        self.recalculate_qa_counts_from_cache()
        self.refresh_files()
        if self.current_path:
            candidate = self.current_path if self.current_path.suffix.lower()=='.json' else self.current_path.with_suffix('.json')
            if candidate.exists():
                try:
                    self.open_file(candidate)
                except Exception:
                    pass
        self.log_msg(f"Tự tạo tim {scope}: OK {ok}, cần kiểm tra {warn}, lỗi {err}")
        QMessageBox.information(self, "Tự tạo tim hàng loạt", f"OK: {ok}\nCần kiểm tra: {warn}\nLỗi: {err}")

    def batch_auto_create_centerlines_folder(self):
        self._batch_auto_create_centerlines(self.active_folder(), recursive=False)

    def batch_auto_create_centerlines_all(self):
        self._batch_auto_create_centerlines(self.root, recursive=True)

    def batch_apply_material(self):
        material = self.ed_mat.text().strip()
        if not material:
            QMessageBox.warning(self, "NEVIS", "Hãy nhập vật tư trước, ví dụ: DV / TMP / VP.")
            return
        files = sorted(self.active_folder().glob("*.json"))
        if not files:
            QMessageBox.information(self, "NEVIS", "Không có JSON trong thư mục.")
            return
        ret = QMessageBox.question(self, "Áp dụng vật tư", f"Ghi vật tư '{material}' cho {len(files)} JSON trong folder đang chọn?")
        if ret != QMessageBox.Yes:
            return
        ok = err = 0
        for p in files:
            try:
                data = json.loads(p.read_text(encoding="utf-8-sig"))
                data["material"] = material
                p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                ok += 1
            except Exception as e:
                err += 1
                self.log_msg(f"ERR material {p.name}: {e}")
        if self.json_data:
            self.json_data["material"] = material
        self.log_msg(f"Đã áp dụng vật tư {material}: OK {ok}, lỗi {err}")
        QMessageBox.information(self, "Áp dụng vật tư", f"OK: {ok}\nLỗi: {err}")
        self.refresh_files()

    def _selected_duplicate_formats(self) -> List[str]:
        if hasattr(self, 'rb_txt') and self.rb_txt.isChecked():
            return ['txt']
        if hasattr(self, 'rb_json') and self.rb_json.isChecked():
            return ['json']
        return ['txt', 'json']

    def check_duplicate_files(self):
        """Check duplicate TXT/JSON libraries inside the current folder.

        TXT files are compared with TXT files, and JSON files are compared with
        JSON files. Coordinates are rounded to 0.001 so tiny JWW floating noise
        does not hide copied libraries.
        """
        groups: Dict[str, List[Path]] = {}
        errors: List[str] = []
        formats = self._selected_duplicate_formats()
        paths: List[Path] = []
        if 'txt' in formats:
            paths += sorted(self.active_folder().glob('*.txt'))
        if 'json' in formats:
            paths += sorted(self.active_folder().glob('*.json'))
        if not paths:
            QMessageBox.information(self, 'Kiểm tra trùng', 'Không có file để kiểm tra.')
            return
        for fp in paths:
            try:
                if fp.suffix.lower() == '.json':
                    data = json.loads(fp.read_text(encoding='utf-8-sig'))
                    sig = 'json:' + json_duplicate_signature(data)
                else:
                    sig = 'txt:' + txt_duplicate_signature(fp)
                groups.setdefault(sig, []).append(fp)
            except Exception as e:
                errors.append(f'{fp.name}: {e}')
        dups = [lst for lst in groups.values() if len(lst) >= 2]
        self.duplicate_paths = {str(fp.resolve()) for lst in dups for fp in lst}
        if getattr(self, 'qa_status_by_path', None):
            self.check_all_libraries(silent=True)
        else:
            self.refresh_files()
        total_dup_files = sum(len(lst) for lst in dups)
        if not dups:
            self.log_msg(f'Kiểm tra trùng: không thấy trùng. Lỗi đọc: {len(errors)}')
            QMessageBox.information(self, 'Kiểm tra trùng', f'Không phát hiện file trùng.\nLỗi đọc: {len(errors)}')
            return
        self.log_msg('==== FILE TRÙNG / CẦN KIỂM TRA ====')
        for idx, lst in enumerate(dups, 1):
            names = ', '.join(str(x.relative_to(self.root)) for x in lst[:8])
            more = '' if len(lst) <= 8 else f' ... +{len(lst)-8}'
            self.log_msg(f'Nhóm {idx}: {names}{more}')
        if errors:
            self.log_msg('Lỗi đọc: ' + '; '.join(errors[:5]))
        QMessageBox.warning(self, 'Kiểm tra trùng', f'Phát hiện {len(dups)} nhóm trùng, tổng {total_dup_files} file.\nCác file trùng đã hiện màu đỏ trong danh sách.')

    def update_qa_legend(self):
        counts = getattr(self, 'qa_counts', {"ok":0,"warn":0,"error":0,"unprocessed":0})
        total = sum(counts.values())
        if not hasattr(self, 'qa_legend'):
            return
        self.qa_legend.setText(
            "<b>Chú thích trạng thái thư viện</b> &nbsp; "
            "<span style='background:#DAF5E2;border:1px solid #7BBF8A;padding:2px 6px;'>🟢 OK: {ok}</span> &nbsp; "
            "<span style='background:#FFEDCC;border:1px solid #E0AA46;padding:2px 6px;'>🟠 Cần kiểm tra: {warn}</span> &nbsp; "
            "<span style='background:#FFDADA;border:1px solid #D66A6A;padding:2px 6px;'>🔴 Lỗi: {error}</span> &nbsp; "
            "<span style='background:#EBEFF4;border:1px solid #AAB7C4;padding:2px 6px;'>⚪ Chưa xử lý: {unprocessed}</span> &nbsp; "
            "<b>Tổng:</b> {total}".format(total=total, **counts)
        )

    def update_current_status_detail(self, path: Optional[Path] = None):
        if not hasattr(self, 'status_detail'):
            return
        path = path or self.current_path
        if not path:
            self.status_detail.setText("Chưa mở file.")
            return
        pkey = str(path.resolve())
        qa = getattr(self, 'qa_status_by_path', {}).get(pkey)
        if not qa and self.json_data is not None:
            qa = qa_analyze_data(path, self.geo, self.json_data, duplicate=str(path.resolve()) in getattr(self, 'duplicate_paths', set()))
            self.qa_status_by_path[pkey] = qa
        if not qa:
            self.status_detail.setText("⚪ Chưa kiểm tra. Bấm <b>③ Kiểm tra thư viện</b> để tô màu danh sách.")
            return
        status = qa.get('status', 'unprocessed')
        icon = {"ok":"🟢", "warn":"🟠", "error":"🔴", "unprocessed":"⚪"}.get(status, "⚪")
        color = {"ok":"#1B7F3A", "warn":"#A96A00", "error":"#B00000", "unprocessed":"#607080"}.get(status, "#607080")
        lines = [f"<b style='color:{color}'>{icon} {qa.get('label','')}</b> — Độ tin cậy: <b>{round(float(qa.get('confidence',0))*100)}%</b>"]
        lines.append(f"Số cửa: <b>{qa.get('port_count','')}</b> | Tâm: {round(float(qa.get('center_confidence',0))*100)}% | Port: {round(float(qa.get('port_count_confidence',0))*100)}%")
        for e in qa.get('errors', [])[:4]:
            lines.append(f"<span style='color:#B00000'>✗ {e}</span>")
        for w in qa.get('warnings', [])[:5]:
            lines.append(f"<span style='color:#A96A00'>⚠ {w}</span>")
        for m in qa.get('messages', [])[:4]:
            lines.append(f"<span style='color:#1B7F3A'>✓ {m}</span>")
        if len(lines) == 2 and status == 'ok':
            lines.append("<span style='color:#1B7F3A'>✓ Tâm cút, số cửa, flow và quy ước port hợp lệ.</span>")
        self.status_detail.setText("<br>".join(lines))

    def check_all_libraries(self, silent: bool = False):
        # Backward-compatible wrapper.  The final UI uses ③ Kiểm tra thư viện,
        # which works on the exact files currently visible in the list.
        return self.check_visible_libraries(silent=silent)

    def log_msg(self, msg: str):
        self.log.append(msg)



# ============================================================
# V2.19: CAD preview renderer upgrade
# - TXT and JSON both become the same Geometry first.
# - Preview never changes raw coordinates; only screen Y is inverted for CAD display.
# - Cosmetic pens keep line weight constant during zoom.
# - Arcs/lines/ports/flow use one renderer path so TXT/JSON do not diverge.
# ============================================================

def _nevis_screen_y(y: float) -> float:
    return -float(y)


def _nevis_item_fixed(item):
    try:
        item.setFlag(item.ItemIgnoresTransformations, True)
    except Exception:
        pass
    return item


def _nevis_cad_pen(color, width: float = 0.85, style=Qt.SolidLine) -> QPen:
    pen = QPen(color, width, style)
    pen.setCosmetic(True)
    return pen


def _nevis_add_text(scene: QGraphicsScene, text: str, x: float, y: float, color: QColor):
    item = scene.addText(text)
    item.setDefaultTextColor(color)
    item.setPos(x, _nevis_screen_y(y))
    _nevis_item_fixed(item)
    return item


def _nevis_draw_arrow(scene: QGraphicsScene, x1: float, y1: float, x2: float, y2: float, color: QColor):
    pen = _nevis_cad_pen(color, 1.05, Qt.SolidLine)
    scene.addLine(x1, _nevis_screen_y(y1), x2, _nevis_screen_y(y2), pen)
    dx, dy = x2 - x1, y2 - y1
    ln = math.hypot(dx, dy)
    if ln < 1e-9:
        return
    ux, uy = dx/ln, dy/ln
    # arrow head is drawn in screen coordinates so it stays visually correct after Y inversion
    sx2, sy2 = x2, _nevis_screen_y(y2)
    sux, suy = ux, -uy
    nx, ny = -suy, sux
    size = 9.0
    p1 = QPointF(sx2, sy2)
    p2 = QPointF(sx2 - sux*size + nx*size*0.42, sy2 - suy*size + ny*size*0.42)
    p3 = QPointF(sx2 - sux*size - nx*size*0.42, sy2 - suy*size - ny*size*0.42)
    poly = scene.addPolygon(QPolygonF([p1, p2, p3]), pen, QBrush(QColor(color.red(), color.green(), color.blue(), 120)))
    _nevis_item_fixed(poly)


def _nevis_arc_preview_points(c: CircleArc, steps: int = 96) -> List[Tuple[float, float]]:
    """CAD/JWW-friendly arc preview.

    Supported TXT forms:
      ci cx cy r
      ci cx cy r start_deg end_deg ... rotate_deg

    JWW fitting TXT arcs in this project use degrees.  The last value is usually
    rotation when there are four or more numeric values after radius.
    The preview chooses the shorter span, which matches small elbow arcs in the
    existing NEVIS/JWW libraries.
    """
    nums = [float(x) for x in re.findall(NUM, c.rest or "")]
    if c.r <= 0:
        return []
    if len(nums) < 2:
        n = max(48, steps)
        return [(c.cx + c.r*math.cos(2*math.pi*i/n), c.cy + c.r*math.sin(2*math.pi*i/n)) for i in range(n+1)]
    a1, a2 = nums[0], nums[1]
    rot = nums[3] if len(nums) >= 4 else 0.0
    a1 = math.radians(a1 + rot)
    a2 = math.radians(a2 + rot)
    span = a2 - a1
    while span > math.pi:
        span -= 2*math.pi
    while span < -math.pi:
        span += 2*math.pi
    if abs(span) < 1e-9:
        span = 2*math.pi
    n = max(10, min(192, int(abs(span) / (2*math.pi) * steps) + 4))
    return [(c.cx + c.r*math.cos(a1 + span*i/n), c.cy + c.r*math.sin(a1 + span*i/n)) for i in range(n+1)]

# Replace old arc function used by other routines too.
arc_preview_points = _nevis_arc_preview_points


def _nevis_canvas_draw(self, geo: Geometry, json_data: Optional[Dict[str,Any]] = None, active_ports: int = 3, show_test=True):
    self.geo = geo
    sc = self.scene()
    sc.clear()

    # CAD colors: readable but thin. All pens are cosmetic -> zoom does not thicken lines.
    pen_outline = _nevis_cad_pen(QColor(0, 95, 150), 0.85, Qt.SolidLine)
    pen_aux = _nevis_cad_pen(QColor(75, 120, 145), 0.75, Qt.SolidLine)
    pen_center = _nevis_cad_pen(QColor(205, 55, 45), 0.85, Qt.DashLine)
    pen_origin = _nevis_cad_pen(QColor(120, 130, 145), 0.7, Qt.DotLine)
    pen_main = _nevis_cad_pen(QColor(30, 85, 205), 0.95, Qt.SolidLine)
    pen_branch = _nevis_cad_pen(QColor(165, 45, 160), 0.95, Qt.DashDotLine)
    pen_cut = _nevis_cad_pen(QColor(230, 135, 15), 0.9, Qt.SolidLine)

    pts: List[Tuple[float, float]] = []

    # 0,0 coordinate guide. This is not fitting center unless JSON says so;
    # it helps spot coordinate/preview misunderstanding immediately.
    sc.addLine(-18, 0, 18, 0, pen_origin)
    sc.addLine(0, -18, 0, 18, pen_origin)
    _nevis_add_text(sc, "0,0", 4, -4, QColor(110, 120, 135))
    pts += [(-18, -18), (18, 18)]

    # Draw every segment from raw coordinates. Do not recenter, do not normalize.
    for s in geo.segments:
        if s.lt == CENTER_LT:
            pen = pen_center
        elif s.lt == SOLID_LT:
            pen = pen_outline
        else:
            # Any non-lt49 line is still real geometry. Older libraries may use lt2/lt3/etc.
            pen = pen_aux
        sc.addLine(s.x1, _nevis_screen_y(s.y1), s.x2, _nevis_screen_y(s.y2), pen)
        pts += [(s.x1, _nevis_screen_y(s.y1)), (s.x2, _nevis_screen_y(s.y2))]

    # Draw circles/arcs with the same y conversion.
    for c in geo.circles:
        pen = pen_center if c.lt == CENTER_LT else (pen_outline if c.lt == SOLID_LT else pen_aux)
        pnts = _nevis_arc_preview_points(c)
        if len(pnts) >= 2:
            path = QPainterPath(QPointF(pnts[0][0], _nevis_screen_y(pnts[0][1])))
            for x, y in pnts[1:]:
                path.lineTo(x, _nevis_screen_y(y))
            sc.addPath(path, pen)
            pts += [(x, _nevis_screen_y(y)) for x, y in pnts]

    if json_data:
        try:
            cx, cy = [float(v) for v in json_data.get("center", [0,0])[:2]]
        except Exception:
            cx, cy = 0.0, 0.0

        # Fitting insert center.
        sc.addLine(cx-9, _nevis_screen_y(cy), cx+9, _nevis_screen_y(cy), _nevis_cad_pen(QColor(210, 30, 30), 1.1))
        sc.addLine(cx, _nevis_screen_y(cy)-9, cx, _nevis_screen_y(cy)+9, _nevis_cad_pen(QColor(210, 30, 30), 1.1))
        _nevis_item_fixed(sc.addEllipse(cx-3, _nevis_screen_y(cy)-3, 6, 6, _nevis_cad_pen(QColor(210,30,30), 1.0), QBrush(QColor(255,70,70,95))))
        _nevis_add_text(sc, "CENTER", cx+7, cy-7, QColor(190, 20, 20))
        pts.append((cx, _nevis_screen_y(cy)))

        ports = list(json_data.get("ports", []) or [])[:active_ports]
        ports_by_id = {str(p.get("id", "")): p for p in ports}

        # Main route and branch convention line for 3-port fittings.
        if show_test and int(json_data.get("port_count", active_ports) or active_ports) == 3:
            p1, p2, p3 = ports_by_id.get("P1"), ports_by_id.get("P2"), ports_by_id.get("P3")
            if p1 and p2:
                a = p1.get("center", [cx, cy]); b = p2.get("center", [cx, cy])
                sc.addLine(float(a[0]), _nevis_screen_y(float(a[1])), float(b[0]), _nevis_screen_y(float(b[1])), pen_main)
            if p3:
                a = p3.get("center", [cx, cy])
                sc.addLine(cx, _nevis_screen_y(cy), float(a[0]), _nevis_screen_y(float(a[1])), pen_branch)

        # Ports and cut points.
        for p in ports:
            try:
                px, py = [float(v) for v in p.get("center", [cx, cy])[:2]]
            except Exception:
                continue
            pid = str(p.get("id", "P"))
            role = str(p.get("role", ""))
            is_branch = pid == "P3" or role == "branch"
            port_pen = pen_branch if is_branch else pen_main
            port_brush = QBrush(QColor(220, 80, 220, 105) if is_branch else QColor(70, 145, 255, 105))
            _nevis_item_fixed(sc.addEllipse(px-4, _nevis_screen_y(py)-4, 8, 8, port_pen, port_brush))
            label = f"{pid} nhánh" if is_branch else pid
            _nevis_add_text(sc, label, px+6, py-3, QColor(155, 35, 155) if is_branch else QColor(20, 70, 150))
            if show_test:
                sc.addLine(cx, _nevis_screen_y(cy), px, _nevis_screen_y(py), _nevis_cad_pen(QColor(45,105,205), 0.75, Qt.DotLine))
            cp = p.get("cut_point")
            if cp:
                try:
                    qx, qy = float(cp[0]), float(cp[1])
                    _nevis_item_fixed(sc.addEllipse(qx-3, _nevis_screen_y(qy)-3, 6, 6, pen_cut, QBrush(QColor(255,170,40,100))))
                    pts.append((qx, _nevis_screen_y(qy)))
                except Exception:
                    pass
            pts.append((px, _nevis_screen_y(py)))

        # Flow arrow: always from fitting center to chosen standard port.
        flow = json_data.get("flow", {}) if isinstance(json_data, dict) else {}
        fport = flow.get("port")
        if show_test and flow.get("model", "directional") != "collector" and fport in ports_by_id:
            p = ports_by_id[fport]
            try:
                tx, ty = [float(v) for v in p.get("center", [cx, cy])[:2]]
                _nevis_draw_arrow(sc, cx, cy, tx, ty, QColor(40, 150, 70))
                _nevis_add_text(sc, "FLOW", (cx+tx)/2 + 4, (cy+ty)/2 - 4, QColor(30, 130, 60))
            except Exception:
                pass

    # Scene rect from actual drawn points. No data recentering.
    if not pts:
        pts = [(-100,-100), (100,100)]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    rect = QRectF(min(xs), min(ys), max(xs)-min(xs) or 100, max(ys)-min(ys) or 100)
    self.last_rect = rect.adjusted(-45, -45, 45, 45)
    sc.setSceneRect(self.last_rect)

# Install the upgraded renderer.
Canvas.draw = _nevis_canvas_draw


def main():
    app = QApplication(sys.argv)
    try:
        from nevis_activation_guard import ensure_activation_or_show
        if not ensure_activation_or_show():
            sys.exit(2)
    except Exception as ex:
        QMessageBox.critical(None, "NEVIS Activation", str(ex))
        sys.exit(2)
    w = MainWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
