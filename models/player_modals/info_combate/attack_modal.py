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

class AttackPrimaryModal(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)

        super().__init__(title=t("attack_primary.title", self.locale, user=interaction.user.display_name))

        self.nome_ataque = discord.ui.TextInput(
            label=t("attack_primary.name.label", self.locale),
            placeholder=t("attack_primary.name.ph", self.locale),
            required=True,
            max_length=120
        )
        self.teste_de_acerto = discord.ui.TextInput(
            label=t("attack_primary.hit.label", self.locale),
            placeholder=t("attack_primary.hit.ph", self.locale),
            required=True,
            max_length=120
        )
        self.dano = discord.ui.TextInput(
            label=t("attack_primary.damage.label", self.locale),
            placeholder=t("attack_primary.damage.ph", self.locale),
            required=True,
            max_length=120
        )
        self.alcance = discord.ui.TextInput(
            label=t("attack_primary.range.label", self.locale),
            placeholder=t("attack_primary.range.ph", self.locale),
            required=False,
            max_length=120
        )
        self.usos = discord.ui.TextInput(
            label=t("attack_primary.uses.label", self.locale),
            placeholder=t("attack_primary.uses.ph", self.locale),
            required=False,
            max_length=120
        )

        self.add_item(self.nome_ataque)
        self.add_item(self.teste_de_acerto)
        self.add_item(self.dano)
        self.add_item(self.alcance)
        self.add_item(self.usos)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
