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

class PlayerAtributosFisicosModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("attr_phys.title", self.locale))
        saved = (self.ficha.get("atributos") or {})
        self.forca = discord.ui.TextInput(
            label=t("attr_phys.str.label", self.locale),
            placeholder=t("attr_phys.str.ph", self.locale),
            required=True,
            max_length=4,
            default=str(saved.get("forca", "")) if saved.get("forca") is not None else ""
        )
        self.destreza = discord.ui.TextInput(
            label=t("attr_phys.dex.label", self.locale),
            placeholder=t("attr_phys.dex.ph", self.locale),
            required=True,
            max_length=4,
            default=str(saved.get("destreza", "")) if saved.get("destreza") is not None else ""
        )
        self.constituicao = discord.ui.TextInput(
            label=t("attr_phys.con.label", self.locale),
            placeholder=t("attr_phys.con.ph", self.locale),
            required=True,
            max_length=4,
            default=str(saved.get("constituicao", "")) if saved.get("constituicao") is not None else ""
        )

        self.add_item(self.forca)
        self.add_item(self.destreza)
        self.add_item(self.constituicao)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            forca = int(self.forca.value)
            destreza = int(self.destreza.value)
            constituicao = int(self.constituicao.value)

            for valor, key in [
                (forca, "attr_phys.str.short"),
                (destreza, "attr_phys.dex.short"),
                (constituicao, "attr_phys.con.short"),
            ]:
                if not (1 <= valor <= 2000):
                    await interaction.response.send_message(
                        t("attr_phys.errors.range", self.locale, name=t(key, self.locale)),
                        ephemeral=True
                    )
                    return

        except ValueError:
            await interaction.response.send_message(
                t("attr_phys.errors.nan", self.locale),
                ephemeral=True
            )
            return
        attrs = self.ficha.setdefault("atributos", {})
        attrs.update({
            "forca": forca,
            "destreza": destreza,
            "constituicao": constituicao
        })
        self.save()

        embed = discord.Embed(
            title=t("attr_phys.saved.title", self.locale),
            color=discord.Color.green()
        )
        embed.add_field(name=t("attr_phys.str.short", self.locale), value=forca, inline=True)
        embed.add_field(name=t("attr_phys.dex.short", self.locale), value=destreza, inline=True)
        embed.add_field(name=t("attr_phys.con.short", self.locale), value=constituicao, inline=True)
        embed.set_footer(text=t("attr_phys.saved.footer", self.locale))

        await interaction.response.send_message(embed=embed, ephemeral=True)
