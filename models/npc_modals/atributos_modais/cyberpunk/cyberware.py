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
from models.npc_modals.npc_basic_modal import NPCModalBase

class NPCCyberpunkCyberwareModal(NPCModalBase):
  def __init__(self, npc_context):
    super().__init__(npc_context, title=f"🔋 Cyberware de {npc_context.npc_name}")
    cyberware_data = self.npc_data.get("cyberware", {})
    implantes_str = ", ".join(cyberware_data.get("implantes", []))
    melhorias_str = ", ".join(cyberware_data.get("melhorias", []))

    self.humanidade = discord.ui.TextInput(
      label="Humanidade Atual",
      placeholder="Ex: 70",
      default=str(cyberware_data.get("humanidade", "")),
      required=True,
      max_length=3
    )
    self.implantes = discord.ui.TextInput(
      label="Implantes Instalados (separados por vírgula)",
      placeholder="Ex: Ótico Cyberware 3, Garras Retráteis...",
      style=discord.TextStyle.paragraph,
      default=implantes_str,
      required=False
    )
    self.melhorias = discord.ui.TextInput(
      label="Sistemas de Interface",
      placeholder="Ex: Sandevistan, Interface Neural 2...",
      style=discord.TextStyle.paragraph,
      default=melhorias_str,
      required=False
    )

    self.add_item(self.humanidade)
    self.add_item(self.implantes)
    self.add_item(self.melhorias)

  async def on_submit(self, interaction: discord.Interaction):
    try:
      atributos = self.npc_data.get("atributos", {})
      emp_value = atributos.get("Empatia", atributos.get("empatia", "1"))
      empathy = int(emp_value)
      max_humanidade = empathy * 10

      humanidade_val = int(self.humanidade.value)
      if not 0 <= humanidade_val <= max_humanidade:
        raise ValueError(f"A Humanidade do NPC deve ser entre 0 e {max_humanidade} (Empatia {empathy} x 10)")

      cyberware_data = {
        "humanidade": humanidade_val,
        "perda_humanidade": max_humanidade - humanidade_val,
        "implantes": [imp.strip() for imp in self.implantes.value.split(',') if imp.strip()],
        "melhorias": [mel.strip() for mel in self.melhorias.value.split(',') if mel.strip()]
      }
      self.npc_data["cyberware"] = cyberware_data
      self.save()

      embed = discord.Embed(
        title=f"🔋 Sistema Cyberware de {self.npc_context.npc_name}",
        color=0x71ddbf
      )
      progress = int((humanidade_val / max_humanidade) * 10) if max_humanidade > 0 else 0
      embed.add_field(
        name="Nível de Conexão Humana",
        value=f"`[{'█' * progress}{'░' * (10 - progress)}] {humanidade_val}/{max_humanidade}`",
        inline=False
      )
      implantes_str = "\n".join(f"• {imp}" for imp in cyberware_data["implantes"]) or "Nenhum"
      embed.add_field(name="⚙️ Implantes", value=implantes_str, inline=True)
      melhorias_str = "\n".join(f"• {mel}" for mel in cyberware_data["melhorias"]) or "Nenhum"
      embed.add_field(name="💿 Sistemas", value=melhorias_str, inline=True)
      embed.set_footer(text=f"NPC atualizado por {interaction.user.display_name}")

      await interaction.response.send_message(embed=embed, ephemeral=True)

    except (ValueError, TypeError) as e:
      await interaction.response.send_message(
        f"❌ Erro: {e}. Verifique se a Humanidade é um número válido e se o atributo 'Empatia' está definido na ficha do NPC.",
        ephemeral=True)