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

class PlayerCombatInfoModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("combat_info.title", self.locale))
        saved = (self.ficha.get("informacoes_combate") or {})
        vida_default = ""
        if saved.get("vida_atual") is not None and saved.get("vida_maxima") is not None:
            vida_default = f"{saved.get('vida_atual')}/{saved.get('vida_maxima')}"

        magia_default = ""
        if saved.get("magia_atual") is not None and saved.get("magia_maxima") is not None:
            magia_default = f"{saved.get('magia_atual')}/{saved.get('magia_maxima')}"

        self.vida = discord.ui.TextInput(
            label=t("combat_info.hp.label", self.locale),
            placeholder=t("combat_info.hp.ph", self.locale),
            max_length=21,
            default=vida_default
        )
        self.magia = discord.ui.TextInput(
            label=t("combat_info.mp.label", self.locale),
            placeholder=t("combat_info.mp.ph", self.locale),
            max_length=21,
            default=magia_default
        )
        self.defesa = discord.ui.TextInput(
            label=t("combat_info.def.label", self.locale),
            placeholder=t("combat_info.def.ph", self.locale),
            max_length=100,
            default=saved.get("defesa", "") or ""
        )
        self.resistencia_magica = discord.ui.TextInput(
            label=t("combat_info.mr.label", self.locale),
            placeholder=t("combat_info.mr.ph", self.locale),
            max_length=100,
            default=saved.get("resistencia_magica", "") or ""
        )
        self.iniciativa = discord.ui.TextInput(
            label=t("combat_info.init.label", self.locale),
            placeholder=t("combat_info.init.ph", self.locale),
            max_length=50,
            default=saved.get("iniciativa", "") or ""
        )

        self.add_item(self.vida)
        self.add_item(self.magia)
        self.add_item(self.defesa)
        self.add_item(self.resistencia_magica)
        self.add_item(self.iniciativa)

    async def on_submit(self, interaction: discord.Interaction):
        na = t("common.na", self.locale)

        try:
            vida_parts = self.vida.value.replace(" ", "").split('/')
            if len(vida_parts) != 2:
                raise ValueError("hp_fmt")

            vida_atual = int(vida_parts[0])
            vida_maxima = int(vida_parts[1])

            if vida_atual < 0 or vida_maxima < 0:
                await interaction.response.send_message(
                    t("combat_info.errors.hp_negative", self.locale),
                    ephemeral=True
                )
                return
            if vida_atual > vida_maxima:
                await interaction.response.send_message(
                    t("combat_info.errors.hp_overmax", self.locale),
                    ephemeral=True
                )
                return

            magia_parts = self.magia.value.replace(" ", "").split('/')
            if len(magia_parts) != 2:
                raise ValueError("mp_fmt")

            magia_atual = int(magia_parts[0])
            magia_maxima = int(magia_parts[1])

            if magia_atual < 0 or magia_maxima < 0:
                await interaction.response.send_message(
                    t("combat_info.errors.mp_negative", self.locale),
                    ephemeral=True
                )
                return
            if magia_atual > magia_maxima:
                await interaction.response.send_message(
                    t("combat_info.errors.mp_overmax", self.locale),
                    ephemeral=True
                )
                return

        except ValueError as e:
            await interaction.response.send_message(
                t("combat_info.errors.format_hpmp", self.locale),
                ephemeral=True
            )
            return

        self.ficha["informacoes_combate"] = {
            "vida_atual": vida_atual,
            "vida_maxima": vida_maxima,
            "magia_atual": magia_atual,
            "magia_maxima": magia_maxima,
            "defesa": self.defesa.value,
            "resistencia_magica": self.resistencia_magica.value,
            "iniciativa": self.iniciativa.value,
        }
        self.save()

        embed = discord.Embed(
            title=t("combat_info.saved.title", self.locale),
            description=t("combat_info.saved.desc", self.locale),
            color=discord.Color.red()
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
        embed.add_field(
            name=t("combat_info.field.hp", self.locale),
            value=f"`{vida_atual} / {vida_maxima}`",
            inline=True
        )
        embed.add_field(
            name=t("combat_info.field.mp", self.locale),
            value=f"`{magia_atual} / {magia_maxima}`",
            inline=True
        )
        embed.add_field(
            name=t("combat_info.field.def", self.locale),
            value=self.defesa.value or na,
            inline=False
        )
        embed.add_field(
            name=t("combat_info.field.mr", self.locale),
            value=self.resistencia_magica.value or na,
            inline=False
        )
        embed.add_field(
            name=t("combat_info.field.init", self.locale),
            value=self.iniciativa.value or na,
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
