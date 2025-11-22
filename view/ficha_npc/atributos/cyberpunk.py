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
from utils.npc_utils import NPCContext
from models.npc_modals.atributos_modais.cyberpunk.cyberware import NPCCyberpunkCyberwareModal
from models.npc_modals.atributos_modais.cyberpunk.fisicos import NPCCyberpunkFisicosModal
from models.npc_modals.atributos_modais.cyberpunk.mentais import NPCCyberpunkMentaisModal
from models.npc_modals.atributos_modais.cyberpunk.sociais import NPCCyberpunkSociaisModal

class NPCCyberpunkMenu(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=None)
    self.npc_context = npc_context

  @discord.ui.button(label="⚙️ Físicos", style=discord.ButtonStyle.primary, custom_id="npc_cyber_fisicos")
  async def fisicos(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(NPCCyberpunkFisicosModal(self.npc_context))

  @discord.ui.button(label="💿 Mentais", style=discord.ButtonStyle.secondary, custom_id="npc_cyber_mentais")
  async def mentais(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(NPCCyberpunkMentaisModal(self.npc_context))

  @discord.ui.button(label="🌐 Sociais", style=discord.ButtonStyle.primary, custom_id="npc_cyber_sociais")
  async def sociais(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(NPCCyberpunkSociaisModal(self.npc_context))

  @discord.ui.button(label="🔋 Cyberware", style=discord.ButtonStyle.danger, custom_id="npc_cyber_ware")
  async def cyberware(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(NPCCyberpunkCyberwareModal(self.npc_context))

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger)
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_npc.npc_attributes import NPCAtributosMenuView
    view = NPCAtributosMenuView(npc_context=self.npc_context)
    await interaction.response.edit_message(
        content=f"💪 Escolha um sistema para editar os atributos de **{self.npc_context.npc_name}**:",
        view=view
    )