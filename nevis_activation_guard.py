# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import hmac
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import List, Optional

NEVIS_ACTIVATION_SECRET = b"NEVIS-MEP-NewVision-Offline-Activation-2026"
NEVIS_APPDATA_NAME = "NEVIS MEP"


def _is_frozen() -> bool:
    try:
        return bool(getattr(sys, "frozen", False))
    except Exception:
        return False


def app_dir() -> Path:
    if _is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def program_data_dir() -> Path:
    base = os.environ.get("PROGRAMDATA") or r"C:\ProgramData"
    return Path(base) / NEVIS_APPDATA_NAME


def _run_cmd_text(cmd: List[str]) -> str:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, timeout=2)
        return out.decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""


def _first_wmic_value(alias: str, prop: str) -> str:
    txt = _run_cmd_text(["wmic", alias, "get", prop])
    lines = [x.strip() for x in txt.splitlines() if x.strip()]
    vals = [x for x in lines if x.lower() != prop.lower()]
    return vals[0] if vals else ""


def machine_fingerprint() -> str:
    parts: List[str] = []
    if os.name == "nt":
        try:
            import winreg  # type: ignore
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as k:
                parts.append(str(winreg.QueryValueEx(k, "MachineGuid")[0]))
        except Exception:
            pass
    for alias, prop in (
        ("cpu", "ProcessorId"),
        ("bios", "SerialNumber"),
        ("baseboard", "SerialNumber"),
        ("diskdrive", "SerialNumber"),
    ):
        v = _first_wmic_value(alias, prop)
        if v:
            parts.append(v)
    if not parts:
        parts.append(str(uuid.getnode()))
        parts.append(os.environ.get("COMPUTERNAME", ""))
    raw = "|".join(x.strip().upper() for x in parts if str(x).strip())
    return hashlib.sha256(raw.encode("utf-8", errors="ignore")).hexdigest().upper()


def machine_code() -> str:
    h = machine_fingerprint()
    return "NEVIS-" + "-".join(h[i:i + 4] for i in range(0, 16, 4))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig").strip()
    except Exception:
        return ""


def _install_id_paths() -> List[Path]:
    return [app_dir() / "install_id.dat", program_data_dir() / "install_id.dat"]


def _activation_paths() -> List[Path]:
    return [app_dir() / "activation.dat", program_data_dir() / "activation.dat"]


def _read_install_id() -> str:
    vals = [_read_text(p) for p in _install_id_paths()]
    vals = [v for v in vals if v]
    if not vals:
        return ""
    if len(set(vals)) != 1:
        return ""
    return vals[0]


def _signature(install_id: str, code: str) -> str:
    msg = f"{install_id}|{code}|{NEVIS_APPDATA_NAME}".encode("utf-8", errors="ignore")
    return hmac.new(NEVIS_ACTIVATION_SECRET, msg, hashlib.sha256).hexdigest().upper()


def _activation_payload(install_id: str) -> dict:
    code = machine_code()
    return {
        "product": NEVIS_APPDATA_NAME,
        "install_id": install_id,
        "machine_code": code,
        "activated_at": int(time.time()),
        "signature": _signature(install_id, code),
    }


def _payload_valid(data: dict, install_id: str) -> bool:
    try:
        code = machine_code()
        return (
            str(data.get("product")) == NEVIS_APPDATA_NAME
            and str(data.get("install_id")) == install_id
            and str(data.get("machine_code")) == code
            and hmac.compare_digest(str(data.get("signature")), _signature(install_id, code))
        )
    except Exception:
        return False


def _read_activation(path: Path) -> Optional[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _write_activation_to_all(data: dict) -> None:
    for p in _activation_paths():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def activation_error_message() -> str:
    return (
        "NEVIS is not activated for this computer.\n\n"
        "Please install NEVIS using the official installer on this PC.\n"
        "Copying the installed folder to another computer is not allowed."
    )


def ensure_activation() -> bool:
    if not _is_frozen() or os.environ.get("NEVIS_SKIP_ACTIVATION") == "1":
        return True
    install_id = _read_install_id()
    if not install_id:
        return False
    existing = []
    invalid_existing = False
    for p in _activation_paths():
        data = _read_activation(p)
        if data is None:
            continue
        if _payload_valid(data, install_id):
            existing.append(data)
        else:
            invalid_existing = True
    if existing:
        try:
            _write_activation_to_all(existing[0])
        except Exception:
            return False
        return True
    # If the installer has just refreshed install_id.dat, older activation files
    # may no longer match. Regenerate them on this officially installed machine
    # instead of blocking a normal reinstall/update.
    if invalid_existing:
        try:
            _write_activation_to_all(_activation_payload(install_id))
            return True
        except Exception:
            return False
    try:
        _write_activation_to_all(_activation_payload(install_id))
        return True
    except Exception:
        return False


def ensure_activation_or_show(parent=None) -> bool:
    ok = ensure_activation()
    if ok:
        return True
    try:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(parent, "NEVIS Activation", activation_error_message())
    except Exception:
        try:
            print(activation_error_message())
        except Exception:
            pass
    return False
