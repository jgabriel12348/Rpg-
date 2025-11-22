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

class PlayerAtributosFisicosModal(discord.ui.Modal, title="💪 Atributos Físicos (Call of Cthulhu)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"

    forca = discord.ui.TextInput(
        label="Força (FOR)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    destreza = discord.ui.TextInput(
        label="Destreza (DES)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    constituicao = discord.ui.TextInput(
        label="Constituição (CON)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    tamanho = discord.ui.TextInput(
        label="Tamanho (TAM)",
        placeholder="Valor entre 1-100",
        required=True,
        max_length=3
    )

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            forca_val = int(self.forca.value)
            destreza_val = int(self.destreza.value)
            constituicao_val = int(self.constituicao.value)
            tamanho_val = int(self.tamanho.value)
            if not all(1 <= val <= 1000 for val in [forca_val, destreza_val, constituicao_val, tamanho_val]):
                raise ValueError("Valores devem estar entre 1 e 100")
            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "forca": forca_val,
                "destreza": destreza_val,
                "constituicao": constituicao_val,
                "tamanho": tamanho_val
            })
            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="💪 Atributos Físicos Atualizados",
                description="**Call of Cthulhu**",
                color=0x8B0000
            )
            embed.add_field(name="Força (FOR)", value=f"`{forca_val}`", inline=True)
            embed.add_field(name="Destreza (DES)", value=f"`{destreza_val}`", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Espaçador
            embed.add_field(name="Constituição (CON)", value=f"`{constituicao_val}`", inline=True)
            embed.add_field(name="Tamanho (TAM)", value=f"`{tamanho_val}`", inline=True)
            embed.set_footer(text="Use /atributos-mentais para continuar")

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
