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

class NPCAddFearModal(NPCModalBase):
    def __init__(self, npc_context):
        _ = resolve_locale(getattr(npc_context, "interaction", None))
        self._ = _

        super().__init__(
            npc_context,
            title=t("npc.fear.add.title", _, name=npc_context.npc_name)
        )

        roleplay = (self.npc_data.get("roleplay") or {})
        drafts = (roleplay.get("drafts") or {})
        saved = (drafts.get("add_medo") or {})

        self.medo = discord.ui.TextInput(
            label=t("npc.fear.add.name.label", _),
            placeholder=t("npc.fear.add.name.ph", _),
            required=True,
            max_length=100,
            default=saved.get("medo", "") or ""
        )
        self.descricao = discord.ui.TextInput(
            label=t("npc.fear.add.desc.label", _),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.fear.add.desc.ph", _),
            required=False,
            max_length=1000,
            default=saved.get("descricao", "") or ""
        )

        self.add_item(self.medo)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        roleplay = self.npc_data.setdefault("roleplay", {})
        drafts = roleplay.setdefault("drafts", {})
        fears_list = roleplay.setdefault("medos_fobias", [])

        drafts["add_medo"] = {
            "medo": self.medo.value,
            "descricao": self.descricao.value
        }

        fears_list.append({
            "medo": self.medo.value,
            "descricao": self.descricao.value
        })

        self.save()

        await interaction.response.send_message(
            t("npc.fear.add.success", self._, fear=self.medo.value, name=self.npc_context.npc_name),
            ephemeral=True
        )
