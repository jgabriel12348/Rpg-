# Copyright (C) 2025 Matheus Pereira
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# TRADEMARK NOTICE: The name "Roll & Play Bot" and its logo are distinct
# from the software and are NOT covered by the AGPL. They remain the
# exclusive property of the author.

from __future__ import annotations
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, Iterable, Optional
import json

LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"
DEFAULT_LOCALE = "pt"

def set_default_locale(locale: str) -> None:
    global DEFAULT_LOCALE
    DEFAULT_LOCALE = _normalize(locale)
    clear_i18n_cache()

def clear_i18n_cache() -> None:
    _load_bundle.cache_clear()

def available_locales() -> list[str]:
    if not LOCALES_DIR.exists():
        return []
    return sorted([p.name for p in LOCALES_DIR.iterdir() if p.is_dir()])

def _normalize(loc: Optional[str]) -> str:
    if not loc:
        return DEFAULT_LOCALE
    loc = str(loc).lower()
    if loc.startswith("pt"):
        return "pt"
    if loc.startswith("en"):
        return "en"
    return DEFAULT_LOCALE

def _merge_dicts(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _merge_dicts(dst[k], v)
        else:
            dst[k] = v

@lru_cache(maxsize=16)
def _load_bundle(locale: str) -> Dict[str, Any]:
    bundle: Dict[str, Any] = {}
    loc_dir = LOCALES_DIR / locale
    if not loc_dir.exists():
        return bundle
    for p in sorted(loc_dir.glob("*.json")):
        try:
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                _merge_dicts(bundle, data)
        except Exception:
            continue
    return bundle

def _get_from_bundle(bundle: Dict[str, Any], dot_key: str) -> Any:
    cur: Any = bundle
    parts = dot_key.split(".")
    ok = True
    for part in parts:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            ok = False
            break
    if ok:
        return cur

    if isinstance(bundle, dict) and dot_key in bundle:
        return bundle[dot_key]

    return None

def t(key: str, locale: Optional[str] = None, **kwargs) -> str:
    loc = _normalize(locale)
    text = _get_from_bundle(_load_bundle(loc), key)
    if text is None and loc != DEFAULT_LOCALE:
        text = _get_from_bundle(_load_bundle(DEFAULT_LOCALE), key)
    if text is None:
        text = key
    if isinstance(text, str) and kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text

def keys(locale: Optional[str] = None) -> set[str]:
    loc = _normalize(locale)
    bundle = _load_bundle(loc)
    out: set[str] = set()
    def walk(prefix: str, node: Any):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(f"{prefix}.{k}" if prefix else k, v)
        else:
            out.add(prefix)
    walk("", bundle)
    return out

def diff_locales(a: str, b: str) -> dict[str, set[str]]:
    ak, bk = keys(a), keys(b)
    return {
        "missing_in_" + a: bk - ak,
        "missing_in_" + b: ak - bk,
    }
