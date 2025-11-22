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

class NPCGeneralInfoModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)

        super().__init__(
            npc_context,
            title=t("npc.general.title", self.locale, name=npc_context.npc_name)
        )

        general_info = self.npc_data.get("informacoes_gerais", {}) or {}

        self.nivel_rank = discord.ui.TextInput(
            label=t("npc.general.level.label", self.locale),
            placeholder=t("npc.general.level.ph", self.locale),
            default=general_info.get("nivel_rank") or "",
            required=False,
            max_length=50,
        )
        self.genero = discord.ui.TextInput(
            label=t("npc.general.gender.label", self.locale),
            placeholder=t("npc.general.gender.ph", self.locale),
            default=general_info.get("genero") or "",
            required=False,
            max_length=30,
        )
        self.idade = discord.ui.TextInput(
            label=t("npc.general.age.label", self.locale),
            placeholder=t("npc.general.age.ph", self.locale),
            default=general_info.get("idade") or "",
            required=False,
            max_length=20,
        )
        self.altura_peso = discord.ui.TextInput(
            label=t("npc.general.height_weight.label", self.locale),
            placeholder=t("npc.general.height_weight.ph", self.locale),
            default=general_info.get("altura_peso") or "",
            required=False,
            max_length=30,
        )

        self.add_item(self.nivel_rank)
        self.add_item(self.genero)
        self.add_item(self.idade)
        self.add_item(self.altura_peso)

    async def on_submit(self, interaction: discord.Interaction):
        info = self.npc_data.setdefault("informacoes_gerais", {})
        info["nivel_rank"] = self.nivel_rank.value
        info["genero"] = self.genero.value
        info["idade"] = self.idade.value
        info["altura_peso"] = self.altura_peso.value

        self.save()

        embed = discord.Embed(
            title=t("npc.general.embed.title", self.locale, name=self.npc_context.npc_name),
            description=t("npc.general.embed.desc", self.locale),
            color=discord.Color.blue(),
        )
        embed.add_field(
            name=t("npc.general.embed.level", self.locale),
            value=self.nivel_rank.value or t("misc.na", self.locale),
            inline=True,
        )
        embed.add_field(
            name=t("npc.general.embed.gender", self.locale),
            value=self.genero.value or t("misc.na", self.locale),
            inline=True,
        )
        embed.add_field(
            name=t("npc.general.embed.age", self.locale),
            value=self.idade.value or t("misc.na", self.locale),
            inline=True,
        )
        embed.add_field(
            name=t("npc.general.embed.height_weight", self.locale),
            value=self.altura_peso.value or t("misc.na", self.locale),
            inline=True,
        )
        embed.set_footer(text=t("npc.general.embed.footer", self.locale, user=interaction.user.display_name))

        await interaction.response.send_message(embed=embed, ephemeral=True)
