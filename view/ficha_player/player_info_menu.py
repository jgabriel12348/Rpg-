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
from models.player_modals.info_basicas.info_basicas import PlayerBasicInfoModal
from models.player_modals.info_basicas.info_gerais import PlayerGeneralInfoModal
from models.player_modals.info_basicas.info_extras import PlayerExtraInfoModal
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


class PlayerInfoMenuView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self._loc = "pt"

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "player:info:basic":
                    item.label = _tr("player.info.btn.basic", self._loc, "📋 Informações Básicas")
                elif item.custom_id == "player:info:general":
                    item.label = _tr("player.info.btn.general", self._loc, "📋 Informações Gerais")
                elif item.custom_id == "player:info:extra":
                    item.label = _tr("player.info.btn.extra", self._loc, "📋 Informações Extras")
                elif item.custom_id == "player:info:back":
                    item.label = _tr("common.back", self._loc, "🔙 Voltar")

    @discord.ui.button(label="📋 Informações Básicas", style=discord.ButtonStyle.primary, custom_id="player:info:basic")
    async def basic_info(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(PlayerBasicInfoModal(interaction))

    @discord.ui.button(label="📋 Informações Gerais", style=discord.ButtonStyle.secondary, custom_id="player:info:general")
    async def general_info(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(PlayerGeneralInfoModal(interaction))

    @discord.ui.button(label="📋 Informações Extras", style=discord.ButtonStyle.success, custom_id="player:info:extra")
    async def extra_info(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_modal(PlayerExtraInfoModal(interaction))

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, custom_id="player:info:back")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
      from view.ficha_player.ficha_player_menu import PlayerMainMenuView
      loc = resolve_locale(interaction, fallback=self._loc)
      content = _tr("player.menu.main.title", loc, "🎮 Menu Principal do Player")
      await interaction.response.edit_message(content=content, view=PlayerMainMenuView(user=self.user))
