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

class PlayerExtraInfoModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("extra_info.title", self.locale))

        saved = (self.ficha.get("informacoes_extras") or {})

        self.idiomas = discord.ui.TextInput(
            label=t("extra_info.langs.label", self.locale),
            placeholder=t("extra_info.langs.ph", self.locale),
            default=saved.get("idiomas", "") or "",
            required=False,
            max_length=500
        )
        self.personalidade = discord.ui.TextInput(
            label=t("extra_info.personality.label", self.locale),
            placeholder=t("extra_info.personality.ph", self.locale),
            default=saved.get("personalidade", "") or "",
            required=False,
            max_length=500
        )
        self.aparencia = discord.ui.TextInput(
            label=t("extra_info.appearance.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("extra_info.appearance.ph", self.locale),
            default=saved.get("aparencia", "") or "",
            required=False,
            max_length=1500
        )
        self.background = discord.ui.TextInput(
            label=t("extra_info.background.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("extra_info.background.ph", self.locale),
            default=saved.get("background", "") or "",
            required=False,
            max_length=3000
        )
        self.origem = discord.ui.TextInput(
            label=t("extra_info.origin.label", self.locale),
            placeholder=t("extra_info.origin.ph", self.locale),
            default=saved.get("origem", "") or "",
            required=False,
            max_length=200
        )

        self.add_item(self.idiomas)
        self.add_item(self.personalidade)
        self.add_item(self.aparencia)
        self.add_item(self.background)
        self.add_item(self.origem)

    async def on_submit(self, interaction: discord.Interaction):
        self.ficha["informacoes_extras"] = {
            "idiomas": self.idiomas.value,
            "personalidade": self.personalidade.value,
            "aparencia": self.aparencia.value,
            "background": self.background.value,
            "origem": self.origem.value
        }
        self.save()

        na = t("common.na", self.locale)

        embed = discord.Embed(
            title=t("extra_info.saved.title", self.locale),
            description=t("extra_info.saved.desc", self.locale, character=self.character_name),
            color=discord.Color.green()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        embed.add_field(
            name=t("extra_info.field.langs", self.locale),
            value=self.idiomas.value or na,
            inline=True
        )
        embed.add_field(
            name=t("extra_info.field.personality", self.locale),
            value=self.personalidade.value or na,
            inline=True
        )

        apar = self.aparencia.value.strip()
        if apar:
            embed.add_field(
                name=t("extra_info.field.appearance", self.locale),
                value=apar,
                inline=False
            )
            if apar.lower().startswith(("http://", "https://")):
                embed.set_image(url=apar)
        else:
            embed.add_field(
                name=t("extra_info.field.appearance", self.locale),
                value=na,
                inline=False
            )

        embed.add_field(
            name=t("extra_info.field.background", self.locale),
            value=self.background.value or na,
            inline=False
        )
        embed.add_field(
            name=t("extra_info.field.origin", self.locale),
            value=self.origem.value or na,
            inline=True
        )
        embed.set_footer(text=t("extra_info.footer", self.locale))

        await interaction.response.send_message(embed=embed, ephemeral=True)
