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
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class RoleplayDashboardView(discord.ui.View):
    def __init__(self, user: discord.User, category: str, category_name: str, modal_class: discord.ui.Modal):
        super().__init__(timeout=None)
        self.user = user
        self.category = category
        self.category_name = category_name
        self.modal_class = modal_class
        self.locale = None
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.callback == self.add_item.callback:
                    child.label = "➕"
                elif child.callback == self.back_to_roleplay_menu.callback:
                    child.label = "🔙"

    def _ensure_locale(self, interaction: discord.Interaction):
        if not self.locale:
            self.locale = resolve_locale(interaction)

        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.callback == self.add_item.callback:
                    child.label = t("roleplay_dashboard.add_button", self.locale)
                    child.style = discord.ButtonStyle.success
                elif child.callback == self.back_to_roleplay_menu.callback:
                    child.label = t("roleplay_dashboard.back_button", self.locale)
                    child.style = discord.ButtonStyle.danger

    @discord.ui.button(label="➕ Adicionar", style=discord.ButtonStyle.success)
    async def add_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._ensure_locale(interaction)
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                t("common.errors.not_owner_menu", self.locale),
                ephemeral=True
            )
        await interaction.response.send_modal(self.modal_class(interaction=interaction))

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger)
    async def back_to_roleplay_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_player.player_config_avancada import PlayerRoleplayMenuView
        self._ensure_locale(interaction)
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                t("common.errors.not_owner_menu", self.locale),
                ephemeral=True
            )

        view = PlayerRoleplayMenuView(user=self.user)
        await interaction.response.edit_message(
            content=t("roleplay_dashboard.menu_title", self.locale),
            view=view,
            embed=None
        )
