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

class NPCItemDashboardView(discord.ui.View):
    def __init__(self, npc_context: NPCContext, category: str, category_name: str, modal_class: discord.ui.Modal):
        super().__init__(timeout=180)
        self.npc_context = npc_context
        self.category = category
        self.category_name = category_name
        self.modal_class = modal_class
        self._base_locale = getattr(npc_context, "locale", None) or "pt"

    @discord.ui.button(label="➕", style=discord.ButtonStyle.success, row=0, custom_id="npc_add_item_btn")
    async def add_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.npc_context.mestre_id:
            loc = resolve_locale(interaction)
            return await interaction.response.send_message(
                t("npc.common.only_gm", loc),
                ephemeral=True
            )
        self.npc_context.interaction = interaction
        try:
            modal = self.modal_class(npc_context=self.npc_context, interaction=interaction)
        except TypeError:
            modal = self.modal_class(npc_context=self.npc_context)

        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🔙", style=discord.ButtonStyle.danger, row=0, custom_id="npc_back_btn")
    async def back_to_inventory_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_npc.npc_itens import NPCInventoryView

        if interaction.user.id != self.npc_context.mestre_id:
            loc = resolve_locale(interaction)
            return await interaction.response.send_message(
                t("npc.common.only_gm", loc),
                ephemeral=True
            )

        loc = resolve_locale(interaction)
        view = NPCInventoryView(npc_context=self.npc_context)
        await interaction.response.edit_message(
            content=t("npc.inventory.menu.title", loc).format(name=self.npc_context.npc_name),
            view=view,
            embed=None
        )

    def update_button_labels(self):
        loc = self._base_locale
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "npc_add_item_btn":
                    child.label = t("npc.inventory.dashboard.add_item_btn", loc)
                elif child.custom_id == "npc_back_btn":
                    child.label = t("npc.common.back", loc)
