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
from utils import player_utils
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


class RemoveItemView(discord.ui.View):
  def __init__(self, user: discord.User, category: str, category_name: str, modal_class):
    super().__init__(timeout=180)
    self.user = user
    self.character_name = f"{user.id}_{user.name.lower()}"
    self.category = category
    self.category_name = category_name
    self.modal_class = modal_class

    self._loc = "pt"

    ficha = player_utils.load_player_sheet(self.character_name)
    items = ficha.get("inventario", {}).get(self.category, [])

    if items:
      self.add_item(self.ItemSelect(items, parent_view=self))
      self.add_item(self.ConfirmRemoveButton())
    self.add_item(self.BackButton())
    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "player:inv:remove:confirm":
          item.label = _tr("player.inventory.remove.confirm", self._loc, "Confirmar Remoção")
        elif item.custom_id == "player:inv:remove:back":
          item.label = _tr("common.back", self._loc, "🔙 Voltar")

  class ItemSelect(discord.ui.Select):
    def __init__(self, items: list, parent_view: 'RemoveItemView'):
      self.parent_view = parent_view
      placeholder = _tr(
        "player.inventory.remove.placeholder",
        parent_view._loc,
        "Selecione os itens para remover..."
      )
      options = [discord.SelectOption(label=item['nome'], value=item['nome']) for item in items]
      super().__init__(
        placeholder=placeholder,
        min_values=1,
        max_values=len(items),
        options=options
      )

    async def callback(self, interaction: discord.Interaction):
      await interaction.response.defer()

  class ConfirmRemoveButton(discord.ui.Button):
    def __init__(self):
      super().__init__(label="Confirmar Remoção", style=discord.ButtonStyle.danger, row=1,
                       custom_id="player:inv:remove:confirm")

    async def callback(self, interaction: discord.Interaction):
      from view.ficha_player.player_itens import PlayerInventarioMenuView

      loc = resolve_locale(interaction, fallback=getattr(self.view, "_loc", "pt"))

      items_to_remove = self.view.children[0].values
      ficha = player_utils.load_player_sheet(self.view.character_name)

      if self.view.category in ficha.get("inventario", {}):
        ficha["inventario"][self.view.category] = [
          item for item in ficha["inventario"][self.view.category]
          if item["nome"] not in items_to_remove
        ]

      player_utils.save_player_sheet(self.view.character_name, ficha)

      view = PlayerInventarioMenuView(user=self.view.user)
      removed_msg = _tr(
        "player.inventory.remove.done",
        loc,
        "✅ **{count}** item(ns) removido(s) com sucesso!",
        count=len(items_to_remove)
      )
      menu_title = _tr("player.inventory.menu.title", loc, "🎒 Menu de **Inventário**")

      await interaction.response.edit_message(
        content=f"{removed_msg}\n\n{menu_title}",
        view=view,
        embed=None
      )

  class BackButton(discord.ui.Button):
    def __init__(self):
      super().__init__(label="🔙 Voltar", style=discord.ButtonStyle.secondary, row=1,
                       custom_id="player:inv:remove:back")

    async def callback(self, interaction: discord.Interaction):
      from view.ficha_player.player_itens import PlayerInventarioMenuView
      loc = resolve_locale(interaction, fallback=getattr(self.view, "_loc", "pt"))
      view = PlayerInventarioMenuView(user=self.view.user)
      menu_title = _tr("player.inventory.menu.title", loc, "🎒 Menu de **Inventário**")
      await interaction.response.edit_message(
        content=menu_title,
        view=view,
        embed=None
      )
