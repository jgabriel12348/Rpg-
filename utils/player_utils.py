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

import os
import json
import re

BASE_PLAYER_PATH = "data/players"

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)

def get_player_sheet_path(character_name: str) -> str:
    safe_name = sanitize_filename(character_name.lower().replace(" ", "_"))
    return os.path.join(BASE_PLAYER_PATH, f"{safe_name}.json")

def load_player_sheet(character_name: str) -> dict:
    path = get_player_sheet_path(character_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_player_sheet(character_name: str, data: dict):
    path = get_player_sheet_path(character_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def player_sheet_exists(character_name: str) -> bool:
    return os.path.exists(get_player_sheet_path(character_name))

def delete_player_sheet(character_name: str) -> bool:
    path = get_player_sheet_path(character_name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
