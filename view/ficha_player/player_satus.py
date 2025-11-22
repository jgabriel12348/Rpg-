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
from models.player_modals.satus_modais.carga_modal import CargaModal
from models.player_modals.satus_modais.alinhamento import AlignmentModal
from models.player_modals.satus_modais.alianca import AllianceModal
from models.player_modals.satus_modais.objetivos import ObjectivesModal
from models.player_modals.satus_modais.personalidade import PersonalityModal
from models.player_modals.satus_modais.extras import ExtrasModal
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
  """
  Wrapper para i18n.t com fallback seguro.
  Se a chave não existir (t retorna a própria key), usamos o fallback informado.
  """
  try:
    text = t_raw(key, locale, **kwargs)
  except Exception:
    return fallback.format(**kwargs) if kwargs else fallback
  if text == key:
    try:
      return fallback.format(**kwargs) if kwargs else fallback
    except Exception:
      return fallback
  return text


class PlayerStatusMenuView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user
    self._loc = "pt"

    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "player:status:load":
          item.label = _tr("player.status.btn.load", self._loc, "💪 Carga Máxima")
        elif item.custom_id == "player:status:alignment":
          item.label = _tr("player.status.btn.alignment", self._loc, "🧠 Alinhamento")
        elif item.custom_id == "player:status:alliances":
          item.label = _tr("player.status.btn.alliances", self._loc, "🔰 Alianças")
        elif item.custom_id == "player:status:objectives":
          item.label = _tr("player.status.btn.objectives", self._loc, "📌 Objetivos")
        elif item.custom_id == "player:status:personality":
          item.label = _tr("player.status.btn.personality", self._loc, "🎭 Personalidade")
        elif item.custom_id == "player:status:extras":
          item.label = _tr("player.status.btn.extras", self._loc, "➕ Extras")
        elif item.custom_id == "player:status:back":
          item.label = _tr("common.back", self._loc, "🔙 Voltar")

  @discord.ui.button(label="💪 Carga Máxima", style=discord.ButtonStyle.primary, custom_id="player:status:load")
  async def add_carga(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(CargaModal(interaction=interaction))

  @discord.ui.button(label="🧠 Alinhamento", style=discord.ButtonStyle.secondary, custom_id="player:status:alignment")
  async def add_alignment(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(AlignmentModal(interaction=interaction))

  @discord.ui.button(label="🔰 Alianças", style=discord.ButtonStyle.success, custom_id="player:status:alliances")
  async def add_alliance(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(AllianceModal(interaction=interaction))

  @discord.ui.button(label="📌 Objetivos", style=discord.ButtonStyle.primary, custom_id="player:status:objectives")
  async def add_objectives(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(ObjectivesModal(interaction=interaction))

  @discord.ui.button(label="🎭 Personalidade", style=discord.ButtonStyle.secondary, custom_id="player:status:personality")
  async def add_personality(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(PersonalityModal(interaction=interaction))

  @discord.ui.button(label="➕ Extras", style=discord.ButtonStyle.success, custom_id="player:status:extras")
  async def add_extras(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(ExtrasModal(interaction=interaction))

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, custom_id="player:status:back")
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.ficha_player_menu import PlayerMainMenuView
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.menu.main.title", loc, "🎮 Menu Principal do Player")
    await interaction.response.edit_message(content=content, view=PlayerMainMenuView(user=self.user))
