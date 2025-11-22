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

BASE_DIR = "data/servidores"

def get_server_path(guild_name: str) -> str:
    server_path = os.path.join(BASE_DIR, guild_name)
    os.makedirs(server_path, exist_ok=True)
    return server_path

def get_mestres_path(guild_name: str) -> str:
    return os.path.join(get_server_path(guild_name), "mestres.json")

def carregar_mestres(guild_name: str) -> list:
    mestres_path = get_mestres_path(guild_name)
    if not os.path.exists(mestres_path):
        return []
    with open(mestres_path, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_mestres(guild_name: str, mestres: list):
    mestres_path = get_mestres_path(guild_name)
    with open(mestres_path, "w", encoding="utf-8") as f:
        json.dump(mestres, f, indent=4, ensure_ascii=False)

def adicionar_mestre(guild_name: str, mestre_id: int, mestre_nome: str):
    mestres = carregar_mestres(guild_name)
    if any(m["id"] == mestre_id for m in mestres):
        return False
    mestres.append({"id": mestre_id, "nome": mestre_nome})
    salvar_mestres(guild_name, mestres)
    return True

def verificar_mestre(guild_name: str, user_id: int) -> bool:
    mestres = carregar_mestres(guild_name)
    return any(m["id"] == user_id for m in mestres)
