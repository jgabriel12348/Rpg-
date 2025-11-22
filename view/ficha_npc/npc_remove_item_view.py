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
from utils.i18n  import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
  """
  Wrapper para usar i18n.t com fallback.
  Se a chave não existir (t retorna a própria key), usa o fallback informado.
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

def _cat_display(cat: str, loc: str) -> str:
  mapping = {
    "combate":   _tr("npc.inv.cat.combat",     loc, "Combate"),
    "defesa":    _tr("npc.inv.cat.defense",    loc, "Defesa"),
    "consumivel":_tr("npc.inv.cat.consumable", loc, "Consumíveis"),
    "aleatorio": _tr("npc.inv.cat.random",     loc, "Itens Aleatórios"),
  }
  return mapping.get(cat, str(cat).capitalize())


class NPCRemoveItemView(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=None)
    self.npc_context = npc_context
    self._loc = (
      getattr(npc_context, "user_pref", None)
      or getattr(npc_context, "guild_pref", None)
      or getattr(npc_context, "locale", None)
      or "pt"
    )

    npc_data = self.npc_context.load()
    self.all_items = []
    inventario = npc_data.get("inventario", {})
    for category, items in inventario.items():
      if isinstance(items, list):
        for item in items:
          self.all_items.append({"nome": item['nome'], "categoria": category})

    if self.all_items:
      self.add_item(self.ItemSelect(self.all_items, locale=self._loc))
      self.add_item(self.ConfirmRemoveButton(locale=self._loc))

    self.add_item(self.BackButton(locale=self._loc))

  class ItemSelect(discord.ui.Select):
    def __init__(self, items: list, locale: str = "pt"):
      self._loc = locale
      options = [
        discord.SelectOption(
          label=f"[{_cat_display(item['categoria'], locale)}] {item['nome']}",
          value=f"{item['categoria']}|{item['nome']}"
        ) for item in items
      ]
      placeholder = _tr("npc.inv.remove.items.ph", locale, "Selecione os itens para remover...")
      super().__init__(
        placeholder=placeholder,
        min_values=1,
        max_values=len(items),
        options=options,
        custom_id="npc:inv:remove:select"
      )

    async def callback(self, interaction: discord.Interaction):
      await interaction.response.defer()

  class ConfirmRemoveButton(discord.ui.Button):
    def __init__(self, locale: str = "pt"):
      self._loc = locale
      label = _tr("npc.inv.remove.confirm", locale, "Confirmar Remoção")
      super().__init__(label=label, style=discord.ButtonStyle.danger, custom_id="npc:inv:remove:confirm")

    async def callback(self, interaction: discord.Interaction):
      from view.ficha_npc.npc_itens import NPCInventoryView
      items_to_remove = self.view.children[0].values
      npc_data = self.view.npc_context.load()
      inventario = npc_data.setdefault("inventario", {})
      removed_count = 0
      for item_info in items_to_remove:
        category, name = item_info.split('|', 1)
        if category in inventario:
          original_len = len(inventario[category])
          inventario[category] = [
            item for item in inventario[category]
            if item["nome"] != name
          ]
          removed_count += original_len - len(inventario[category])

      self.view.npc_context.save(npc_data)
      view = NPCInventoryView(npc_context=self.view.npc_context)
      loc = resolve_locale(interaction) or self._loc

      success = _tr(
        "npc.inv.remove.done",
        loc,
        "✅ **{count}** item(ns) removido(s) com sucesso!\n\n🎒 Inventário de **{name}**",
        count=removed_count,
        name=self.view.npc_context.npc_name
      )

      await interaction.response.edit_message(
        content=success,
        view=view,
        embed=None
      )

  class BackButton(discord.ui.Button):
    def __init__(self, locale: str = "pt"):
      self._loc = locale
      label = _tr("common.back", locale, "🔙 Voltar")
      super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id="npc:inv:remove:back")

    async def callback(self, interaction: discord.Interaction):
      from view.ficha_npc.npc_itens import NPCInventoryView
      view = NPCInventoryView(npc_context=self.view.npc_context)

      # ⚠️ Corrigido: resolve_locale sem kwargs extras
      loc = resolve_locale(interaction) or self._loc
      header = _tr("npc.inv.header", loc, "🎒 Inventário de **{name}**", name=self.view.npc_context.npc_name)

      await interaction.response.edit_message(
        content=header,
        view=view,
        embed=None
      )
