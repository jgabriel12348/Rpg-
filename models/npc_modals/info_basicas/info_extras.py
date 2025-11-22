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

class NPCExtraInfoModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)

        super().__init__(
            npc_context,
            title=t("npc.extra.title", self.locale, name=npc_context.npc_name)
        )

        extra_info = self.npc_data.get("informacoes_extras", {}) or {}

        self.idiomas = discord.ui.TextInput(
            label=t("npc.extra.languages.label", self.locale),
            placeholder=t("npc.extra.languages.ph", self.locale),
            default=extra_info.get("idiomas") or "",
            required=False,
            max_length=1000,
        )
        self.personalidade = discord.ui.TextInput(
            label=t("npc.extra.personality.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.extra.personality.ph", self.locale),
            default=extra_info.get("personalidade") or "",
            required=False,
            max_length=1500,
        )
        self.aparencia = discord.ui.TextInput(
            label=t("npc.extra.appearance.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.extra.appearance.ph", self.locale),
            default=extra_info.get("aparencia") or "",
            required=False,
            max_length=1500,
        )
        self.background = discord.ui.TextInput(
            label=t("npc.extra.background.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.extra.background.ph", self.locale),
            default=extra_info.get("background") or "",
            required=False,
            max_length=2000,
        )
        self.origem = discord.ui.TextInput(
            label=t("npc.extra.origin.label", self.locale),
            placeholder=t("npc.extra.origin.ph", self.locale),
            default=extra_info.get("origem") or "",
            required=False,
            max_length=200,
        )

        self.add_item(self.idiomas)
        self.add_item(self.personalidade)
        self.add_item(self.aparencia)
        self.add_item(self.background)
        self.add_item(self.origem)

    async def on_submit(self, interaction: discord.Interaction):
        info = self.npc_data.setdefault("informacoes_extras", {})
        info["idiomas"] = self.idiomas.value
        info["personalidade"] = self.personalidade.value
        info["aparencia"] = self.aparencia.value
        info["background"] = self.background.value
        info["origem"] = self.origem.value

        self.save()

        embed = discord.Embed(
            title=t("npc.extra.embed.title", self.locale, name=self.npc_context.npc_name),
            description=t("npc.extra.embed.desc", self.locale),
            color=discord.Color.green(),
        )
        embed.add_field(
            name=t("npc.extra.embed.languages", self.locale),
            value=self.idiomas.value or t("misc.na", self.locale),
            inline=False,
        )
        embed.add_field(
            name=t("npc.extra.embed.personality", self.locale),
            value=self.personalidade.value or t("misc.na", self.locale),
            inline=False,
        )
        embed.set_footer(text=t("npc.extra.embed.footer", self.locale, user=interaction.user.display_name))

        await interaction.response.send_message(embed=embed, ephemeral=True)
