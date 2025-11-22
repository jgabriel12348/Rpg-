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

class VampiroAtributosMentaisModal(discord.ui.Modal, title="🧠 Atributos Mentais (Vampiro)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        self.percepcao = discord.ui.TextInput(
            label="Percepção (PER)",
            placeholder="Valor",
            required=True,
            max_length=1
        )
        self.inteligencia = discord.ui.TextInput(
            label="Inteligência (INT)",
            placeholder="Valor",
            required=True,
            max_length=1
        )
        self.raciocinio = discord.ui.TextInput(
            label="Raciocínio (RAC)",
            placeholder="Valor",
            required=True,
            max_length=1
        )

        self.add_item(self.percepcao)
        self.add_item(self.inteligencia)
        self.add_item(self.raciocinio)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            percepcao_val = int(self.percepcao.value)
            inteligencia_val = int(self.inteligencia.value)
            raciocinio_val = int(self.raciocinio.value)

            if not all(1 <= val <= 5000 for val in [percepcao_val, inteligencia_val, raciocinio_val]):
                raise ValueError("Todos os atributos devem estar entre 1 e 5")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "percepcao": percepcao_val,
                "inteligencia": inteligencia_val,
                "raciocinio": raciocinio_val
            })
            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="🧠 Atributos Mentais Atualizados",
                description="**Vampiro: A Máscara**",
                color=0x1E3A8A
            )
            embed.add_field(name="👀 Percepção (PER)", value=f"`{percepcao_val}`", inline=True)
            embed.add_field(name="📚 Inteligência (INT)", value=f"`{inteligencia_val}`", inline=True)
            embed.add_field(name="🌀 Raciocínio (RAC)", value=f"`{raciocinio_val}`", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            error_msg = "❌ Digite apenas números entre 1 e 5!" if "invalid literal" in str(e) else f"❌ {str(e)}"
            await interaction.response.send_message(
                error_msg,
                ephemeral=True,
                delete_after=10
            )
