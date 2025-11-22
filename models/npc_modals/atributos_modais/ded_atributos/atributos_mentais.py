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

class NPCDnDAtributosMentaisModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(npc_context, title=t("npc.attr_mental.title", self.locale, name=npc_context.npc_name))

        atributos = self.npc_data.get("atributos", {})

        self.inteligencia = self._input("npc.attr_mental.int", atributos.get("Inteligência"))
        self.sabedoria    = self._input("npc.attr_mental.wis", atributos.get("Sabedoria"))
        self.carisma      = self._input("npc.attr_mental.cha", atributos.get("Carisma"))

        self.add_item(self.inteligencia)
        self.add_item(self.sabedoria)
        self.add_item(self.carisma)

    def _input(self, base_key: str, default_value):
        return discord.ui.TextInput(
            label=t(f"{base_key}.label", self.locale),
            placeholder=t("npc.attr_mental.ph", self.locale),
            default=str(default_value or ""),
            required=False,
            max_length=2  # 1..30
        )

    def _parse_optional_int(self, value: str, display_name_key: str):
        if not value:
            return None
        try:
            v = int(value)
        except ValueError:
            raise ValueError(t("common.errors.number_required", self.locale))
        if not 1 <= v <= 30:
            name_disp = t(display_name_key, self.locale)
            raise ValueError(t("npc.attr_mental.errors.range", self.locale, name=name_disp))
        return v

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valores_int = {}

            v_int = self._parse_optional_int(self.inteligencia.value, "npc.attr_mental.int.short")
            if v_int is not None:
                valores_int["Inteligência"] = v_int

            v_wis = self._parse_optional_int(self.sabedoria.value, "npc.attr_mental.wis.short")
            if v_wis is not None:
                valores_int["Sabedoria"] = v_wis

            v_cha = self._parse_optional_int(self.carisma.value, "npc.attr_mental.cha.short")
            if v_cha is not None:
                valores_int["Carisma"] = v_cha

            if valores_int:
                self.npc_data.setdefault("atributos", {})
                self.npc_data["atributos"].update(valores_int)
                self.save()

            embed = discord.Embed(
                title=t("npc.attr_mental.saved.title", self.locale, name=self.npc_context.npc_name),
                description=t("npc.attr_mental.saved.sys", self.locale),
                color=discord.Color.purple()
            )
            mapping_label_key = [
                (t("npc.attr_mental.int.short", self.locale), "Inteligência"),
                (t("npc.attr_mental.wis.short", self.locale), "Sabedoria"),
                (t("npc.attr_mental.cha.short", self.locale), "Carisma"),
            ]
            for label, json_key in mapping_label_key:
                if json_key in valores_int:
                    embed.add_field(name=label, value=f"`{valores_int[json_key]}`", inline=True)

            embed.set_footer(text=t("npc.attr_mental.saved.footer", self.locale, user=interaction.user.display_name))
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            await interaction.response.send_message(
                t("npc.attr_mental.errors.prefix", self.locale, msg=str(e)),
                ephemeral=True
            )
