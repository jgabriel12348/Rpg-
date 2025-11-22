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
from models.player_modals.config_avancada.notas import NotesModal
from models.player_modals.config_avancada.aliados import AddAllyModal
from models.player_modals.config_avancada.inimigos import AddEnemyModal
from models.player_modals.config_avancada.medos import AddFearModal
from models.player_modals.config_avancada.segredos import AddSecretModal
from models.player_modals.config_avancada.dashboard import RoleplayDashboardView
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


class PlayerRoleplayMenuView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=None)
    self.user = user
    self._loc = "pt"
    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "player:roleplay:notes":
          item.label = _tr("player.roleplay.btn.notes", self._loc, "✏️ Editar Notas")
        elif item.custom_id == "player:roleplay:allies":
          item.label = _tr("player.roleplay.btn.allies", self._loc, "👥 Aliados")
        elif item.custom_id == "player:roleplay:enemies":
          item.label = _tr("player.roleplay.btn.enemies", self._loc, "🥷 Inimigos")
        elif item.custom_id == "player.roleplay:fears":
          item.label = _tr("player.roleplay.btn.fears", self._loc, "😱 Medos/Fobias")
        elif item.custom_id == "player:roleplay:fears":
          item.label = _tr("player.roleplay.btn.fears", self._loc, "😱 Medos/Fobias")
        elif item.custom_id == "player:roleplay:secrets":
          item.label = _tr("player.roleplay.btn.secrets", self._loc, "🔒 Segredos")
        elif item.custom_id == "player:roleplay:back":
          item.label = _tr("common.back", self._loc, "🔙 Voltar")

  def create_list_embed(self, category: str, category_name: str, icon: str) -> discord.Embed:
    character_name = f"{self.user.id}_{self.user.name.lower()}"
    ficha = player_utils.load_player_sheet(character_name)
    items = ficha.get("roleplay", {}).get(category, [])

    display_name = _tr(f"player.roleplay.{category}.title", self._loc, category_name)
    title = f"{icon} {display_name}"

    embed = discord.Embed(title=title, color=discord.Color.blue())

    if not items:
      none_text = _tr(
        "player.roleplay.none",
        self._loc,
        "Nenhum(a) {name} registrado(a).",
        name=display_name.lower()
      )
      embed.description = none_text
    else:
      description = ""
      for item in items:
        title_key = next(iter(item))
        description += f"**{item[title_key]}**\n"
      embed.description = description
    return embed

  @discord.ui.button(label="✏️ Editar Notas", style=discord.ButtonStyle.primary, custom_id="player:roleplay:notes")
  async def edit_notas(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.send_modal(NotesModal(interaction=interaction))

  @discord.ui.button(label="👥 Aliados", style=discord.ButtonStyle.success, custom_id="player:roleplay:allies")
  async def allies_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_list_embed('aliados', 'Aliados', '👥')
    view = RoleplayDashboardView(self.user, 'aliados', _tr("player.roleplay.allies.title", self._loc, "Aliados"), AddAllyModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="🥷 Inimigos", style=discord.ButtonStyle.secondary, custom_id="player:roleplay:enemies")
  async def enemies_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_list_embed('inimigos', 'Inimigos', '🥷')
    view = RoleplayDashboardView(self.user, 'inimigos', _tr("player.roleplay.enemies.title", self._loc, "Inimigos"), AddEnemyModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="😱 Medos/Fobias", style=discord.ButtonStyle.danger, custom_id="player:roleplay:fears")
  async def fears_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_list_embed('medos_fobias', 'Medos e Fobias', '😱')
    view = RoleplayDashboardView(self.user, 'medos_fobias', _tr("player.roleplay.fears.title", self._loc, "Medos e Fobias"), AddFearModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="🔒 Segredos", style=discord.ButtonStyle.blurple, custom_id="player:roleplay:secrets")
  async def secrets_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = self.create_list_embed('segredos', 'Segredos', '🔒')
    view = RoleplayDashboardView(self.user, 'segredos', _tr("player.roleplay.secrets.title", self._loc, "Segredos"), AddSecretModal)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, custom_id="player:roleplay:back")
  async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
    from view.ficha_player.ficha_player_menu import PlayerMainMenuView
    self._loc = resolve_locale(interaction, fallback=self._loc)
    content = _tr("player.menu.main.title", self._loc, "🎮 Menu Principal do Player")
    await interaction.response.edit_message(content=content, view=PlayerMainMenuView(user=self.user))
