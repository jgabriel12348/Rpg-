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
from models.npc_modals.atributos_modais.ordem.fisicos import NPCOrdemFisicosModal
from models.npc_modals.atributos_modais.ordem.mentais import NPCOrdemMentaisModal
from models.npc_modals.atributos_modais.ordem.recursos import NPCOrdemRecursosModal

class NPCOrdemAtributosView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context

    @discord.ui.button(label="👁️ Físicos/Paranormais", style=discord.ButtonStyle.primary)
    async def fisicos(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(NPCOrdemFisicosModal(self.npc_context))

    @discord.ui.button(label="📜 Mentais", style=discord.ButtonStyle.secondary)
    async def mentais(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(NPCOrdemMentaisModal(self.npc_context))

    @discord.ui.button(label="🔮 Recursos", style=discord.ButtonStyle.success, row=0)
    async def recursos(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(NPCOrdemRecursosModal(self.npc_context))

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger)
    async def back_to_selector(self, interaction: discord.Interaction, button: discord.ui.Button):
      from view.ficha_npc.npc_attributes import NPCAtributosMenuView
      view = NPCAtributosMenuView(npc_context=self.npc_context)
      await interaction.response.edit_message(
        content=f"💪 Escolha um sistema para editar os atributos de **{self.npc_context.npc_name}**:",
        view=view
      )