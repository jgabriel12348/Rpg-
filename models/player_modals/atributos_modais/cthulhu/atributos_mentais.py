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
from utils.player_utils import load_player_sheet, save_player_sheet

class PlayerAtributosMentaisModal(discord.ui.Modal, title="🧠 Atributos Mentais (Call of Cthulhu)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"

    inteligencia = discord.ui.TextInput(
        label="Inteligência (INT)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    educacao = discord.ui.TextInput(
        label="Educação (EDU)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    poder = discord.ui.TextInput(
        label="Poder (POW)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    aparencia = discord.ui.TextInput(
        label="Aparência (APA)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            int_val = int(self.inteligencia.value)
            edu_val = int(self.educacao.value)
            pow_val = int(self.poder.value)
            apa_val = int(self.aparencia.value)

            if not all(1 <= val <= 1000 for val in [int_val, edu_val, pow_val, apa_val]):
                raise ValueError("Todos os valores devem estar entre 1 e 100")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "inteligencia": int_val,
                "educacao": edu_val,
                "poder": pow_val,
                "aparencia": apa_val
            })
            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="🧠 Atributos Mentais Atualizados",
                description="**Call of Cthulhu**",
                color=0x5e35b1
            )
            embed.add_field(name="Inteligência (INT)", value=f"`{int_val}`", inline=True)
            embed.add_field(name="Educação (EDU)", value=f"`{edu_val}`", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Espaçador
            embed.add_field(name="Poder (POW)", value=f"`{pow_val}`", inline=True)
            embed.add_field(name="Aparência (APA)", value=f"`{apa_val}`", inline=True)
            embed.set_footer(text="Use /habilidades para continuar")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            error_msg = "❌ Erro: "
            if "invalid literal" in str(e):
                error_msg += "Digite apenas números válidos!"
            else:
                error_msg += str(e)

            await interaction.response.send_message(
                error_msg,
                ephemeral=True,
                delete_after=10
            )
