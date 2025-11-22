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

class PlayerMovementInfoModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("movement_info.title", self.locale))

        saved = (self.ficha.get("informacoes_deslocamento") or {})

        self.velocidade = discord.ui.TextInput(
            label=t("movement_info.speed.label", self.locale),
            placeholder=t("movement_info.speed.ph", self.locale),
            max_length=100,
            default=saved.get("velocidade", "") or "",
            required=False
        )

        self.regeneracao = discord.ui.TextInput(
            label=t("movement_info.regen.label", self.locale),
            placeholder=t("movement_info.regen.ph", self.locale),
            max_length=100,
            default=saved.get("regeneracao", "") or "",
            required=False
        )

        self.resistencias = discord.ui.TextInput(
            label=t("movement_info.resist.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("movement_info.resist.ph", self.locale),
            default=saved.get("resistencias", "") or "",
            required=False
        )

        self.fraquezas = discord.ui.TextInput(
            label=t("movement_info.weak.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("movement_info.weak.ph", self.locale),
            default=saved.get("fraquezas", "") or "",
            required=False
        )

        self.imunidades = discord.ui.TextInput(
            label=t("movement_info.immune.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("movement_info.immune.ph", self.locale),
            default=saved.get("imunidades", "") or "",
            required=False
        )

        self.add_item(self.velocidade)
        self.add_item(self.regeneracao)
        self.add_item(self.resistencias)
        self.add_item(self.fraquezas)
        self.add_item(self.imunidades)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["informacoes_deslocamento"] = {
            "velocidade": self.velocidade.value,
            "regeneracao": self.regeneracao.value,
            "resistencias": self.resistencias.value,
            "fraquezas": self.fraquezas.value,
            "imunidades": self.imunidades.value,
        }
        self.save()

        na = t("common.na", self.locale)

        embed = discord.Embed(
            title=t("movement_info.saved.title", self.locale),
            description=t("movement_info.saved.desc", self.locale),
            color=discord.Color.green()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.add_field(name=t("movement_info.field.speed", self.locale), value=self.velocidade.value or na, inline=False)
        embed.add_field(name=t("movement_info.field.regen", self.locale), value=self.regeneracao.value or na, inline=False)
        embed.add_field(name=t("movement_info.field.resist", self.locale), value=self.resistencias.value or na, inline=False)
        embed.add_field(name=t("movement_info.field.weak", self.locale), value=self.fraquezas.value or na, inline=False)
        embed.add_field(name=t("movement_info.field.immune", self.locale), value=self.imunidades.value or na, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
