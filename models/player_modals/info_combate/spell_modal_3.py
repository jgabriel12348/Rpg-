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

class SpellExtraModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, draft: dict):
        self.locale = resolve_locale(interaction)
        self.draft = draft or {}

        super().__init__(title=t("spell_extra.title", self.locale, user=interaction.user.display_name))

        self.area_acao = discord.ui.TextInput(
            label=t("spell_extra.area.label", self.locale),
            placeholder=t("spell_extra.area.ph", self.locale),
            default=self.draft.get("area_acao", "") or "",
            max_length=100,
            required=False
        )
        self.duracao = discord.ui.TextInput(
            label=t("spell_extra.duration.label", self.locale),
            placeholder=t("spell_extra.duration.ph", self.locale),
            default=self.draft.get("duracao", "") or "",
            max_length=100,
            required=False
        )
        self.em_niveis_superiores = discord.ui.TextInput(
            label=t("spell_extra.upcast.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("spell_extra.upcast.ph", self.locale),
            default=self.draft.get("em_niveis_superiores", "") or "",
            max_length=800,
            required=False
        )
        self.classe_conjurador = discord.ui.TextInput(
            label=t("spell_extra.caster_class.label", self.locale),
            placeholder=t("spell_extra.caster_class.ph", self.locale),
            default=self.draft.get("classe_conjurador", "") or "",
            max_length=100,
            required=False
        )
        self.descricao = discord.ui.TextInput(
            label=t("spell_extra.desc.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("spell_extra.desc.ph", self.locale),
            default=self.draft.get("descricao", "") or "",
            max_length=1500,
            required=False
        )
        self.add_item(self.area_acao)
        self.add_item(self.duracao)
        self.add_item(self.em_niveis_superiores)
        self.add_item(self.classe_conjurador)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
