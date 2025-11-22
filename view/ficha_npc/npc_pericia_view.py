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


class NPCLinkSkillAttributeView(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=180)
    self.npc_context = npc_context
    self.selected_skill = None
    self._loc = (
      getattr(npc_context, "user_pref", None)
      or getattr(npc_context, "guild_pref", None)
      or getattr(npc_context, "locale", None)
      or "pt"
    )

    npc_data = self.npc_context.load()
    skills = list(npc_data.get("pericias", {}).keys())
    attributes = list(npc_data.get("atributos", {}).keys())

    self.add_item(self.SkillSelect(skills, self, locale=self._loc))
    self.add_item(self.AttributeSelect(attributes, self, locale=self._loc))
    self.add_item(self.BackButton(self, locale=self._loc))

  class SkillSelect(discord.ui.Select):
    def __init__(self, skills: list, parent_view: 'NPCLinkSkillAttributeView', locale: str = "pt"):
      self.parent_view = parent_view
      self._loc = locale

      lbl_none_skill = _tr("npc.skill_attr.none_skill", locale, "Nenhuma perícia aprendida")
      options = [discord.SelectOption(label=s) for s in skills] if skills else [
        discord.SelectOption(label=lbl_none_skill)
      ]

      placeholder = _tr("npc.skill_attr.skill.ph", locale, "1. Escolha a perícia para modificar...")
      super().__init__(placeholder=placeholder, options=options, disabled=not skills, custom_id="npc:skillattr:skill")

    async def callback(self, interaction: discord.Interaction):
      loc = resolve_locale(
        interaction,
        user_pref=getattr(self.parent_view.npc_context, "user_pref", None),
        guild_pref=getattr(self.parent_view.npc_context, "guild_pref", None),
        fallback=self._loc,
      )
      self.parent_view.selected_skill = self.values[0]
      msg = _tr(
        "npc.skill_attr.skill.selected",
        loc,
        "Perícia **{skill}** selecionada. Agora escolha o atributo base abaixo.",
        skill=self.values[0]
      )
      await interaction.response.send_message(msg, ephemeral=True, delete_after=10)

  class AttributeSelect(discord.ui.Select):
    def __init__(self, attributes: list, parent_view: 'NPCLinkSkillAttributeView', locale: str = "pt"):
      self.parent_view = parent_view
      self._loc = locale

      lbl_none_attr = _tr("npc.skill_attr.none_attr", locale, "Nenhum atributo registrado")
      options = [discord.SelectOption(label=a.capitalize()) for a in attributes] if attributes else [
        discord.SelectOption(label=lbl_none_attr)
      ]

      placeholder = _tr("npc.skill_attr.attr.ph", locale, "2. Escolha o novo atributo base...")
      super().__init__(placeholder=placeholder, options=options, disabled=not attributes, custom_id="npc:skillattr:attr")

    async def callback(self, interaction: discord.Interaction):
      loc = resolve_locale(
        interaction,
        user_pref=getattr(self.parent_view.npc_context, "user_pref", None),
        guild_pref=getattr(self.parent_view.npc_context, "guild_pref", None),
        fallback=self._loc,
      )

      if self.parent_view.selected_skill is None:
        err = _tr("npc.skill_attr.need_skill_first", loc, "❌ Você precisa escolher uma perícia primeiro!")
        await interaction.response.send_message(err, ephemeral=True)
        return

      selected_attribute = self.values[0]
      npc_data = self.parent_view.npc_context.load()
      npc_data["pericias"][self.parent_view.selected_skill] = selected_attribute
      self.parent_view.npc_context.save(npc_data)

      success = _tr(
        "npc.skill_attr.link.success",
        loc,
        "✅ A perícia **{skill}** agora usa **{attr}**!",
        skill=self.parent_view.selected_skill,
        attr=selected_attribute
      )

      view = NPCLinkSkillAttributeView(self.parent_view.npc_context)
      await interaction.response.edit_message(
        content=success + "\n\n" + view.format_skills_list(),
        view=view
      )

  class BackButton(discord.ui.Button):
    def __init__(self, parent_view: 'NPCLinkSkillAttributeView', locale: str = "pt"):
      self.parent_view = parent_view
      self._loc = locale
      label = _tr("common.back", locale, "🔙 Voltar")
      super().__init__(label=label, style=discord.ButtonStyle.danger, row=2, custom_id="npc:skillattr:back")

    async def callback(self, interaction: discord.Interaction):
      from view.ficha_npc.npc_pericia_menu import NPCSkillManagementView
      view = NPCSkillManagementView(self.parent_view.npc_context)

      loc = resolve_locale(
        interaction,
        user_pref=getattr(self.parent_view.npc_context, "user_pref", None),
        guild_pref=getattr(self.parent_view.npc_context, "guild_pref", None),
        fallback=self._loc,
      )
      header = _tr("npc.skills.manage.header", loc, "⚙️ Menu de Gerenciamento de Perícias")
      await interaction.response.edit_message(content=header, view=view)

  def format_skills_list(self) -> str:
    npc_data = self.npc_context.load()
    skills_dict = npc_data.get("pericias", {})
    if not skills_dict:
      return _tr("npc.skill_attr.none_skill", self._loc, "Nenhuma perícia aprendida.")
    return "\n".join(f"• **{skill}** -> `{attr}`" for skill, attr in skills_dict.items())
