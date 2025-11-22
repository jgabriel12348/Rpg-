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
from utils.player_utils import save_player_sheet, load_player_sheet

class CyberpunkSociaisModal(discord.ui.Modal, title="🌐 Atributos Sociais (Cyberpunk)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        self.atratividade = discord.ui.TextInput(
            label="Atratividade (ATR)",
            placeholder="2-8",
            required=True,
            max_length=1
        )

        self.sorte = discord.ui.TextInput(
            label="Sorte (SOR)",
            placeholder="2-8",
            required=True,
            max_length=1
        )

        self.add_item(self.atratividade)
        self.add_item(self.sorte)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            atratividade_val = int(self.atratividade.value)
            sorte_val = int(self.sorte.value)

            if not all(2 <= val <= 800 for val in [atratividade_val, sorte_val]):
                raise ValueError("Atributos devem estar entre 2 e 8")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "atratividade": atratividade_val,
                "sorte": sorte_val
            })

            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="🌐 Atributos Sociais Atualizados",
                description="**Cyberpunk RED**",
                color=0x9370DB
            )

            embed.add_field(name="🥵 Atratividade (ATR)", value=f"`{atratividade_val}`", inline=True)
            embed.add_field(name="🍀 Sorte (SOR)", value=f"`{sorte_val}`", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            error_msg = "❌ Erro: "
            if "invalid literal" in str(e):
                error_msg += "Digite apenas números de 2 a 8!"
            else:
                error_msg += str(e)

            await interaction.response.send_message(
                error_msg,
                ephemeral=True,
                delete_after=10
            )
