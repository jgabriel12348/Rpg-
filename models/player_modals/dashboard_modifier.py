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
from models.player_modals.teste_modifier import AddTestModifierModal
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class TestsDashboardView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=180)
        self.user = user
        self.locale = "pt"

    def _ensure_locale(self, interaction: discord.Interaction | None):
        if interaction:
            self.locale = resolve_locale(interaction)

    def create_embed(self) -> discord.Embed:
        character_name = f"{self.user.id}_{self.user.name.lower()}"
        ficha = player_utils.load_player_sheet(character_name)
        modificadores = ficha.get("testes_modificadores", [])

        embed = discord.Embed(
            title=t("tests_dash.title", self.locale, name=self.user.display_name),
            color=discord.Color.dark_teal()
        )

        if not modificadores:
            embed.description = t("tests_dash.empty", self.locale)
        else:
            lines = []
            for mod in modificadores:
                cond = mod.get("condicao") or ""
                cond_fmt = t("tests_dash.cond_fmt", self.locale, cond=cond) if cond else ""
                lines.append(t(
                    "tests_dash.line",
                    self.locale,
                    test=mod.get("nome_teste", ""),
                    mod=mod.get("modificador", ""),
                    cond=cond_fmt
                ))
            embed.description = "\n".join(lines)

        return embed

    @discord.ui.button(label="➕ Adicionar Modificador", style=discord.ButtonStyle.success)
    async def add_modifier(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._ensure_locale(interaction)
        button.label = t("tests_dash.add.label", self.locale)

        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                t("tests_dash.errors.other_user", self.locale),
                ephemeral=True
            )
        await interaction.response.send_modal(AddTestModifierModal(interaction=interaction))

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger)
    async def back_to_main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._ensure_locale(interaction)
        button.label = t("common.back", self.locale)

        from view.ficha_player.ficha_player_menu import PlayerMainMenuView
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                t("tests_dash.errors.other_user", self.locale),
                ephemeral=True
            )
        view = PlayerMainMenuView(user=self.user)
        await interaction.response.edit_message(
            content=t("tests_dash.menu.title", self.locale),
            view=view,
            embed=None
        )
