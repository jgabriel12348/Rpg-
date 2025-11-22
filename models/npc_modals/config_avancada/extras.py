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

class NPCExtrasModal(NPCModalBase):
    def __init__(self, npc_context):
        _ = resolve_locale(getattr(npc_context, "interaction", None))
        self._ = _

        super().__init__(
            npc_context,
            title=t("npc.extras.title", _, name=npc_context.npc_name)
        )

        extras_data = (self.npc_data.get("extras") or {})

        self.comportamento = discord.ui.TextInput(
            label=t("npc.extras.behavior.label", _),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.extras.behavior.ph", _),
            default=(extras_data.get("comportamento") or ""),
            required=False,
            max_length=2000
        )
        self.loot = discord.ui.TextInput(
            label=t("npc.extras.loot.label", _),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.extras.loot.ph", _),
            default=(extras_data.get("loot") or ""),
            required=False,
            max_length=2000
        )

        self.add_item(self.comportamento)
        self.add_item(self.loot)

    async def on_submit(self, interaction: discord.Interaction):
        self.npc_data.setdefault("extras", {})
        self.npc_data["extras"]["comportamento"] = self.comportamento.value
        self.npc_data["extras"]["loot"] = self.loot.value
        self.save()

        await interaction.response.send_message(
            t("npc.extras.saved", self._, name=self.npc_context.npc_name),
            ephemeral=True
        )
