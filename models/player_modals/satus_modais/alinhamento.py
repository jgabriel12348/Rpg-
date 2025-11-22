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
from models.player_modals.player_basic_modal import PlayerModalBase
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class AlignmentModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("alignment.title", self.locale))
        saved = (self.ficha.get("alinhamento_crencas") or {})

        self.alinhamento = discord.ui.TextInput(
            label=t("alignment.alignment.label", self.locale),
            placeholder=t("alignment.alignment.ph", self.locale),
            required=False,
            max_length=200,
            default=saved.get("alinhamento", "") or ""
        )
        self.ideais = discord.ui.TextInput(
            label=t("alignment.ideals.label", self.locale),
            placeholder=t("alignment.ideals.ph", self.locale),
            required=False,
            max_length=300,
            default=saved.get("ideais", "") or ""
        )
        self.defeitos = discord.ui.TextInput(
            label=t("alignment.flaws.label", self.locale),
            placeholder=t("alignment.flaws.ph", self.locale),
            required=False,
            max_length=300,
            default=saved.get("defeitos", "") or ""
        )
        self.vinculos = discord.ui.TextInput(
            label=t("alignment.bonds.label", self.locale),
            placeholder=t("alignment.bonds.ph", self.locale),
            required=False,
            max_length=300,
            default=saved.get("vinculos", "") or ""
        )

        self.add_item(self.alinhamento)
        self.add_item(self.ideais)
        self.add_item(self.defeitos)
        self.add_item(self.vinculos)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["alinhamento_crencas"] = {
            "alinhamento": self.alinhamento.value,
            "ideais": self.ideais.value,
            "defeitos": self.defeitos.value,
            "vinculos": self.vinculos.value
        }
        self.save()

        await interaction.response.send_message(
            t("alignment.saved", self.locale),
            ephemeral=True
        )
