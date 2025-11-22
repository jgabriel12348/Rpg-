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

class NPCOrdemRecursosModal(NPCModalBase):
  def __init__(self, npc_context):
    super().__init__(npc_context, title=f"🔮 Recursos de {npc_context.npc_name}")

    recursos = self.npc_data.get("recursos", {})

    self.sanidade = self.create_input("Sanidade Atual", "Ex: 50", recursos.get("sanidade"))
    self.pe = self.create_input("Pontos de Esforço (PE)", "Ex: 10", recursos.get("pe"))
    self.nex = self.create_input("NEX (%)", "5-99%", recursos.get("nex"))

    self.add_item(self.sanidade)
    self.add_item(self.pe)
    self.add_item(self.nex)

  def create_input(self, label, placeholder, default_value):
    return discord.ui.TextInput(
      label=label, placeholder=placeholder,
      default=str(default_value or ""), required=False, max_length=3
    )

  async def on_submit(self, interaction: discord.Interaction):
    try:
      atributos = self.npc_data.get("atributos", {})
      intelecto = int(atributos.get("Intelecto", atributos.get("intelecto", 0)))
      vontade = int(atributos.get("Vontade", atributos.get("vontade", 0)))
      vigor = int(atributos.get("Vigor", atributos.get("vigor", 0)))
      presenca = int(atributos.get("Presença", atributos.get("presenca", 0)))

      sanidade_val = int(self.sanidade.value or 0)
      pe_val = int(self.pe.value or 0)
      nex_val = int(self.nex.value or 0)

      if not (0 <= sanidade_val <= 2000):
        raise ValueError("Sanidade deve ser um número válido.")
      if not (0 <= pe_val <= 999):
        raise ValueError("PE deve ser um número válido.")
      if not (5 <= nex_val <= 999):
        raise ValueError("NEX deve ser entre 5% e 99%")

      max_sanidade = (intelecto + vontade) * 5 if (intelecto + vontade) > 0 else sanidade_val
      max_pe = (vigor + presenca) if (vigor + presenca) > 0 else pe_val

      self.npc_data.setdefault("recursos", {}).update({
        "sanidade": sanidade_val, "pe": pe_val, "nex": nex_val
      })
      self.save()

      embed = discord.Embed(
        title=f"🔮 Recursos Paranormais de {self.npc_context.npc_name}",
        description="**Ordem Paranormal RPG**",
        color=0x8A2BE2
      )
      embed.add_field(name="🧠 Sanidade", value=f"`{sanidade_val}/{max_sanidade}`", inline=True)
      embed.add_field(name="⚡ Pontos de Esforço", value=f"`{pe_val}/{max_pe}`", inline=True)
      embed.add_field(name="👁️ NEX", value=f"`{nex_val}%`", inline=True)

      progress = int(nex_val / 10) if nex_val >= 10 else 0
      embed.add_field(
        name="📈 Progresso Paranormal",
        value=f"`[{'■' * progress}{'□' * (10 - progress)}] {nex_val}%`",
        inline=False
      )
      embed.set_footer(text=f"NPC atualizado por {interaction.user.display_name}")
      await interaction.response.send_message(embed=embed, ephemeral=True)

    except (ValueError, TypeError) as e:
      await interaction.response.send_message(
        f"❌ Erro: {e}. Verifique se os atributos base (Intelecto, Vigor, etc.) estão definidos.", ephemeral=True)