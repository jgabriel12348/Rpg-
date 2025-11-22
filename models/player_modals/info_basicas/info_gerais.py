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

class PlayerGeneralInfoModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("general_info.title", self.locale))

        saved = (self.ficha.get("informacoes_gerais") or {})

        self.nivel_rank = discord.ui.TextInput(
            label=t("general_info.level.label", self.locale),
            placeholder=t("general_info.level.ph", self.locale),
            required=False, max_length=50,
            default=saved.get("nivel_rank", "") or ""
        )
        self.genero = discord.ui.TextInput(
            label=t("general_info.gender.label", self.locale),
            placeholder=t("general_info.gender.ph", self.locale),
            required=False, max_length=30,
            default=saved.get("genero", "") or ""
        )
        self.idade = discord.ui.TextInput(
            label=t("general_info.age.label", self.locale),
            placeholder=t("general_info.age.ph", self.locale),
            required=False, max_length=20,
            default=saved.get("idade", "") or ""
        )
        self.altura_peso = discord.ui.TextInput(
            label=t("general_info.hw.label", self.locale),
            placeholder=t("general_info.hw.ph", self.locale),
            required=False, max_length=30,
            default=saved.get("altura_peso", "") or ""
        )

        self.add_item(self.nivel_rank)
        self.add_item(self.genero)
        self.add_item(self.idade)
        self.add_item(self.altura_peso)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["informacoes_gerais"] = {
            "nivel_rank": self.nivel_rank.value,
            "genero": self.genero.value,
            "idade": self.idade.value,
            "altura_peso": self.altura_peso.value,
        }
        self.save()

        na = t("common.na", self.locale)

        embed = discord.Embed(
            title=t("general_info.saved.title", self.locale),
            description=t(
                "general_info.saved.desc",
                self.locale,
                character=getattr(self, "character_name", na)
            ),
            color=discord.Color.blue()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(name=t("general_info.field.level", self.locale), value=self.nivel_rank.value or na, inline=True)
        embed.add_field(name=t("general_info.field.gender", self.locale), value=self.genero.value or na, inline=True)
        embed.add_field(name=t("general_info.field.age", self.locale), value=self.idade.value or na, inline=True)
        embed.add_field(name=t("general_info.field.hw", self.locale), value=self.altura_peso.value or na, inline=True)
        embed.set_footer(text=t("general_info.footer", self.locale))  # adicione no JSON se quiser personalizar

        await interaction.response.send_message(embed=embed, ephemeral=True)
