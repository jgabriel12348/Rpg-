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

class SkiFallRecursosModal(discord.ui.Modal, title="✨ Recursos Especiais"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"

        self.enfase = discord.ui.TextInput(
            label="Pontos de Ênfase",
            placeholder="Ex: 3",
            max_length=2,
            required=True
        )
        self.dano_sangue = discord.ui.TextInput(
            label="Dano de Sangue Total",
            placeholder="Ex: 2",
            max_length=1,
            required=True
        )
        self.corrupcao = discord.ui.TextInput(
            label="Corrupção Total",
            placeholder="Ex: 0",
            max_length=1,
            required=True
        )

        self.add_item(self.enfase)
        self.add_item(self.dano_sangue)
        self.add_item(self.corrupcao)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            enfase_total = int(self.enfase.value)
            ds_total = int(self.dano_sangue.value)
            cor_total = int(self.corrupcao.value)

            if not (0 <= enfase_total <= 1000):
                raise ValueError("Ênfase deve ser um número")
            if not (0 <= ds_total <= 5000):
                raise ValueError("Dano de Sangue deve ser um número")
            if not (0 <= cor_total <= 5000):
                raise ValueError("Corrupção deve ser um número")

            ficha["recursos"] = ficha.get("recursos", {})
            ficha["recursos"].update({
                "enfase_total": enfase_total,
                "dano_sangue_total": ds_total,
                "corrupcao_total": cor_total
            })

            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="✨ Recursos Especiais Atualizados",
                color=0x9932CC
            )
            embed.add_field(name="🎯 Ênfase Total", value=f"`{enfase_total}`", inline=True)
            embed.add_field(name="🩸 Dano de Sangue", value=f"`{ds_total}/5`", inline=True)
            embed.add_field(name="☠️ Corrupção", value=f"`{cor_total}/5`", inline=True)

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
