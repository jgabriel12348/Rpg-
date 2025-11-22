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

class ExtrasModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("extras.title", self.locale))
        saved = (self.ficha.get("extras") or {})

        self.notas = discord.ui.TextInput(
            label=t("extras.notes.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("extras.notes.ph", self.locale),
            required=False,
            max_length=3000,
            default=saved.get("notas", "") or ""
        )

        self.add_item(self.notas)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["extras"] = {
            "notas": self.notas.value
        }
        self.save()

        await interaction.response.send_message(
            t("extras.saved", self.locale),
            ephemeral=True
        )
