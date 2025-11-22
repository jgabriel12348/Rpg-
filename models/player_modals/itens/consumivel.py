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

class AddItemConsumableModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("inv_add_cons.title", self.locale))
        inventario = self.ficha.get("inventario", {}) or {}
        drafts = inventario.get("drafts", {}) or {}
        saved = drafts.get("add_item_consumivel", {}) or {}

        self.nome = discord.ui.TextInput(
            label=t("inv_add_cons.name.label", self.locale),
            placeholder=t("inv_add_cons.name.ph", self.locale),
            required=True,
            max_length=120,
            default=saved.get("nome", "")
        )
        self.quantidade = discord.ui.TextInput(
            label=t("inv_add_cons.qty.label", self.locale),
            placeholder=t("inv_add_cons.qty.ph", self.locale),
            required=True,
            max_length=5,
            default=str(saved.get("quantidade", "1"))
        )
        self.efeito = discord.ui.TextInput(
            label=t("inv_add_cons.effect.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("inv_add_cons.effect.ph", self.locale),
            required=True,
            max_length=1000,
            default=saved.get("efeito", "")
        )
        self.peso = discord.ui.TextInput(
            label=t("inv_add_cons.weight.label", self.locale),
            placeholder=t("inv_add_cons.weight.ph", self.locale),
            required=False,
            max_length=30,
            default=saved.get("peso", "")
        )

        self.add_item(self.nome)
        self.add_item(self.quantidade)
        self.add_item(self.efeito)
        self.add_item(self.peso)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qtd = int(self.quantidade.value)
            if not (1 <= qtd <= 9999):
                await interaction.response.send_message(
                    t("inv_add_cons.errors.qty_range", self.locale),
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                t("inv_add_cons.errors.qty_na", self.locale),
                ephemeral=True
            )
            return

        inventario = self.ficha.setdefault("inventario", {})
        drafts = inventario.setdefault("drafts", {})
        consumable_items = inventario.setdefault("consumivel", [])
        drafts["add_item_consumivel"] = {
            "nome": self.nome.value,
            "quantidade": qtd,
            "efeito": self.efeito.value,
            "peso": self.peso.value
        }
        novo_item = {
            "nome": self.nome.value,
            "quantidade": qtd,
            "efeito": self.efeito.value,
            "peso": self.peso.value
        }
        consumable_items.append(novo_item)

        self.save()

        await interaction.response.send_message(
            t("inv_add_cons.saved", self.locale, name=self.nome.value, qty=qtd),
            ephemeral=True
        )
