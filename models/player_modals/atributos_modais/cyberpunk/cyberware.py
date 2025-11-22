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

class CyberpunkCyberwareModal(discord.ui.Modal, title="🔋 Sistema Cyberware"):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"

        self.humanidade = discord.ui.TextInput(
            label="Humanidade Atual",
            placeholder="0-EMP×10 (definido pelos atributos)",
            required=True,
            max_length=3
        )

        self.implantes = discord.ui.TextInput(
            label="Implantes Instalados (separados por vírgulas)",
            placeholder="Ex: Ótico Cyberware 3, Garras Retráteis...",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )

        self.melhorias = discord.ui.TextInput(
            label="Sistemas de Interface",
            placeholder="Ex: Sandevistan, Interface Neural 2...",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=500
        )

        self.add_item(self.humanidade)
        self.add_item(self.implantes)
        self.add_item(self.melhorias)

    async def on_submit(self, interaction: discord.Interaction):
        ficha = load_player_sheet(self.character_name)

        empathy = ficha.get("atributos", {}).get("empatia", 1)
        max_humanidade = empathy * 10

        try:
            humanidade_val = int(self.humanidade.value)

            if not 0 <= humanidade_val <= max_humanidade:
                raise ValueError(f"Humanidade deve ser entre 0-{max_humanidade} (EMP×10)")

            cyberware_data = {
                "humanidade": humanidade_val,
                "perda_humanidade": max_humanidade - humanidade_val,
                "implantes": [imp.strip() for imp in self.implantes.value.split(",") if imp.strip()],
                "melhorias": [mel.strip() for mel in self.melhorias.value.split(",") if mel.strip()]
            }

            ficha["cyberware"] = cyberware_data
            save_player_sheet(self.character_name, ficha)

            embed = discord.Embed(
                title="🔋 Sistema Cyberware Atualizado",
                color=0x00FF00
            )

            embed.add_field(
                name="🧠 Humanidade",
                value=f"```{humanidade_val}/{max_humanidade} "
                      f"(Perda: {max_humanidade - humanidade_val})```",
                inline=False
            )

            implantes_str = "\n".join(f"• {imp}" for imp in cyberware_data["implantes"][:3]) or "Nenhum"
            if len(cyberware_data["implantes"]) > 3:
                implantes_str += f"\n+ {len(cyberware_data['implantes']) - 3} outros"

            embed.add_field(name="⚙️ Implantes", value=implantes_str, inline=True)

            melhorias_str = "\n".join(f"• {mel}" for mel in cyberware_data["melhorias"][:3]) or "Nenhum"
            embed.add_field(name="💿 Sistemas", value=melhorias_str, inline=True)

            progress = int((humanidade_val / max_humanidade) * 10)
            embed.add_field(
                name="Nível de Conexão Humana",
                value=f"`[{'█' * progress}{'░' * (10 - progress)}] {humanidade_val}/{max_humanidade}`",
                inline=False
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            error_msg = "⚠️ Erro: "
            if "invalid literal" in str(e):
                error_msg += "Digite apenas números para Humanidade!"
            else:
                error_msg += str(e)

            await interaction.response.send_message(
                error_msg,
                ephemeral=True,
                delete_after=15
            )
