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

class PersonalityModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("personality.title", self.locale))
        saved = (self.ficha.get("personalidade") or {})

        self.personalidade = discord.ui.TextInput(
            label=t("personality.summary.label", self.locale),
            placeholder=t("personality.summary.ph", self.locale),
            max_length=100,
            required=False,
            default=saved.get("resumo", "") or ""
        )
        self.tracos = discord.ui.TextInput(
            label=t("personality.traits.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("personality.traits.ph", self.locale),
            required=False,
            max_length=1500,
            default=saved.get("tracos_marcantes", "") or ""
        )

        self.add_item(self.personalidade)
        self.add_item(self.tracos)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["personalidade"] = {
            "resumo": self.personalidade.value,
            "tracos_marcantes": self.tracos.value
        }
        self.save()

        await interaction.response.send_message(
            t("personality.saved", self.locale),
            ephemeral=True
        )
