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

class AttackDetailsModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, draft: dict):
        self.locale = resolve_locale(interaction)
        self.draft = draft or {}

        super().__init__(title=t("attack_details.title", self.locale, user=interaction.user.display_name))

        self.efeitos = discord.ui.TextInput(
            label=t("attack_details.effects.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("attack_details.effects.ph", self.locale),
            required=False,
            default=self.draft.get("efeitos", "") or "",
            max_length=1500
        )
        self.descricao = discord.ui.TextInput(
            label=t("attack_details.desc.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("attack_details.desc.ph", self.locale),
            required=False,
            default=self.draft.get("descricao", "") or "",
            max_length=2000
        )
        self.tipo_dano = discord.ui.TextInput(
            label=t("attack_details.dtype.label", self.locale),
            placeholder=t("attack_details.dtype.ph", self.locale),
            required=False,
            default=self.draft.get("tipo_dano", "") or "",
            max_length=60
        )
        self.margem_critico = discord.ui.TextInput(
            label=t("attack_details.crit_range.label", self.locale),
            placeholder=t("attack_details.crit_range.ph", self.locale),
            default=str(self.draft.get("margem_critico", "20") or "20"),
            max_length=2,
            required=False
        )
        self.multiplicador_critico = discord.ui.TextInput(
            label=t("attack_details.crit_mult.label", self.locale),
            placeholder=t("attack_details.crit_mult.ph", self.locale),
            default=str(self.draft.get("multiplicador_critico", "2") or "2"),
            max_length=2,
            required=False
        )

        self.add_item(self.efeitos)
        self.add_item(self.descricao)
        self.add_item(self.tipo_dano)
        self.add_item(self.margem_critico)
        self.add_item(self.multiplicador_critico)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
