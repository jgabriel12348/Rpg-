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
from models.player_modals.player_basic_modal import PlayerModalBase
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


class LearnSkillsModal(PlayerModalBase):
  def __init__(self, interaction: discord.Interaction):
    loc = resolve_locale(interaction, fallback="pt")

    title = _tr("player.skills.learn.modal.title", loc, "💡 Aprender Novas Perícias")
    super().__init__(interaction, title=title, custom_id="player:skills:learn")
    self._loc = loc

    self.skills_input = discord.ui.TextInput(
      label=_tr("player.skills.learn.field.label", loc, "Perícias para aprender"),
      style=discord.TextStyle.paragraph,
      placeholder=_tr(
        "player.skills.learn.field.ph",
        loc,
        "Digite as perícias separadas por vírgula.\nEx: Atletismo, Furtividade, Arcanismo, Investigação"
      ),
      custom_id="player:skills:learn:field"
    )
    self.add_item(self.skills_input)

  async def on_submit(self, interaction: discord.Interaction):
    novas_pericias = [skill.strip() for skill in self.skills_input.value.split(',') if skill.strip()]
    pericias_atuais = self.ficha.setdefault("pericias", {})
    for pericia in novas_pericias:
      if pericia not in pericias_atuais:
        pericias_atuais[pericia] = "N/A"

    self.save()

    loc = resolve_locale(interaction, fallback=self._loc)
    msg = _tr(
      "player.skills.learn.added",
      loc,
      "💡 **{count}** perícias foram adicionadas à sua ficha!",
      count=len(novas_pericias)
    )
    await interaction.response.send_message(msg, ephemeral=True)
