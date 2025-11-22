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

class PlayerAtributosMentaisModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("attr_mental.title", self.locale))
        saved = (self.ficha.get("atributos") or {})
        self.inteligencia = discord.ui.TextInput(
            label=t("attr_mental.int.label", self.locale),
            placeholder=t("attr_mental.int.ph", self.locale),
            required=True,
            max_length=4,
            default=str(saved.get("inteligencia", "")) if saved.get("inteligencia") is not None else ""
        )
        self.sabedoria = discord.ui.TextInput(
            label=t("attr_mental.wis.label", self.locale),
            placeholder=t("attr_mental.wis.ph", self.locale),
            required=True,
            max_length=4,
            default=str(saved.get("sabedoria", "")) if saved.get("sabedoria") is not None else ""
        )
        self.carisma = discord.ui.TextInput(
            label=t("attr_mental.cha.label", self.locale),
            placeholder=t("attr_mental.cha.ph", self.locale),
            required=True,
            max_length=4,
            default=str(saved.get("carisma", "")) if saved.get("carisma") is not None else ""
        )

        self.add_item(self.inteligencia)
        self.add_item(self.sabedoria)
        self.add_item(self.carisma)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            inteligencia = int(self.inteligencia.value)
            sabedoria = int(self.sabedoria.value)
            carisma = int(self.carisma.value)

            for valor, key in [
                (inteligencia, "attr_mental.int.short"),
                (sabedoria, "attr_mental.wis.short"),
                (carisma, "attr_mental.cha.short"),
            ]:
                if not (1 <= valor <= 2000):
                    await interaction.response.send_message(
                        t("attr_mental.errors.range", self.locale, name=t(key, self.locale)),
                        ephemeral=True
                    )
                    return

        except ValueError:
            await interaction.response.send_message(
                t("attr_mental.errors.nan", self.locale),
                ephemeral=True
            )
            return

        attrs = self.ficha.setdefault("atributos", {})
        attrs.update({
            "inteligencia": inteligencia,
            "sabedoria": sabedoria,
            "carisma": carisma
        })
        self.save()

        embed = discord.Embed(
            title=t("attr_mental.saved.title", self.locale),
            color=discord.Color.purple()
        )
        embed.add_field(name=t("attr_mental.int.short", self.locale), value=inteligencia, inline=True)
        embed.add_field(name=t("attr_mental.wis.short", self.locale), value=sabedoria, inline=True)
        embed.add_field(name=t("attr_mental.cha.short", self.locale), value=carisma, inline=True)
        embed.set_footer(text=t("attr_mental.saved.footer", self.locale))

        await interaction.response.send_message(embed=embed, ephemeral=True)
