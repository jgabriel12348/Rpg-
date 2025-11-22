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
from typing import Optional, Callable

def _normalize(loc: Optional[str]) -> Optional[str]:
    if not loc:
        return None
    loc = str(loc).lower()
    if loc.startswith("pt"):
        return "pt"
    if loc.startswith("en"):
        return "en"
    return None

def resolve_locale(
    interaction: object,
    *,
    fallback: str = "pt",
    user_pref_resolver: Optional[Callable[[int], Optional[str]]] = None,
    guild_pref_resolver: Optional[Callable[[int], Optional[str]]] = None,
) -> str:
    try:
        user_id = getattr(getattr(interaction, "user", None), "id", None)
        if user_pref_resolver and user_id:
            loc = _normalize(user_pref_resolver(int(user_id)))
            if loc:
                return loc
    except Exception:
        pass

    try:
        guild_id = getattr(getattr(interaction, "guild", None), "id", None)
        if guild_pref_resolver and guild_id:
            loc = _normalize(guild_pref_resolver(int(guild_id)))
            if loc:
                return loc
    except Exception:
        pass

    loc = _normalize(getattr(interaction, "locale", None))
    if loc:
        return loc

    loc = _normalize(getattr(interaction, "guild_locale", None))
    if loc:
        return loc

    return _normalize(fallback) or "pt"
