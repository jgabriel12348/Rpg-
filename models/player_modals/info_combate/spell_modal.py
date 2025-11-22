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

class SpellPrimaryModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, draft: dict | None = None):
        self.locale = resolve_locale(interaction)
        super().__init__(title=t("spell_primary.title", self.locale, user=interaction.user.display_name))

        draft = draft or {}

        self.nome_magia = discord.ui.TextInput(
            label=t("spell_primary.name.label", self.locale),
            placeholder=t("spell_primary.name.ph", self.locale),
            default=draft.get("nome", "") or "",
            max_length=100,
            required=True
        )
        self.nivel = discord.ui.TextInput(
            label=t("spell_primary.level.label", self.locale),
            placeholder=t("spell_primary.level.ph", self.locale),
            default=draft.get("nivel", "") or "",
            max_length=10,
            required=False
        )
        self.escola = discord.ui.TextInput(
            label=t("spell_primary.school.label", self.locale),
            placeholder=t("spell_primary.school.ph", self.locale),
            default=draft.get("escola", "") or "",
            max_length=50,
            required=False
        )
        self.tempo_conjuracao = discord.ui.TextInput(
            label=t("spell_primary.cast_time.label", self.locale),
            placeholder=t("spell_primary.cast_time.ph", self.locale),
            default=draft.get("tempo_conjuracao", "") or "",
            max_length=50,
            required=False
        )
        self.concentracao = discord.ui.TextInput(
            label=t("spell_primary.concentration.label", self.locale),
            placeholder=t("spell_primary.concentration.ph", self.locale),
            default=draft.get("concentracao", "") or "",
            max_length=10,
            required=False
        )

        self.add_item(self.nome_magia)
        self.add_item(self.nivel)
        self.add_item(self.escola)
        self.add_item(self.tempo_conjuracao)
        self.add_item(self.concentracao)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
