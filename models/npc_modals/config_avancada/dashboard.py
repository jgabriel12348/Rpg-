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
from utils.npc_utils import NPCContext
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCRoleplayDashboardView(discord.ui.View):
    def __init__(self, npc_context: NPCContext, category: str, modal_class: discord.ui.Modal):
        super().__init__(timeout=None)
        self.npc_context = npc_context
        self.category = category
        self.modal_class = modal_class
        self._ = resolve_locale(getattr(npc_context, "interaction", None))
        add_btn = discord.ui.Button(
            label=t("npc.roleplay.view.add", self._),
            style=discord.ButtonStyle.success
        )
        add_btn.callback = self._add_item
        self.add_item(add_btn)

        back_btn = discord.ui.Button(
            label=t("common.back", self._),
            style=discord.ButtonStyle.danger
        )
        back_btn.callback = self._back_to_roleplay_menu
        self.add_item(back_btn)

    async def _add_item(self, interaction: discord.Interaction):
        loc = self._
        if interaction.user.id != self.npc_context.mestre_id:
            return await interaction.response.send_message(
                t("npc.roleplay.view.only_master", loc),
                ephemeral=True
            )
        await interaction.response.send_modal(self.modal_class(npc_context=self.npc_context))

    async def _back_to_roleplay_menu(self, interaction: discord.Interaction):
        from view.ficha_npc.npc_config_avancada import NPCConfigAvancadasView
        loc = self._
        if interaction.user.id != self.npc_context.mestre_id:
            return await interaction.response.send_message(
                t("npc.roleplay.view.only_master", loc),
                ephemeral=True
            )

        view = NPCConfigAvancadasView(npc_context=self.npc_context)
        await interaction.response.edit_message(
            content=t("npc.roleplay.view.menu_title", loc, name=self.npc_context.npc_name),
            view=view,
            embed=None
        )
