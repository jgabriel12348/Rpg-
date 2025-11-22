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

class PlayerBasicInfoModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title="📜 Informações Básicas do Personagem")

        saved = self.ficha.get("informacoes_basicas", {})
        self.titulo_apelido = discord.ui.TextInput(
            label=t("basic_info.nickname.label", self.locale),
            placeholder=t("basic_info.nickname.ph", self.locale),
            default=saved.get('titulo_apelido', {}),
            max_length=100
        )
        self.raca_especie = discord.ui.TextInput(
            label=t("basic_info.race.label", self.locale),
            placeholder=t("basic_info.race.ph", self.locale),
            default=saved.get('raca_especie', {}),
            max_length=50
        )
        self.classe_profissao = discord.ui.TextInput(
            label=t("basic_info.class.label", self.locale),
            placeholder=t("basic_info.class.ph", self.locale),
            default=saved.get('classe_profissao', {}),
            max_length=50
        )

        self.add_item(self.titulo_apelido)
        self.add_item(self.raca_especie)
        self.add_item(self.classe_profissao)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["informacoes_basicas"] = {
            "titulo_apelido": self.titulo_apelido.value,
            "raca_especie": self.raca_especie.value,
            "classe_profissao": self.classe_profissao.value,
        }
        self.save()
        embed = discord.Embed(
            title=t("basic_info.saved.title", self.locale),
            description=f"**{self.titulo_apelido.value or t('common.na', self.locale)}**",
            color=discord.Color.gold()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=t("basic_info.field.race", self.locale),
                        value=self.raca_especie.value or t("common.na", self.locale),
                        inline=True)
        embed.add_field(name=t("basic_info.field.class", self.locale),
                        value=self.classe_profissao.value or t("common.na", self.locale),
                        inline=True)
        embed.set_footer(text=t("basic_info.footer", self.locale))
        await interaction.response.send_message(embed=embed, ephemeral=True)
