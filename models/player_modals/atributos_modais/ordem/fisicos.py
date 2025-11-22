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

class OrdemFisicosModal(discord.ui.Modal, title="👁️ Atributos Físicos/Paranormais"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        self.forca = discord.ui.TextInput(
            label="Força (FOR)",
            placeholder="Valor",
            required=True,
            max_length=1
        )

        self.agilidade = discord.ui.TextInput(
            label="Agilidade (AGI)",
            placeholder="Valor",
            required=True,
            max_length=1
        )

        self.vigor = discord.ui.TextInput(
            label="Vigor (VIG)",
            placeholder="Valor",
            required=True,
            max_length=1
        )

        self.presenca = discord.ui.TextInput(
            label="Presença (PRE)",
            placeholder="Valor",
            required=True,
            max_length=1
        )
        self.add_item(self.forca)
        self.add_item(self.agilidade)
        self.add_item(self.vigor)
        self.add_item(self.presenca)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            forca_val = int(self.forca.value)
            agilidade_val = int(self.agilidade.value)
            vigor_val = int(self.vigor.value)
            presenca_val = int(self.presenca.value)

            if not all(1 <= val <= 5000 for val in [forca_val, agilidade_val, vigor_val, presenca_val]):
                raise ValueError("Níveis devem estar entre 1 e 5")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "forca": forca_val,
                "agilidade": agilidade_val,
                "vigor": vigor_val,
                "presenca": presenca_val
            })

            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="👁️ Atributos Atualizados",
                description="**Ordem Paranormal RPG**",
                color=0x4B0082
            )

            embed.add_field(name="💪 Força (FOR)", value=f"`{forca_val}`", inline=True)
            embed.add_field(name="🤸 Agilidade (AGI)", value=f"`{agilidade_val}`", inline=True)
            embed.add_field(name="🏋️ Vigor (VIG)", value=f"`{vigor_val}`", inline=True)
            embed.add_field(name="🌌 Presença (PRE)", value=f"`{presenca_val}`", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            error_msg = "❌ Erro: "
            if "invalid literal" in str(e):
                error_msg += "Digite apenas números de 1 a 5!"
            else:
                error_msg += str(e)

            await interaction.response.send_message(
                error_msg,
                ephemeral=True,
                delete_after=10
            )
