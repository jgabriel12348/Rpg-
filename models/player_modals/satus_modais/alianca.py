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

class AllianceModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("alliances.title", self.locale))
        saved = (self.ficha.get("aliancas") or {})

        self.faccao = discord.ui.TextInput(
            label=t("alliances.faction.label", self.locale),
            placeholder=t("alliances.faction.ph", self.locale),
            required=False,
            max_length=100,
            default=saved.get("faccao", "") or ""
        )
        self.status = discord.ui.TextInput(
            label=t("alliances.status.label", self.locale),
            placeholder=t("alliances.status.ph", self.locale),
            required=False,
            max_length=80,
            default=saved.get("status", "") or ""
        )
        self.contatos = discord.ui.TextInput(
            label=t("alliances.contacts.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("alliances.contacts.ph", self.locale),
            required=False,
            max_length=1000,
            default=saved.get("contatos", "") or ""
        )
        self.inimigos = discord.ui.TextInput(
            label=t("alliances.enemies.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("alliances.enemies.ph", self.locale),
            required=False,
            max_length=1000,
            default=saved.get("inimigos", "") or ""
        )

        self.add_item(self.faccao)
        self.add_item(self.status)
        self.add_item(self.contatos)
        self.add_item(self.inimigos)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["aliancas"] = {
            "faccao": self.faccao.value,
            "status": self.status.value,
            "contatos": self.contatos.value,
            "inimigos": self.inimigos.value
        }
        self.save()

        await interaction.response.send_message(
            t("alliances.saved", self.locale),
            ephemeral=True
        )
