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

class NPCSkifallFisicosModal(NPCModalBase):
  def __init__(self, npc_context):
    super().__init__(npc_context, title=f"❄️ Atributos Físicos de {npc_context.npc_name}")
    atributos = self.npc_data.get("atributos", {})

    self.forca = self.create_input("Força Total", atributos.get("forca_total"))
    self.destreza = self.create_input("Destreza Total", atributos.get("destreza_total"))
    self.vigor = self.create_input("Vigor Total", atributos.get("vigor_total"))
    self.add_item(self.forca)
    self.add_item(self.destreza)
    self.add_item(self.vigor)

  def create_input(self, label, default_value):
    return discord.ui.TextInput(
      label=label,
      placeholder="Ex: 12",
      default=str(default_value or ""),
      required=False,
    )

  async def on_submit(self, interaction: discord.Interaction):
    try:
      valores = {
        "forca_total": self.forca.value,
        "destreza_total": self.destreza.value,
        "vigor_total": self.vigor.value
      }
      valores_int = {}
      for nome, valor in valores.items():
        if valor:
          v_int = int(valor)
          if not 1 <= v_int <= 2000:
            raise ValueError(f"O valor de {nome} deve estar entre 1 e 20")
          valores_int[nome] = v_int
      self.npc_data.setdefault("atributos", {}).update(valores_int)
      self.save()

      embed = discord.Embed(
        title=f"❄️ Atributos Físicos de {self.npc_context.npc_name}",
        description="**SkiFall RPG**",
        color=0x4682B4
      )
      for nome, valor in valores_int.items():
        embed.add_field(name=f"💪 {nome.replace('_', ' ').capitalize()}", value=f"`{valor}`", inline=True)
      embed.set_footer(text=f"NPC atualizado por {interaction.user.display_name}")
      await interaction.response.send_message(embed=embed, ephemeral=True)

    except ValueError as e:
      await interaction.response.send_message(f"❌ Erro: {e}. Certifique-se de usar apenas números entre 1 e 20.",
                                              ephemeral=True)