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
from utils import player_utils, rpg_rules

class SystemSelect(discord.ui.Select):
  def __init__(self, user: discord.User):
    self.user = user
    self.character_name = f"{user.id}_{user.name.lower()}"
    ficha = player_utils.load_player_sheet(self.character_name)
    current_system = ficha.get("informacoes_basicas", {}).get("sistema_rpg", "dnd")
    options = []
    for key, name in rpg_rules.SUPPORTED_SYSTEMS.items():
      option = discord.SelectOption(label=name, value=key)
      if key == current_system:
        option.default = True
      options.append(option)
    super().__init__(placeholder="Selecione o sistema de RPG da sua ficha...", options=options)
  async def callback(self, interaction: discord.Interaction):
    from view.ficha_player.ficha_player_menu import PlayerMainMenuView
    await interaction.response.defer()
    selected_system = self.values[0]
    ficha = player_utils.load_player_sheet(self.character_name)
    ficha.setdefault("informacoes_basicas", {})["sistema_rpg"] = selected_system
    player_utils.save_player_sheet(self.character_name, ficha)
    view = PlayerMainMenuView(user=self.user)
    await interaction.edit_original_response(
      content=f"✅ Sistema da ficha alterado para **{rpg_rules.SUPPORTED_SYSTEMS[selected_system]}**!\n\n"
              f"🎮 Menu Principal do Player",
      view=view
    )

class SystemSelectView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user
    self.add_item(SystemSelect(user=user))
  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, row=1)
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.ficha_player_menu import PlayerMainMenuView
    view = PlayerMainMenuView(user=self.user)
    await interaction.response.edit_message(content="🎮 Menu Principal do Player", view=view)