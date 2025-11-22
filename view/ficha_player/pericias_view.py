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
from utils.player_utils import load_player_sheet, save_player_sheet
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


class LinkSkillAttributeView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=180)
    self.user = user
    self.character_name = f"{user.id}_{user.name.lower()}"
    self.selected_skill = None

    ficha = load_player_sheet(self.character_name)
    self._loc = ficha.get("locale") or "pt"

    skills = list(ficha.get("pericias", {}).keys())
    attributes = list(ficha.get("atributos", {}).keys())

    self.add_item(self.SkillSelect(skills, self, locale=self._loc))
    self.add_item(self.AttributeSelect(attributes, self, locale=self._loc))

  class SkillSelect(discord.ui.Select):
    def __init__(self, skills: list, parent_view: 'LinkSkillAttributeView', locale: str = "pt"):
      self.parent_view = parent_view
      self._loc = locale

      none_opt = _tr("player.linkskill.none_skills", locale, "Nenhuma perícia aprendida")
      options = [discord.SelectOption(label=s) for s in skills] if skills else [discord.SelectOption(label=none_opt)]

      placeholder = _tr("player.linkskill.select.skill.ph", locale, "1. Escolha a perícia para modificar...")
      super().__init__(
        placeholder=placeholder,
        options=options,
        disabled=not skills,
        custom_id="player:linkskill:select-skill"
      )

    async def callback(self, interaction: discord.Interaction):
      loc = resolve_locale(interaction, fallback=self._loc)

      self.parent_view.selected_skill = self.values[0]
      msg = _tr(
        "player.linkskill.skill_selected",
        loc,
        "Perícia **{skill}** selecionada. Agora escolha o atributo base abaixo.",
        skill=self.values[0]
      )
      await interaction.response.send_message(msg, ephemeral=True, delete_after=10)

  class AttributeSelect(discord.ui.Select):
    def __init__(self, attributes: list, parent_view: 'LinkSkillAttributeView', locale: str = "pt"):
      self.parent_view = parent_view
      self._loc = locale

      none_attr = _tr("player.linkskill.none_attrs", locale, "Nenhum atributo registrado")
      options = [discord.SelectOption(label=a.capitalize()) for a in attributes] if attributes else [
        discord.SelectOption(label=none_attr)
      ]

      placeholder = _tr("player.linkskill.select.attr.ph", locale, "2. Escolha o novo atributo base...")
      super().__init__(
        placeholder=placeholder,
        options=options,
        disabled=not attributes,
        custom_id="player:linkskill:select-attr"
      )

    async def callback(self, interaction: discord.Interaction):
      loc = resolve_locale(interaction, fallback=self._loc)

      if self.parent_view.selected_skill is None:
        err = _tr("player.linkskill.need_skill_first", loc, "❌ Você precisa escolher uma perícia primeiro!")
        await interaction.response.send_message(err, ephemeral=True)
        return

      selected_attribute = self.values[0]
      ficha = load_player_sheet(self.parent_view.character_name)
      ficha["pericias"][self.parent_view.selected_skill] = selected_attribute
      save_player_sheet(self.parent_view.character_name, ficha)

      msg = _tr(
        "player.linkskill.success",
        loc,
        "✅ A perícia **{skill}** agora usa **{attr}** como atributo base!",
        skill=self.parent_view.selected_skill,
        attr=selected_attribute
      )
      await interaction.response.edit_message(content=msg, view=None)
