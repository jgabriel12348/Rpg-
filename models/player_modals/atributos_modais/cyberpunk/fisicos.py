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

class CyberpunkFisicosModal(discord.ui.Modal, title="⚙️ Atributos Físicos (Cyberpunk)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        self.corpo = discord.ui.TextInput(
            label="Corpo (COR)",
            placeholder="2-8 (Baseado no Tipo Corporal)",
            required=True,
            max_length=1
        )

        self.reflexos = discord.ui.TextInput(
            label="Reflexos (REF)",
            placeholder="2-8",
            required=True,
            max_length=1
        )

        self.tecnica = discord.ui.TextInput(
            label="Técnica (TEC)",
            placeholder="2-8",
            required=True,
            max_length=1
        )

        self.add_item(self.corpo)
        self.add_item(self.reflexos)
        self.add_item(self.tecnica)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            corpo_val = int(self.corpo.value)
            reflexos_val = int(self.reflexos.value)
            tecnica_val = int(self.tecnica.value)

            if not all(2 <= val <= 800 for val in [corpo_val, reflexos_val, tecnica_val]):
                raise ValueError("Atributos devem estar entre 2 e 8")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "corpo": corpo_val,
                "reflexos": reflexos_val,
                "tecnica": tecnica_val
            })

            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="⚙️ Atributos Físicos Atualizados",
                description="**Cyberpunk RED**",
                color=0xFF4500
            )

            embed.add_field(name="🦾 Corpo (COR)", value=f"`{corpo_val}`", inline=True)
            embed.add_field(name="⚡ Reflexos (REF)", value=f"`{reflexos_val}`", inline=True)
            embed.add_field(name="🔧 Técnica (TEC)", value=f"`{tecnica_val}`", inline=True)

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
