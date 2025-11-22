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
import time
from models.player_modals.info_combate.attack_builder import AttackBuilderView
from models.player_modals.info_combate.spell_builder_view import SpellBuilderView
from models.player_modals.info_combate.remove_attack_view import RemoveAttackView
from models.player_modals.info_combate.info_combate_modal import PlayerCombatInfoModal
from models.player_modals.info_combate.info_deslocamento import PlayerMovementInfoModal
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


class PlayerAtaquesMenuView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user

        self._loc = "pt"

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "player:atk:combat_info":
                    item.label = _tr("player.attacks.btn.combat_info", self._loc, "🛡️ Informações de Combate")
                elif item.custom_id == "player:atk:movement_info":
                    item.label = _tr("player.attacks.btn.movement_info", self._loc, "🏃‍♂️ Deslocamento e Resistências")
                elif item.custom_id == "player:atk:register_attack":
                    item.label = _tr("player.attacks.btn.register_attack", self._loc, "📝 Registrar Ataque")
                elif item.custom_id == "player:atk:register_spell":
                    item.label = _tr("player.attacks.btn.register_spell", self._loc, "🔮 Registrar Magia")
                elif item.custom_id == "player:atk:remove":
                    item.label = _tr("player.attacks.btn.remove", self._loc, "➖ Remover Ataque/Magia")
                elif item.custom_id == "player:atk:back":
                    item.label = _tr("common.back", self._loc, "🔙 Voltar")

    @discord.ui.button(label="🛡️ Informações de Combate", style=discord.ButtonStyle.primary, row=0, custom_id="player:atk:combat_info")
    async def combate_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayerCombatInfoModal(interaction))

    @discord.ui.button(label="🏃‍♂️ Deslocamento e Resistências", style=discord.ButtonStyle.secondary, row=0, custom_id="player:atk:movement_info")
    async def deslocamento_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayerMovementInfoModal(interaction))

    @discord.ui.button(label="📝 Registrar Ataque", style=discord.ButtonStyle.success, custom_id="player:atk:register_attack")
    async def register_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction, fallback=self._loc)
        attack_id = f"{interaction.user.id}-{int(time.time())}"
        view = AttackBuilderView(user=self.user, attack_id=attack_id)
        embed = view.create_embed()
        content = _tr("player.attacks.register_attack.title", loc, "Registre Seu Ataque")
        await interaction.response.edit_message(content=content, embed=embed, view=view)

    @discord.ui.button(label="🔮 Registrar Magia", style=discord.ButtonStyle.primary, custom_id="player:atk:register_spell")
    async def register_spell(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction, fallback=self._loc)
        spell_id = f"{interaction.user.id}-{int(time.time())}"
        view = SpellBuilderView(user=self.user, spell_id=spell_id)
        embed = view.create_embed()
        content = _tr("player.attacks.register_spell.title", loc, "Registre Sua Magia")
        await interaction.response.edit_message(content=content, embed=embed, view=view)

    @discord.ui.button(label="➖ Remover Ataque/Magia", style=discord.ButtonStyle.danger, custom_id="player:atk:remove")
    async def remove_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction, fallback=self._loc)
        view = RemoveAttackView(user=self.user, previous_view=self)
        prompt = _tr("player.attacks.remove.prompt", loc, "Selecione um ou mais ataques/magias para remover:")
        await interaction.response.edit_message(content=prompt, view=view)

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.secondary, custom_id="player:atk:back")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_player.ficha_player_menu import PlayerMainMenuView
        loc = resolve_locale(interaction, fallback=self._loc)
        view = PlayerMainMenuView(user=self.user)
        content = _tr("player.menu.main.title", loc, "🎮 Menu Principal do Player")
        await interaction.response.edit_message(content=content, view=view)
