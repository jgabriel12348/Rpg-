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

class AddItemCombatModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("inv_add_combat.title", self.locale))
        inventario = self.ficha.get("inventario", {}) or {}
        drafts = inventario.get("drafts", {}) or {}
        saved = drafts.get("add_item_combate", {}) or {}

        self.nome = discord.ui.TextInput(
            label=t("inv_add_combat.name.label", self.locale),
            placeholder=t("inv_add_combat.name.ph", self.locale),
            required=True,
            max_length=120,
            default=saved.get("nome", "")
        )
        self.quantidade = discord.ui.TextInput(
            label=t("inv_add_combat.qty.label", self.locale),
            placeholder=t("inv_add_combat.qty.ph", self.locale),
            required=True,
            max_length=5,
            default=str(saved.get("quantidade", "1"))
        )
        self.dano = discord.ui.TextInput(
            label=t("inv_add_combat.dmg.label", self.locale),
            placeholder=t("inv_add_combat.dmg.ph", self.locale),
            required=True,
            max_length=20,
            default=saved.get("dano", "")
        )
        self.peso = discord.ui.TextInput(
            label=t("inv_add_combat.weight.label", self.locale),
            placeholder=t("inv_add_combat.weight.ph", self.locale),
            required=False,
            max_length=30,
            default=saved.get("peso", "")
        )
        self.propriedades = discord.ui.TextInput(
            label=t("inv_add_combat.props.label", self.locale),
            placeholder=t("inv_add_combat.props.ph", self.locale),
            required=False,
            max_length=500,
            default=saved.get("propriedades", "")
        )

        self.add_item(self.nome)
        self.add_item(self.quantidade)
        self.add_item(self.dano)
        self.add_item(self.peso)
        self.add_item(self.propriedades)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qtd = int(self.quantidade.value)
            if not (1 <= qtd <= 9999):
                await interaction.response.send_message(
                    t("inv_add_combat.errors.qty_range", self.locale),
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                t("inv_add_combat.errors.qty_na", self.locale),
                ephemeral=True
            )
            return

        inventario = self.ficha.setdefault("inventario", {})
        drafts = inventario.setdefault("drafts", {})
        combat_items = inventario.setdefault("combate", [])
        drafts["add_item_combate"] = {
            "nome": self.nome.value,
            "quantidade": qtd,
            "dano": self.dano.value,
            "peso": self.peso.value,
            "propriedades": self.propriedades.value
        }

        novo_item = {
            "nome": self.nome.value,
            "quantidade": qtd,
            "dano": self.dano.value,
            "peso": self.peso.value,
            "propriedades": self.propriedades.value
        }
        combat_items.append(novo_item)

        self.save()

        await interaction.response.send_message(
            t("inv_add_combat.saved", self.locale, name=self.nome.value),
            ephemeral=True
        )
