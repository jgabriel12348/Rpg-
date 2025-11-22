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

class NPCAddItemConsumableModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)

        super().__init__(
            npc_context,
            title=t("npc.inventory.consumable.title", self.locale, name=npc_context.npc_name)
        )

        inventario = (self.npc_data.get("inventario") or {})
        drafts = (inventario.get("drafts") or {})
        saved = (drafts.get("add_item_consumivel") or {})

        self.nome = discord.ui.TextInput(
            label=t("npc.inventory.consumable.fields.name", self.locale),
            placeholder=t("npc.inventory.consumable.placeholders.name", self.locale),
            required=True,
            max_length=120,
            default=saved.get("nome", "") or ""
        )
        self.quantidade = discord.ui.TextInput(
            label=t("npc.inventory.consumable.fields.quantity", self.locale),
            placeholder=t("npc.inventory.consumable.placeholders.quantity", self.locale),
            required=True,
            max_length=5,
            default=str(saved.get("quantidade", "1"))
        )
        self.efeito = discord.ui.TextInput(
            label=t("npc.inventory.consumable.fields.effect", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.inventory.consumable.placeholders.effect", self.locale),
            required=True,
            max_length=1000,
            default=saved.get("efeito", "") or ""
        )
        self.peso = discord.ui.TextInput(
            label=t("npc.inventory.consumable.fields.weight", self.locale),
            placeholder=t("npc.inventory.consumable.placeholders.weight", self.locale),
            required=False,
            max_length=30,
            default=saved.get("peso", "") or ""
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
                    t("npc.inventory.validation.qty_invalid_range", self.locale),
                    ephemeral=True
                )
                return
        except ValueError:
            await interaction.response.send_message(
                t("npc.inventory.validation.qty_invalid_int", self.locale),
                ephemeral=True
            )
            return

        inventario = self.npc_data.setdefault("inventario", {})
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
            t(
                "npc.inventory.consumable.added",
                self.locale,
                item=self.nome.value,
                qty=qtd,
                name=self.npc_context.npc_name
            ),
            ephemeral=True
        )
