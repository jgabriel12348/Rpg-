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
from utils import player_utils
from view.ficha_player.remove_item_view import RemoveItemView
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class ItemDashboardView(discord.ui.View):
    def __init__(self, user: discord.User, category: str, category_name: str, modal_class: type[discord.ui.Modal]):
        super().__init__(timeout=None)
        self.user = user
        self.category = category
        self.category_name = category_name
        self.modal_class = modal_class
        self.locale = "pt"
        self.add_item(self.AddItemButton(owner=self))
        self.add_item(self.RemoveItemButton(owner=self))
        self.add_item(self.BackButton(owner=self))

    def _ensure_locale(self, interaction: discord.Interaction | None):
        if interaction:
            self.locale = resolve_locale(interaction)

    def _i(self, key: str, **kw) -> str:
        return t(key, self.locale, **kw)

    class AddItemButton(discord.ui.Button):
        def __init__(self, owner: "ItemDashboardView"):
            self.owner = owner
            super().__init__(label=owner._i("items_dash.add.label"), style=discord.ButtonStyle.success)

        async def callback(self, interaction: discord.Interaction):
            self.owner._ensure_locale(interaction)
            self.label = self.owner._i("items_dash.add.label")

            if interaction.user.id != self.view.user.id:
                return await interaction.response.send_message(
                    self.owner._i("items_dash.errors.other_user"),
                    ephemeral=True
                )

            await interaction.response.send_modal(self.view.modal_class(interaction=interaction))

    class RemoveItemButton(discord.ui.Button):
        def __init__(self, owner: "ItemDashboardView"):
            self.owner = owner
            super().__init__(label=owner._i("items_dash.remove.label"), style=discord.ButtonStyle.danger)

        async def callback(self, interaction: discord.Interaction):
            self.owner._ensure_locale(interaction)
            self.label = self.owner._i("items_dash.remove.label")

            if interaction.user.id != self.view.user.id:
                return await interaction.response.send_message(
                    self.owner._i("items_dash.errors.other_user"),
                    ephemeral=True
                )

            view = RemoveItemView(
                user=self.view.user,
                category=self.view.category,
                category_name=self.view.category_name,
                modal_class=self.view.modal_class
            )
            await interaction.response.edit_message(
                content=self.owner._i("items_dash.remove.prompt", category_name=self.view.category_name),
                view=view,
                embed=None
            )

    class BackButton(discord.ui.Button):
        def __init__(self, owner: "ItemDashboardView"):
            self.owner = owner
            super().__init__(label=owner._i("common.back"), style=discord.ButtonStyle.secondary)

        async def callback(self, interaction: discord.Interaction):
            self.owner._ensure_locale(interaction)
            self.label = self.owner._i("common.back")

            from view.ficha_player.player_itens import PlayerInventarioMenuView

            if interaction.user.id != self.view.user.id:
                return await interaction.response.send_message(
                    self.owner._i("items_dash.errors.other_user"),
                    ephemeral=True
                )

            view = PlayerInventarioMenuView(user=self.view.user)
            await interaction.response.edit_message(
                content=self.owner._i("items_dash.menu.title"),
                view=view,
                embed=None
            )
