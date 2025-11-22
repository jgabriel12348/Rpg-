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
from models.player_modals.atributos_modais.cyberpunk.fisicos import CyberpunkFisicosModal
from models.player_modals.atributos_modais.cyberpunk.mentais import CyberpunkMentaisModal
from models.player_modals.atributos_modais.cyberpunk.sociais import CyberpunkSociaisModal
from models.player_modals.atributos_modais.cyberpunk.cyberware import CyberpunkCyberwareModal

class CyberpunkMenu(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user

  @discord.ui.button(label="⚙️ Físicos", style=discord.ButtonStyle.primary, custom_id="cyber_fisicos")
  async def fisicos(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(CyberpunkFisicosModal(interaction))

  @discord.ui.button(label="💿 Mentais", style=discord.ButtonStyle.secondary, custom_id="cyber_mentais")
  async def mentais(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(CyberpunkMentaisModal(interaction))

  @discord.ui.button(label="🌐 Sociais", style=discord.ButtonStyle.primary, custom_id="cyber_sociais")
  async def sociais(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(CyberpunkSociaisModal(interaction))

  @discord.ui.button(label="🔋 Cyberware", style=discord.ButtonStyle.danger, custom_id="cyber_ware")
  async def cyberware(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(CyberpunkCyberwareModal(interaction))

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger)
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.player_attributes_menu import PlayerAtributosMenuView
    await interaction.response.edit_message(content="🎮 Menu Principal do Player", view=PlayerAtributosMenuView(user=self.user))