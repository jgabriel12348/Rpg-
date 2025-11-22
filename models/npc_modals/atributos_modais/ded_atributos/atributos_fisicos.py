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

class NPCDnDAtributosFisicosModal(NPCModalBase):
    def __init__(self, npc_context, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(npc_context, title=t("npc.attr_phys.title", self.locale, name=npc_context.npc_name))

        atributos = self.npc_data.get("atributos", {})

        self.forca = self._input("npc.attr_phys.str", atributos.get("Força"))
        self.destreza = self._input("npc.attr_phys.dex", atributos.get("Destreza"))
        self.constituicao = self._input("npc.attr_phys.con", atributos.get("Constituição"))

        self.add_item(self.forca)
        self.add_item(self.destreza)
        self.add_item(self.constituicao)

    def _input(self, base_key: str, default_value):
        return discord.ui.TextInput(
            label=t(f"{base_key}.label", self.locale),
            placeholder=t("npc.attr_phys.ph", self.locale),
            default=str(default_value or ""),
            required=False,
            max_length=2
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
            raise ValueError(t("npc.attr_phys.errors.range", self.locale, name=name_disp))
        return v

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valores_int = {}

            v_for = self._parse_optional_int(self.forca.value, "npc.attr_phys.str.short")
            if v_for is not None:
                valores_int["Força"] = v_for

            v_des = self._parse_optional_int(self.destreza.value, "npc.attr_phys.dex.short")
            if v_des is not None:
                valores_int["Destreza"] = v_des

            v_con = self._parse_optional_int(self.constituicao.value, "npc.attr_phys.con.short")
            if v_con is not None:
                valores_int["Constituição"] = v_con

            # aplica no JSON apenas os campos enviados
            if valores_int:
                self.npc_data.setdefault("atributos", {})
                self.npc_data["atributos"].update(valores_int)
                self.save()

            embed = discord.Embed(
                title=t("npc.attr_phys.saved.title", self.locale, name=self.npc_context.npc_name),
                description=t("npc.attr_phys.saved.sys", self.locale),
                color=discord.Color.red()
            )
            for nome_pt, chave_json in [
                (t("npc.attr_phys.str.short", self.locale), "Força"),
                (t("npc.attr_phys.dex.short", self.locale), "Destreza"),
                (t("npc.attr_phys.con.short", self.locale), "Constituição"),
            ]:
                if chave_json in valores_int:
                    embed.add_field(name=nome_pt, value=f"`{valores_int[chave_json]}`", inline=True)

            embed.set_footer(text=t("npc.attr_phys.saved.footer", self.locale, user=interaction.user.display_name))
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            await interaction.response.send_message(
                t("npc.attr_phys.errors.prefix", self.locale, msg=str(e)),
                ephemeral=True
            )
