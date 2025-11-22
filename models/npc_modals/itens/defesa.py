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

class NPCAddItemDefenseModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(
            npc_context,
            title=t("npc.items.defense.title", self.locale, name=npc_context.npc_name),
        )

        inventario = (self.npc_data.get("inventario") or {})
        drafts = (inventario.get("drafts") or {})
        saved = (drafts.get("add_item_defesa") or {})

        self.nome = discord.ui.TextInput(
            label=t("npc.items.common.fields.name.label", self.locale),
            placeholder=t("npc.items.common.fields.name.ph", self.locale),
            required=True,
            max_length=120,
            default=saved.get("nome", "") or ""
        )
        self.quantidade = discord.ui.TextInput(
            label=t("npc.items.common.fields.quantity.label", self.locale),
            placeholder=t("npc.items.common.fields.quantity.ph", self.locale),
            required=True,
            max_length=5,
            default=str(saved.get("quantidade", "1"))
        )
        self.defesa = discord.ui.TextInput(
            label=t("npc.items.defense.fields.bonus.label", self.locale),
            placeholder=t("npc.items.defense.fields.bonus.ph", self.locale),
            required=True,
            max_length=60,
            default=saved.get("defesa", "") or ""
        )
        self.peso = discord.ui.TextInput(
            label=t("npc.items.common.fields.weight.label", self.locale),
            placeholder=t("npc.items.common.fields.weight.ph", self.locale),
            required=False,
            max_length=30,
            default=saved.get("peso", "") or ""
        )
        self.penalidade = discord.ui.TextInput(
            label=t("npc.items.defense.fields.penalty.label", self.locale),
            placeholder=t("npc.items.defense.fields.penalty.ph", self.locale),
            required=False,
            max_length=500,
            default=saved.get("penalidade", "") or ""
        )

        self.add_item(self.nome)
        self.add_item(self.quantidade)
        self.add_item(self.defesa)
        self.add_item(self.peso)
        self.add_item(self.penalidade)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            qtd = int(self.quantidade.value)
            if not (1 <= qtd <= 9999):
                return await interaction.response.send_message(
                    t("npc.items.common.errors.quantity_range", self.locale),
                    ephemeral=True
                )
        except ValueError:
            return await interaction.response.send_message(
                t("npc.items.common.errors.quantity_integer", self.locale),
                ephemeral=True
            )

        inventario = self.npc_data.setdefault("inventario", {})
        drafts = inventario.setdefault("drafts", {})
        defense_items = inventario.setdefault("defesa", [])

        drafts["add_item_defesa"] = {
            "nome": self.nome.value,
            "quantidade": qtd,
            "defesa": self.defesa.value,
            "peso": self.peso.value,
            "penalidade": self.penalidade.value
        }
        defense_items.append({
            "nome": self.nome.value,
            "quantidade": qtd,
            "defesa": self.defesa.value,
            "peso": self.peso.value,
            "penalidade": self.penalidade.value
        })

        self.save()

        await interaction.response.send_message(
            t("npc.items.defense.added", self.locale, item=self.nome.value, name=self.npc_context.npc_name),
            ephemeral=True
        )
