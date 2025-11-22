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
from models.npc_modals.npc_basic_modal import NPCModalBase
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCWalletModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)

        super().__init__(
            npc_context,
            title=t("npc.wallet.title", self.locale, name=npc_context.npc_name)
        )

        inventory = self.npc_data.get("inventario", {}) or {}
        wallet = inventory.get("carteira", {}) or {}

        self.moedas = discord.ui.TextInput(
            label=t("npc.wallet.fields.coins", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.wallet.placeholders.coins", self.locale),
            default=wallet.get("moedas") or "",
            required=False
        )
        self.gemas = discord.ui.TextInput(
            label=t("npc.wallet.fields.gems", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.wallet.placeholders.gems", self.locale),
            default=wallet.get("gemas") or "",
            required=False
        )

        self.add_item(self.moedas)
        self.add_item(self.gemas)

    async def on_submit(self, interaction: discord.Interaction):
        inventory = self.npc_data.setdefault("inventario", {})
        inventory["carteira"] = {
            "moedas": self.moedas.value,
            "gemas": self.gemas.value
        }
        self.save()

        await interaction.response.send_message(
            t("npc.wallet.updated", self.locale, name=self.npc_context.npc_name),
            ephemeral=True
        )
