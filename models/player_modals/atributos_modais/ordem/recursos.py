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

class OrdemParanormalModal(discord.ui.Modal, title="🔮 Recursos Paranormais"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        self.sanidade = discord.ui.TextInput(
            label="Sanidade Atual",
            placeholder="Ex: 50",
            required=True,
            max_length=3
        )

        self.pe = discord.ui.TextInput(
            label="Pontos de Esforço (PE)",
            placeholder="Ex: 10",
            required=True,
            max_length=2
        )

        self.nex = discord.ui.TextInput(
            label="NEX (%)",
            placeholder="5-99%",
            required=True,
            max_length=2
        )
        self.add_item(self.sanidade)
        self.add_item(self.pe)
        self.add_item(self.nex)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        try:
            sanidade_val = int(self.sanidade.value)
            pe_val = int(self.pe.value)
            nex_val = int(self.nex.value)
            if not (0 <= sanidade_val <= 999):
                raise ValueError("Sanidade deve ser entre 0 e 99")

            if not (1 <= pe_val <= 2000):
                raise ValueError("PE deve ser um numero válido")

            if not (5 <= nex_val <= 999):
                raise ValueError("NEX deve ser entre 5% e 99%")
            max_sanidade = (ficha["atributos"].get("intelecto", 0) + ficha["atributos"].get("vontade", 0)) * 5
            max_pe = (ficha["atributos"].get("vigor", 0) + ficha["atributos"].get("presenca", 0))
            ficha["recursos"] = ficha.get("recursos", {})
            ficha["recursos"].update({
                "sanidade": sanidade_val,
                "pe": pe_val,
                "nex": nex_val
            })

            save_player_sheet(self.character_name, ficha)
            embed = discord.Embed(
                title="🔮 Recursos Paranormais Atualizados",
                description="**Ordem Paranormal RPG**",
                color=0x8A2BE2
            )
            embed.add_field(
                name="🧠 Sanidade",
                value=f"`{sanidade_val}/{max_sanidade}`",
                inline=True
            )
            embed.add_field(
                name="⚡ Pontos de Esforço",
                value=f"`{pe_val}/{max_pe}`",
                inline=True
            )
            embed.add_field(
                name="👁️ NEX",
                value=f"`{nex_val}%`",
                inline=True
            )
            progress = int(nex_val / 10)
            embed.add_field(
                name="📈 Progresso Paranormal",
                value=f"`[{'■' * progress}{'□' * (10 - progress)}] {nex_val}%`",
                inline=False
            )

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
                delete_after=15
            )
