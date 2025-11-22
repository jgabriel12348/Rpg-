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

class SpellDetailsModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, draft: dict):
        self.locale = resolve_locale(interaction)
        self.draft = draft or {}

        super().__init__(title=t("spell_details.title", self.locale, user=interaction.user.display_name))

        self.componentes = discord.ui.TextInput(
            label=t("spell_details.components.label", self.locale),
            placeholder=t("spell_details.components.ph", self.locale),
            default=self.draft.get("componentes", "") or "",
            max_length=100,
            required=False
        )
        self.alcance = discord.ui.TextInput(
            label=t("spell_details.range.label", self.locale),
            placeholder=t("spell_details.range.ph", self.locale),
            default=self.draft.get("alcance", "") or "",
            max_length=100,
            required=False
        )
        self.efeito = discord.ui.TextInput(
            label=t("spell_details.effect.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("spell_details.effect.ph", self.locale),
            default=self.draft.get("efeito", "") or "",
            max_length=1500,
            required=False
        )
        self.formula_acerto = discord.ui.TextInput(
            label=t("spell_details.hit_formula.label", self.locale),
            placeholder=t("spell_details.hit_formula.ph", self.locale),
            default=self.draft.get("formula_acerto", "") or "",
            max_length=120,
            required=False
        )
        self.formula_dano_cura = discord.ui.TextInput(
            label=t("spell_details.dmgheal_formula.label", self.locale),
            placeholder=t("spell_details.dmgheal_formula.ph", self.locale),
            default=self.draft.get("formula_dano_cura", "") or "",
            max_length=120,
            required=False
        )
        self.add_item(self.componentes)
        self.add_item(self.alcance)
        self.add_item(self.efeito)
        self.add_item(self.formula_acerto)
        self.add_item(self.formula_dano_cura)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
