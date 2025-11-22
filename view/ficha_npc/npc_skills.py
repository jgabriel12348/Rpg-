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
from utils.npc_utils import NPCContext
from models.npc_modals.info_combate.info_combate_modal import NPCCombatInfoModal
from models.npc_modals.info_combate.info_deslocamento import NPCMovementInfoModal
from models.npc_modals.info_combate.attack_builder import NPCAttackBuilderView
from models.npc_modals.info_combate.spell_builder_view import NPCSpellBuilderView
from view.ficha_npc.npc_remove_attack_view import NPCRemoveAttackView
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


class NPCSkillsView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context
        self._loc = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "npc:skills:combat_info":
                    item.label = _tr("npc.skills.btn.combat_info", self._loc, "🛡️ Informações de Combate")
                elif item.custom_id == "npc:skills:movement_info":
                    item.label = _tr("npc.skills.btn.movement_info", self._loc, "🏃‍♂️ Deslocamento e Resistências")
                elif item.custom_id == "npc:skills:add_attack":
                    item.label = _tr("npc.skills.btn.add_attack", self._loc, "🗡️ Registrar Ataque")
                elif item.custom_id == "npc:skills:add_spell":
                    item.label = _tr("npc.skills.btn.add_spell", self._loc, "🪄 Registrar Magia")
                elif item.custom_id == "npc:skills:remove":
                    item.label = _tr("npc.skills.btn.remove", self._loc, "➖ Remover Habilidade")
                elif item.custom_id == "npc:skills:back":
                    item.label = _tr("common.back", self._loc, "🔙 Voltar")

    @discord.ui.button(label="npc.skills.btn.combat_info", style=discord.ButtonStyle.primary, custom_id="npc:skills:combat_info")
    async def combate_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Garante que os modais consigam resolver o locale via npc_context.interaction
        self.npc_context.interaction = interaction
        await interaction.response.send_modal(NPCCombatInfoModal(self.npc_context, interaction=interaction))

    @discord.ui.button(label="npc.skills.btn.movement_info", style=discord.ButtonStyle.secondary, custom_id="npc:skills:movement_info")
    async def deslocamento_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        await interaction.response.send_modal(NPCMovementInfoModal(self.npc_context, interaction=interaction))

    @discord.ui.button(label="npc.skills.btn.add_attack", style=discord.ButtonStyle.success, custom_id="npc:skills:add_attack")
    async def add_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        attack_id = f"{interaction.user.id}-{int(time.time())}"
        view = NPCAttackBuilderView(npc_context=self.npc_context, attack_id=attack_id)
        embed = view.create_embed()
        await interaction.response.edit_message(content=None, embed=embed, view=view)

    @discord.ui.button(label="npc.skills.btn.add_spell", style=discord.ButtonStyle.primary, custom_id="npc:skills:add_spell")
    async def add_magic(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        spell_id = f"{interaction.user.id}-{int(time.time())}"
        view = NPCSpellBuilderView(npc_context=self.npc_context, spell_id=spell_id)
        embed = view.create_embed()
        await interaction.response.edit_message(content=None, embed=embed, view=view)

    @discord.ui.button(label="npc.skills.btn.remove", style=discord.ButtonStyle.danger, custom_id="npc:skills:remove")
    async def remove_skill(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        view = NPCRemoveAttackView(npc_context=self.npc_context, previous_view=self)

        loc = resolve_locale(interaction)
        content = _tr(
            "npc.skills.remove.header",
            loc,
            "Selecione as habilidades para remover da ficha de **{name}**:",
            name=self.npc_context.npc_name
        )

        await interaction.response.edit_message(content=content, view=view)

    @discord.ui.button(label="common.back", style=discord.ButtonStyle.secondary, custom_id="npc:skills:back")
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        self.npc_context.interaction = interaction
        view = NPCMainMenuView(self.npc_context)

        loc = resolve_locale(interaction)
        content = _tr("npc.basic.editing", loc, "📜 Editando NPC: **{name}**", name=self.npc_context.npc_name)

        await interaction.response.edit_message(content=content, view=view)
