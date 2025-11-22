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

class SkiFallFisicosModal(discord.ui.Modal, title="❄️ Atributos Físicos (Valores Totais)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"

        self.forca = discord.ui.TextInput(
            label="Força Total",
            placeholder="Ex: 12",
            max_length=2,
            required=True
        )
        self.destreza = discord.ui.TextInput(
            label="Destreza Total",
            placeholder="Ex: 14",
            max_length=2,
            required=True
        )
        self.vigor = discord.ui.TextInput(
            label="Vigor Total",
            placeholder="Ex: 10",
            max_length=2,
            required=True
        )

        self.add_item(self.forca)
        self.add_item(self.destreza)
        self.add_item(self.vigor)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            forca_total = int(self.forca.value)
            destreza_total = int(self.destreza.value)
            vigor_total = int(self.vigor.value)

            if not all(1 <= val <= 2000 for val in [forca_total, destreza_total, vigor_total]):
                raise ValueError("Todos os valores devem ser números")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "forca_total": forca_total,
                "destreza_total": destreza_total,
                "vigor_total": vigor_total
            })

            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="❄️ Atributos Físicos Atualizados",
                description="**Valores totais (modificadores serão calculados depois)**",
                color=0x4682B4
            )
            embed.add_field(name="💪 Força Total", value=f"`{forca_total}`", inline=True)
            embed.add_field(name="🏃 Destreza Total", value=f"`{destreza_total}`", inline=True)
            embed.add_field(name="🛡️ Vigor Total", value=f"`{vigor_total}`", inline=True)
            embed.set_footer(text="Use /modificadores para ver os bônus calculados")

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
