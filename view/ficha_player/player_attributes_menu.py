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
from view.ficha_player.atributos.ded import PlayerDeAtributosView
from view.ficha_player.atributos.cthulhu import PlayerthulhuAtributosView
from view.ficha_player.atributos.vampiro import PlayerVampiroAtributosView
from view.ficha_player.atributos.ordem import OrdemMenu
from view.ficha_player.atributos.cyberpunk import CyberpunkMenu
from view.ficha_player.atributos.skifall import PlayerSkifallAtributosView
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


class PlayerAtributosMenuView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user
    self._loc = "pt"

    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "player:attrs:dnd":
          item.label = _tr("player.attrs.menu.btn.dnd", self._loc, "⚔️ D&D")
        elif item.custom_id == "player:attrs:ordem":
          item.label = _tr("player.attrs.menu.btn.ordem", self._loc, "💀 Ordem Paranormal")
        elif item.custom_id == "player:attrs:coc":
          item.label = _tr("player.attrs.menu.btn.coc", self._loc, "🐙 Call of Cthulhu")
        elif item.custom_id == "player:attrs:vampire":
          item.label = _tr("player.attrs.menu.btn.vampire", self._loc, "🧛 Vampiro: A Máscara")
        elif item.custom_id == "player:attrs:cyberpunk":
          item.label = _tr("player.attrs.menu.btn.cyberpunk", self._loc, "🤖 Cyberpunk")
        elif item.custom_id == "player:attrs:skifall":
          item.label = _tr("player.attrs.menu.btn.skifall", self._loc, "❄️ SkiFall RPG")
        elif item.custom_id == "player:attrs:tormenta":
          item.label = _tr("player.attrs.menu.btn.tormenta", self._loc, "🗡️ Tormenta20")
        elif item.custom_id == "player:attrs:back":
          item.label = _tr("common.back", self._loc, "🔙 Voltar")

  @discord.ui.button(label="⚔️ D&D", style=discord.ButtonStyle.primary, row=1, custom_id="player:attrs:dnd")
  async def dnd_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.attrs.menu.choose_set", loc, "💠 Escolha qual conjunto de atributos deseja editar:")
    await interaction.response.edit_message(
      content=content,
      view=PlayerDeAtributosView(user=self.user)
    )

  @discord.ui.button(label="💀 Ordem Paranormal", style=discord.ButtonStyle.secondary, row=1, custom_id="player:attrs:ordem")
  async def ordem_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.attrs.menu.choose_set", loc, "💠 Escolha qual conjunto de atributos deseja editar:")
    await interaction.response.edit_message(
      content=content,
      view=OrdemMenu(user=self.user)
    )

  @discord.ui.button(label="🐙 Call of Cthulhu", style=discord.ButtonStyle.blurple, row=1, custom_id="player:attrs:coc")
  async def coc_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.attrs.menu.choose_set", loc, "💠 Escolha qual conjunto de atributos deseja editar:")
    await interaction.response.edit_message(
      content=content,
      view=PlayerthulhuAtributosView(user=self.user)
    )

  @discord.ui.button(label="🧛 Vampiro: A Máscara", style=discord.ButtonStyle.danger, row=1, custom_id="player:attrs:vampire")
  async def vampire_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.attrs.menu.choose_set", loc, "💠 Escolha qual conjunto de atributos deseja editar:")
    await interaction.response.edit_message(
      content=content,
      view=PlayerVampiroAtributosView(user=self.user)
    )

  @discord.ui.button(label="🤖 Cyberpunk", style=discord.ButtonStyle.primary, row=2, custom_id="player:attrs:cyberpunk")
  async def cyberpunk_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.attrs.menu.choose_set", loc, "💠 Escolha qual conjunto de atributos deseja editar:")
    await interaction.response.edit_message(
      content=content,
      view=CyberpunkMenu(user=self.user)
    )

  @discord.ui.button(label="❄️ SkiFall RPG", style=discord.ButtonStyle.secondary, row=2, custom_id="player:attrs:skifall")
  async def skifall_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.attrs.menu.choose_set", loc, "💠 Escolha qual conjunto de atributos deseja editar:")
    await interaction.response.edit_message(
      content=content,
      view=PlayerSkifallAtributosView(user=self.user)
    )

  @discord.ui.button(label="🗡️ Tormenta20", style=discord.ButtonStyle.danger, row=2, custom_id="player:attrs:tormenta")
  async def tormenta_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.attrs.menu.choose_set", loc, "💠 Escolha qual conjunto de atributos deseja editar:")
    await interaction.response.edit_message(
      content=content,
      view=PlayerDeAtributosView(user=self.user)
    )

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, row=2, custom_id="player:attrs:back")
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.ficha_player_menu import PlayerMainMenuView
    loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.menu.main.title", loc, "🎮 Menu Principal do Player")
    await interaction.response.edit_message(content=content, view=PlayerMainMenuView(user=self.user))
