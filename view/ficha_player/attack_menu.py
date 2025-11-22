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
from models.player_modals.info_combate.info_combate_modal import PlayerCombatInfoModal
from models.player_modals.info_combate.info_deslocamento import PlayerMovementInfoModal
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
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

class RegisterAbilityView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self._loc = "pt"

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "player:ability:combat_info":
                    item.label = _tr("player.ability.combat_info", self._loc, "🛡️ Informações de Combate")
                elif item.custom_id == "player:ability:movement_info":
                    item.label = _tr("player.ability.movement_info", self._loc, "🏃‍♂️ Deslocamento e Resistências")
                elif item.custom_id == "player:ability:register_attack":
                    item.label = _tr("player.ability.register_attack", self._loc, "📝 Registrar Ataque")
                elif item.custom_id == "player:ability:register_spell":
                    item.label = _tr("player.ability.register_spell", self._loc, "🔮 Registrar Magia")
                elif item.custom_id == "player:ability:back":
                    item.label = _tr("common.back", self._loc, "🔙 Voltar")

    @discord.ui.button(label="player.ability.combat_info", style=discord.ButtonStyle.primary, row=0, custom_id="player:ability:combat_info")
    async def combate_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayerCombatInfoModal(interaction))

    @discord.ui.button(label="player.ability.movement_info", style=discord.ButtonStyle.secondary, row=0, custom_id="player:ability:movement_info")
    async def deslocamento_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayerMovementInfoModal(interaction))

    @discord.ui.button(label="player.ability.register_attack", style=discord.ButtonStyle.success, row=0, custom_id="player:ability:register_attack")
    async def register_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        attack_id = f"{interaction.user.id}-{int(time.time())}"
        view = AttackBuilderView(user=interaction.user, attack_id=attack_id)
        embed = view.create_embed()
        await interaction.response.edit_message(content=None, embed=embed, view=view)

    @discord.ui.button(label="player.ability.register_spell", style=discord.ButtonStyle.primary, row=0, custom_id="player:ability:register_spell")
    async def register_spell(self, interaction: discord.Interaction, button: discord.ui.Button):
        spell_id = f"{interaction.user.id}-{int(time.time())}"
        view = SpellBuilderView(user=interaction.user, spell_id=spell_id)
        embed = view.create_embed()
        await interaction.response.edit_message(content=None, embed=embed, view=view)

    @discord.ui.button(label="common.back", style=discord.ButtonStyle.danger, row=1, custom_id="player:ability:back")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_player.ficha_player_menu import PlayerMainMenuView
        loc = resolve_locale(interaction, fallback=self._loc)
        content = _tr("player.menu.main.title", loc, "🎮 Menu Principal do Player")
        await interaction.response.edit_message(content=content, view=PlayerMainMenuView(user=self.user))
