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

import discord
from models.npc_modals.npc_basic_modal import NPCModalBase
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCAddAllyModal(NPCModalBase):
    def __init__(self, npc_context):
        self.locale = resolve_locale(getattr(npc_context, "interaction", None))
        super().__init__(npc_context, title=t("npc.ally.add.title", self.locale, name=npc_context.npc_name))

        roleplay = (self.npc_data.get("roleplay") or {})
        drafts = (roleplay.get("drafts") or {})
        saved = (drafts.get("add_aliado") or {})

        self.nome = discord.ui.TextInput(
            label=t("npc.ally.add.name.label", self.locale),
            placeholder=t("npc.ally.add.name.ph", self.locale),
            required=True,
            max_length=120,
            default=saved.get("nome", "") or ""
        )
        self.descricao = discord.ui.TextInput(
            label=t("npc.ally.add.desc.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.ally.add.desc.ph", self.locale),
            required=False,
            max_length=1000,
            default=saved.get("descricao", "") or ""
        )

        self.add_item(self.nome)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        roleplay = self.npc_data.setdefault("roleplay", {})
        drafts = roleplay.setdefault("drafts", {})
        allies_list = roleplay.setdefault("aliados", [])
        drafts["add_aliado"] = {
            "nome": self.nome.value,
            "descricao": self.descricao.value
        }
        allies_list.append({
            "nome": self.nome.value,
            "descricao": self.descricao.value
        })

        self.save()

        await interaction.response.send_message(
            t("npc.ally.add.success", self.locale, ally=self.nome.value, name=self.npc_context.npc_name),
            ephemeral=True
        )
