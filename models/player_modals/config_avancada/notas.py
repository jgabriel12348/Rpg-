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

class NotesModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("notes.title", self.locale))

        roleplay_data = (self.ficha.get("roleplay") or {})

        self.notas_gerais = discord.ui.TextInput(
            label=t("notes.general.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("notes.general.ph", self.locale),
            default=roleplay_data.get("notas_gerais", "") or "",
            required=False,
            max_length=4000
        )

        self.recursos_especiais = discord.ui.TextInput(
            label=t("notes.resources.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("notes.resources.ph", self.locale),
            default=roleplay_data.get("recursos_especiais", "") or "",
            required=False,
            max_length=4000
        )

        self.add_item(self.notas_gerais)
        self.add_item(self.recursos_especiais)

    async def on_submit(self, interaction: discord.Interaction):
        roleplay_data = self.ficha.setdefault("roleplay", {})
        roleplay_data["notas_gerais"] = self.notas_gerais.value
        roleplay_data["recursos_especiais"] = self.recursos_especiais.value
        self.save()

        await interaction.response.send_message(
            t("notes.success", self.locale),
            ephemeral=True
        )
