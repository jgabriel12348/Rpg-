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
from models.player_modals.atributos_modais.ded_atributos.atributos_fisicos import PlayerAtributosFisicosModal
from models.player_modals.atributos_modais.ded_atributos.atributos_mentais import PlayerAtributosMentaisModal
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
  """
  Wrapper para usar i18n.t com fallback seguro.
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


class PlayerDeAtributosView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user
    self._loc = "pt"

    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "player:attrs:physical":
          item.label = _tr("player.attr.menu.physical", self._loc, "💪 Atributos Físicos")
        elif item.custom_id == "player:attrs:mental":
          item.label = _tr("player.attr.menu.mental", self._loc, "🧠 Atributos Mentais/Sociais")
        elif item.custom_id == "player:attrs:back":
          item.label = _tr("common.back", self._loc, "🔙 Voltar")

  @discord.ui.button(label="💪 Atributos Físicos", style=discord.ButtonStyle.primary, custom_id="player:attrs:physical")
  async def fisicos(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(PlayerAtributosFisicosModal(interaction))

  @discord.ui.button(label="🧠 Atributos Mentais/Sociais", style=discord.ButtonStyle.secondary, custom_id="player:attrs:mental")
  async def mentais(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(PlayerAtributosMentaisModal(interaction))

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, custom_id="player:attrs:back")
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.ficha_player_menu import PlayerMainMenuView
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.menu.main.title", loc, "🎮 Menu Principal do Player")
    await interaction.response.edit_message(content=content, view=PlayerMainMenuView(user=self.user))
