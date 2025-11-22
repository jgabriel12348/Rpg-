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


class NPCRemoveAttackView(discord.ui.View):
  def __init__(self, npc_context: NPCContext, previous_view: discord.ui.View):
    super().__init__(timeout=None)
    self.npc_context = npc_context
    self.previous_view = previous_view
    self._loc = (
      getattr(npc_context, "user_pref", None)
      or getattr(npc_context, "guild_pref", None)
      or getattr(npc_context, "locale", None)
      or "pt"
    )

    npc_data = self.npc_context.load()
    ataques = npc_data.get("ataques", [])
    magias = npc_data.get("magias", [])
    all_skills = ataques + magias

    if all_skills:
      self.add_item(self.SkillSelect(all_skills, locale=self._loc))
      self.add_item(self.ConfirmRemoveButton(locale=self._loc))

    self.add_item(self.BackButton(locale=self._loc))

  class SkillSelect(discord.ui.Select):
    def __init__(self, skills: list, locale: str = "pt"):
      self._loc = locale
      tag_attack = _tr("npc.remove_skill.tag.attack", locale, "[Ataque]")
      tag_spell  = _tr("npc.remove_skill.tag.spell",  locale, "[Magia]")

      options = [
        discord.SelectOption(
          label=f"{tag_attack} {s['nome']}" if 'dano' in s else f"{tag_spell} {s['nome']}",
          value=s['nome']
        ) for s in skills
      ]

      placeholder = _tr(
        "npc.remove_skill.select.ph",
        locale,
        "Selecione os ataques/magias para remover..."
      )

      super().__init__(
        placeholder=placeholder,
        min_values=1,
        max_values=len(skills),
        options=options,
        custom_id="npc:attacks:remove:select"
      )

    async def callback(self, interaction: discord.Interaction):
      await interaction.response.defer()

  class ConfirmRemoveButton(discord.ui.Button):
    def __init__(self, locale: str = "pt"):
      self._loc = locale
      label = _tr("npc.remove_skill.confirm", locale, "Confirmar Remoção")
      super().__init__(label=label, style=discord.ButtonStyle.danger, row=1, custom_id="npc:attacks:remove:confirm")

    async def callback(self, interaction: discord.Interaction):
      skills_to_remove = self.view.children[0].values

      npc_data = self.view.npc_context.load()

      npc_data["ataques"] = [
        ataque for ataque in npc_data.get("ataques", [])
        if ataque["nome"] not in skills_to_remove
      ]
      npc_data["magias"] = [
        magia for magia in npc_data.get("magias", [])
        if magia["nome"] not in skills_to_remove
      ]

      self.view.npc_context.save(npc_data)

      loc = resolve_locale(
        interaction,
        user_pref=getattr(self.view.npc_context, "user_pref", None),
        guild_pref=getattr(self.view.npc_context, "guild_pref", None),
        fallback=self._loc,
      )

      done = _tr(
        "npc.remove_skill.done",
        loc,
        "✅ **{count}** habilidade(s) removida(s) da ficha de **{name}**!",
        count=len(skills_to_remove),
        name=self.view.npc_context.npc_name
      )

      await interaction.response.edit_message(
        content=done,
        view=None
      )

  class BackButton(discord.ui.Button):
    def __init__(self, locale: str = "pt"):
      self._loc = locale
      label = _tr("common.back", locale, "🔙 Voltar")
      super().__init__(label=label, style=discord.ButtonStyle.secondary, row=1, custom_id="npc:attacks:remove:back")

    async def callback(self, interaction: discord.Interaction):
      loc = resolve_locale(
        interaction,
        user_pref=getattr(self.view.npc_context, "user_pref", None),
        guild_pref=getattr(self.view.npc_context, "guild_pref", None),
        fallback=self._loc,
      )
      header = _tr(
        "npc.remove_skill.editing_header",
        loc,
        "⚔️ Editando ataques e habilidades de **{name}**",
        name=self.view.npc_context.npc_name
      )
      await interaction.response.edit_message(
        content=header,
        view=self.view.previous_view
      )
