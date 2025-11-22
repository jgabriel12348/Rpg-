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

class VampiroAtributosSociaisModal(discord.ui.Modal, title="🎭 Atributos Sociais (Vampiro)"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"

        # Inputs
        self.carisma = discord.ui.TextInput(
            label="Carisma (CAR)",
            placeholder="Valor",
            required=True,
            max_length=1
        )
        self.manipulacao = discord.ui.TextInput(
            label="Manipulação (MAN)",
            placeholder="Valor",
            required=True,
            max_length=1
        )
        self.aparencia = discord.ui.TextInput(
            label="Aparência (APA)",
            placeholder="Valor",
            required=True,
            max_length=1
        )
        self.add_item(self.carisma)
        self.add_item(self.manipulacao)
        self.add_item(self.aparencia)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            carisma_val = int(self.carisma.value)
            manipulacao_val = int(self.manipulacao.value)
            aparencia_val = int(self.aparencia.value)

            if not all(1 <= val <= 5000 for val in [carisma_val, manipulacao_val, aparencia_val]):
                raise ValueError("Todos os atributos devem estar entre 1 e 5")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "carisma": carisma_val,
                "manipulacao": manipulacao_val,
                "aparencia": aparencia_val
            })
            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="🎭 Atributos Sociais Atualizados",
                description="**Vampiro: A Máscara**",
                color=0x6A0DAD
            )
            embed.add_field(name="😎 Carisma (CAR)", value=f"`{carisma_val}`", inline=True)
            embed.add_field(name="🗣️ Manipulação (MAN)", value=f"`{manipulacao_val}`", inline=True)
            embed.add_field(name="✨ Aparência (APA)", value=f"`{aparencia_val}`", inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            error_msg = "❌ Digite apenas números entre 1 e 5!" if "invalid literal" in str(e) else f"❌ {str(e)}"
            await interaction.response.send_message(
                error_msg,
                ephemeral=True,
                delete_after=10
            )
