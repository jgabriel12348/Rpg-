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
from models.player_modals.info_combate.attack_edit_modal import AttackEditModal
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


class EditAttackView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=180)
    self.user = user

    character_name = f"{user.id}_{user.name.lower()}"
    self.ficha = player_utils.load_player_sheet(character_name)
    self._loc = self.ficha.get("locale") or "pt"

    ataques = self.ficha.get("ataques", [])
    self.add_item(self.AttackSelect(ataques, self, locale=self._loc))

  class AttackSelect(discord.ui.Select):
    def __init__(self, ataques: list, parent_view: 'EditAttackView', locale: str = "pt"):
      self.parent_view = parent_view
      self._loc = locale

      options = [discord.SelectOption(label=a['nome']) for a in ataques]
      if not options:
        options.append(
          discord.SelectOption(
            label=_tr("player.edit_attack.none", locale, "Nenhum ataque para editar"),
            value="NO_ATTACKS"
          )
        )

      placeholder = _tr("player.edit_attack.select.ph", locale, "Selecione um ataque para editar...")
      super().__init__(
        placeholder=placeholder,
        options=options,
        disabled=not ataques,
        custom_id="player:attackedit:select"
      )

    async def callback(self, interaction: discord.Interaction):
      loc = resolve_locale(interaction, fallback=self._loc)

      selected_name = self.values[0]
      if selected_name == "NO_ATTACKS":
        await interaction.response.defer()
        return

      attack_to_edit = next((a for a in self.parent_view.ficha['ataques'] if a['nome'] == selected_name), None)

      if attack_to_edit:
        await interaction.response.send_modal(AttackEditModal(interaction, attack_to_edit))
