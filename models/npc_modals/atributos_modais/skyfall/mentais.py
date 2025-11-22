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

class NPCSkifallMentaisModal(NPCModalBase):
  def __init__(self, npc_context):
    super().__init__(npc_context, title=f"🧠 Atributos Mentais de {npc_context.npc_name}")
    atributos = self.npc_data.get("atributos", {})
    self.intelecto = self.create_input("Intelecto Total", atributos.get("intelecto_total"))
    self.percepcao = self.create_input("Percepção Total", atributos.get("percepcao_total"))
    self.vontade = self.create_input("Vontade Total", atributos.get("vontade_total"))
    self.add_item(self.intelecto)
    self.add_item(self.percepcao)
    self.add_item(self.vontade)

  def create_input(self, label, default_value):
    return discord.ui.TextInput(
      label=label,
      placeholder="Ex: 14",
      default=str(default_value or ""),
      required=False,
    )

  async def on_submit(self, interaction: discord.Interaction):
    try:
      valores = {
        "intelecto_total": self.intelecto.value,
        "percepcao_total": self.percepcao.value,
        "vontade_total": self.vontade.value
      }
      valores_int = {}
      for nome, valor in valores.items():
        if valor:
          v_int = int(valor)
          if not 1 <= v_int <= 2000:
            raise ValueError(f"O valor de {nome.replace('_', ' ').capitalize()} deve estar entre 1 e 20")
          valores_int[nome] = v_int
      self.npc_data.setdefault("atributos", {}).update(valores_int)
      self.save()
      embed = discord.Embed(
        title=f"🧠 Atributos Mentais de {self.npc_context.npc_name}",
        description="**SkiFall RPG**",
        color=0x1E90FF
      )
      for nome, valor in valores_int.items():
        embed.add_field(name=f"🧠 {nome.replace('_', ' ').capitalize()}", value=f"`{valor}`", inline=True)
      embed.set_footer(text=f"NPC atualizado por {interaction.user.display_name}")
      await interaction.response.send_message(embed=embed, ephemeral=True)
    except ValueError as e:
      await interaction.response.send_message(f"❌ Erro: {e}. Certifique-se de usar apenas números entre 1 e 20.",
                                              ephemeral=True)