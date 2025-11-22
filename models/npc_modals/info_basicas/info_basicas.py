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

class NPCBasicInfoModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(npc_context, title=t("npc.basic.title", self.locale, name=npc_context.npc_name))

        basic_info = self.npc_data.get("informacoes_basicas", {}) or {}

        self.titulo_apelido = discord.ui.TextInput(
            label=t("npc.basic.nickname.label", self.locale),
            placeholder=t("npc.basic.nickname.ph", self.locale),
            default=basic_info.get("titulo_apelido") or "",
            max_length=100,
            required=False
        )
        self.raca_especie = discord.ui.TextInput(
            label=t("npc.basic.race.label", self.locale),
            placeholder=t("npc.basic.race.ph", self.locale),
            default=basic_info.get("raca_especie") or "",
            max_length=50,
            required=False
        )
        self.classe_profissao = discord.ui.TextInput(
            label=t("npc.basic.class.label", self.locale),
            placeholder=t("npc.basic.class.ph", self.locale),
            default=basic_info.get("classe_profissao") or "",
            max_length=50,
            required=False
        )

        self.add_item(self.titulo_apelido)
        self.add_item(self.raca_especie)
        self.add_item(self.classe_profissao)

    async def on_submit(self, interaction: discord.Interaction):
        info = self.npc_data.setdefault("informacoes_basicas", {})
        info["titulo_apelido"] = self.titulo_apelido.value
        info["raca_especie"] = self.raca_especie.value
        info["classe_profissao"] = self.classe_profissao.value

        self.save()

        embed = discord.Embed(
            title=t("npc.basic.embed.title", self.locale, name=self.npc_context.npc_name),
            description=t(
                "npc.basic.embed.desc",
                self.locale,
                nickname=(self.titulo_apelido.value or t("misc.none", self.locale))
            ),
            color=discord.Color.gold()
        )
        embed.add_field(
            name=t("npc.basic.embed.race", self.locale),
            value=self.raca_especie.value or t("misc.uninformed", self.locale),
            inline=True
        )
        embed.add_field(
            name=t("npc.basic.embed.class", self.locale),
            value=self.classe_profissao.value or t("misc.uninformed", self.locale),
            inline=True
        )
        embed.set_footer(text=t("npc.basic.embed.footer", self.locale, user=interaction.user.display_name))

        await interaction.response.send_message(embed=embed, ephemeral=True)
