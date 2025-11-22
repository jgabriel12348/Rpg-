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
from models.player_modals.atributos_modais.ordem.fisicos import OrdemFisicosModal
from models.player_modals.atributos_modais.ordem.mentais import OrdemMentaisModal
from models.player_modals.atributos_modais.ordem.recursos import OrdemParanormalModal

class OrdemMenu(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user

  @discord.ui.button(label="👁️ Físicos/Paranormais", style=discord.ButtonStyle.primary, custom_id="ordem_fisicos")
  async def fisicos(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(OrdemFisicosModal(interaction))

  @discord.ui.button(label="📜 Mentais", style=discord.ButtonStyle.secondary, custom_id="ordem_mentais")
  async def mentais(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(OrdemMentaisModal(interaction))

  @discord.ui.button(label="🔮 Recursos", style=discord.ButtonStyle.danger, custom_id="ordem_recursos")
  async def recursos(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(OrdemParanormalModal(interaction))

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger)
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.player_attributes_menu import PlayerAtributosMenuView
    await interaction.response.edit_message(content="🎮 Menu Principal do Player", view=PlayerAtributosMenuView(user=self.user))