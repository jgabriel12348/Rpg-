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
from models.player_modals.itens.dashboard import ItemDashboardView
from models.player_modals.itens.combat import AddItemCombatModal
from models.player_modals.itens.defesa import AddItemDefenseModal
from models.player_modals.itens.consumivel import AddItemConsumableModal
from models.player_modals.itens.carteira import WalletModal
from models.player_modals.itens.aleatorio import AddItemRandomModal
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


class PlayerInventarioMenuView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user
    self._loc = "pt"

    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "player:inv:combat":
          item.label = _tr("player.inventory.btn.combat", self._loc, "⚔️ Combate")
        elif item.custom_id == "player:inv:defense":
          item.label = _tr("player.inventory.btn.defense", self._loc, "🛡️ Defesa")
        elif item.custom_id == "player:inv:consumable":
          item.label = _tr("player.inventory.btn.consumable", self._loc, "🍷 Consumível")
        elif item.custom_id == "player:inv:random":
          item.label = _tr("player.inventory.btn.random", self._loc, "🎒 Aleatório")
        elif item.custom_id == "player:inv:wallet":
          item.label = _tr("player.inventory.btn.wallet", self._loc, "💰 Carteira")
        elif item.custom_id == "player:inv:back":
          item.label = _tr("common.back", self._loc, "🔙 Voltar")

  def create_item_list_embed(self, category: str, category_name: str, icon: str) -> discord.Embed:
    character_name = f"{self.user.id}_{self.user.name.lower()}"
    ficha = player_utils.load_player_sheet(character_name)
    items = ficha.get("inventario", {}).get(category, [])
    title = _tr("player.inventory.embed.title", self._loc, "{icon} Itens de {name}", icon=icon, name=category_name)
    embed = discord.Embed(title=title, color=discord.Color.blue())

    if not items:
      embed.description = _tr("player.inventory.none_in_category", self._loc, "Nenhum item desta categoria no inventário.")
    else:
      description = ""
      for item in items:
        description += f"**{item['nome']}** (x{item['quantidade']})\n"
      embed.description = description
    return embed

  @discord.ui.button(label="⚔️ Combate", style=discord.ButtonStyle.danger, custom_id="player:inv:combat")
  async def combat_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_item_list_embed('combate', _tr("player.inventory.category.combat", self._loc, 'Combate'), '⚔️')
    view = ItemDashboardView(self.user, 'combate', _tr("player.inventory.category.combat", self._loc, 'Combate'), AddItemCombatModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="🛡️ Defesa", style=discord.ButtonStyle.blurple, custom_id="player:inv:defense")
  async def defense_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_item_list_embed('defesa', _tr("player.inventory.category.defense", self._loc, 'Defesa'), '🛡️')
    view = ItemDashboardView(self.user, 'defesa', _tr("player.inventory.category.defense", self._loc, 'Defesa'), AddItemDefenseModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="🍷 Consumível", style=discord.ButtonStyle.secondary, custom_id="player:inv:consumable")
  async def consumable_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_item_list_embed('consumivel', _tr("player.inventory.category.consumable", self._loc, 'Consumíveis'), '🍷')
    view = ItemDashboardView(self.user, 'consumivel', _tr("player.inventory.category.consumable", self._loc, 'Consumíveis'), AddItemConsumableModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="🎒 Aleatório", style=discord.ButtonStyle.gray, custom_id="player:inv:random")
  async def random_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_item_list_embed('aleatorio', _tr("player.inventory.category.random", self._loc, 'Itens Aleatórios'), '🎒')
    view = ItemDashboardView(self.user, 'aleatorio', _tr("player.inventory.category.random", self._loc, 'Itens Aleatórios'), AddItemRandomModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="💰 Carteira", style=discord.ButtonStyle.success, custom_id="player:inv:wallet")
  async def wallet_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(WalletModal(interaction=interaction))

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, custom_id="player:inv:back")
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.ficha_player_menu import PlayerMainMenuView
    self._loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.menu.main.title", self._loc, "🎮 Menu Principal do Player")
    await interaction.response.edit_message(content=content, view=PlayerMainMenuView(user=self.user))
