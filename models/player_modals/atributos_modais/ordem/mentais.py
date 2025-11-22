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

class OrdemMentaisModal(discord.ui.Modal, title="📜 Atributos Mentais"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        self.intelecto = discord.ui.TextInput(
            label="Intelecto (INT)",
            placeholder="Valor",
            required=True,
            max_length=1
        )

        self.percepcao = discord.ui.TextInput(
            label="Percepção (PER)",
            placeholder="Valor",
            required=True,
            max_length=1
        )

        self.vontade = discord.ui.TextInput(
            label="Vontade (VON)",
            placeholder="Valor",
            required=True,
            max_length=1
        )
        self.add_item(self.intelecto)
        self.add_item(self.percepcao)
        self.add_item(self.vontade)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            intelecto_val = int(self.intelecto.value)
            percepcao_val = int(self.percepcao.value)
            vontade_val = int(self.vontade.value)

            if not all(1 <= val <= 5000 for val in [intelecto_val, percepcao_val, vontade_val]):
                raise ValueError("Níveis devem estar entre 1 e 5")

            ficha["atributos"] = ficha.get("atributos", {})
            ficha["atributos"].update({
                "intelecto": intelecto_val,
                "percepcao": percepcao_val,
                "vontade": vontade_val
            })

            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="📜 Atributos Mentais Atualizados",
                description="**Ordem Paranormal RPG**",
                color=0x1E90FF
            )

            embed.add_field(name="🧠 Intelecto (INT)", value=f"`{intelecto_val}`", inline=True)
            embed.add_field(name="👀 Percepção (PER)", value=f"`{percepcao_val}`", inline=True)
            embed.add_field(name="🔥 Vontade (VON)", value=f"`{vontade_val}`", inline=True)

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
