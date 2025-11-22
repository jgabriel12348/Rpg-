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
from models.npc_modals.info_combate.npc_skill_edit_modal import NPCSkillEditModal
from utils.i18n import t as t_raw
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


class NPCSkillManagementView(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=None)
    self.npc_context = npc_context
    self._loc = (
      getattr(npc_context, "user_pref", None)
      or getattr(npc_context, "guild_pref", None)
      or getattr(npc_context, "locale", None)
      or "pt"
    )

    self.add_item(self.SkillActionSelect(npc_context=self.npc_context, locale=self._loc))
    self.add_item(self.BackButton(npc_context=self.npc_context, locale=self._loc))

  def create_embed(self) -> discord.Embed:
    npc_data = self.npc_context.load()
    pericias = npc_data.get("pericias", {})

    title = _tr("npc.skills.title", self._loc, "💡 Perícias de {name}", name=self.npc_context.npc_name)
    embed = discord.Embed(title=title, color=discord.Color.dark_green())

    if not pericias:
      embed.description = _tr(
        "npc.skills.empty",
        self._loc,
        "Este NPC ainda não possui nenhuma perícia.\nUse o menu abaixo para adicionar."
      )
    else:
      description = ""
      for nome, dados in pericias.items():
        bonus = dados.get('bonus', 0)
        sinal = "+" if bonus >= 0 else ""
        description += f"• **{nome}** (`{dados.get('atributo_base', 'N/A')}` {sinal}{bonus})\n"
      embed.description = description
    return embed

  class SkillActionSelect(discord.ui.Select):
    def __init__(self, npc_context: NPCContext, locale: str = "pt"):
      self.npc_context = npc_context
      self._loc = locale

      npc_data = self.npc_context.load()
      pericias = npc_data.get("pericias", {})

      opt_add_label   = _tr("npc.skills.select.add",    locale, "➕ Adicionar Nova Perícia")
      opt_remove_lbl  = _tr("npc.skills.select.remove", locale, "➖ Remover Perícias")
      opt_edit_prefix = _tr("npc.skills.select.edit",   locale, "✏️ Editar: {name}", name="{name}")  # será formatado abaixo
      placeholder     = _tr("npc.skills.select.ph",     locale, "Escolha uma ação de perícia...")

      options = [discord.SelectOption(label=opt_add_label, value="CREATE_NEW")]
      if pericias:
        options.append(discord.SelectOption(label=opt_remove_lbl, value="REMOVE_SKILLS", emoji="🗑️"))
        for nome in pericias.keys():
          options.append(discord.SelectOption(label=opt_edit_prefix.format(name=nome), value=str(nome)))

      super().__init__(placeholder=placeholder, options=options, custom_id="npc:skills:select")

    async def callback(self, interaction: discord.Interaction):
      loc = resolve_locale(
        interaction,
        user_pref=getattr(self.npc_context, "user_pref", None),
        guild_pref=getattr(self.npc_context, "guild_pref", None),
        fallback=self._loc,
      )
      selection = self.values[0]

      if selection == "CREATE_NEW":
        await interaction.response.send_modal(NPCSkillEditModal(self.npc_context))
      elif selection == "REMOVE_SKILLS":
        msg = _tr(
          "npc.skills.remove.todo",
          loc,
          "Funcionalidade de remover múltiplas perícias a ser implementada."
        )
        await interaction.response.send_message(msg, ephemeral=True)
      else:
        await interaction.response.send_modal(NPCSkillEditModal(self.npc_context, skill_name=selection))

  class BackButton(discord.ui.Button):
    def __init__(self, npc_context: NPCContext, locale: str = "pt"):
      self.npc_context = npc_context
      self._loc = locale
      label = _tr("common.back", locale, "🔙 Voltar")
      super().__init__(label=label, style=discord.ButtonStyle.danger, row=1, custom_id="npc:skills:back")

    async def callback(self, interaction: discord.Interaction):
      from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
      view = NPCMainMenuView(npc_context=self.npc_context)

      loc = resolve_locale(
        interaction,
        user_pref=getattr(self.npc_context, "user_pref", None),
        guild_pref=getattr(self.npc_context, "guild_pref", None),
        fallback=self._loc,
      )
      content = _tr("npc.basic.editing", loc, "📜 Editando NPC: **{name}**", name=self.npc_context.npc_name)

      await interaction.response.edit_message(content=content, view=view, embed=None)
