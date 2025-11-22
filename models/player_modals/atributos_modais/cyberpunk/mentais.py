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

class CyberpunkMentaisModal(discord.ui.Modal, title="💿 Atributos Mentais (Cyberpunk)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        self.inteligencia = discord.ui.TextInput(
            label="Inteligência (INT)",
            placeholder="2-8",
            required=True,
            max_length=1
        )

        self.frio = discord.ui.TextInput(
            label="Frio (FRI)",
            placeholder="2-8",
            required=True,
            max_length=1
        )

        self.add_item(self.inteligencia)
        self.add_item(self.frio)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            inteligencia_val = int(self.inteligencia.value)
            frio_val = int(self.frio.value)

            if not all(2 <= val <= 800 for val in [inteligencia_val, frio_val]):
                raise ValueError("Atributos devem estar entre 2 e 8")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "inteligencia": inteligencia_val,
                "frio": frio_val
            })

            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="💿 Atributos Mentais Atualizados",
                description="**Cyberpunk RED**",
                color=0x00BFFF
            )

            embed.add_field(name="🧠 Inteligência (INT)", value=f"`{inteligencia_val}`", inline=True)
            embed.add_field(name="❄️ Frio (FRI)", value=f"`{frio_val}`", inline=True)

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
