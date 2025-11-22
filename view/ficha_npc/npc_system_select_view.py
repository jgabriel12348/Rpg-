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
from utils import npc_utils, rpg_rules
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


class NPCSystemSelect(discord.ui.Select):
    def __init__(self, npc_context: npc_utils.NPCContext):
        self.npc_context = npc_context
        self._loc = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        npc_data = self.npc_context.load()
        current_system = npc_data.get("informacoes_basicas", {}).get("sistema_rpg", "dnd")
        options = []
        for key, name in rpg_rules.SUPPORTED_SYSTEMS.items():
            option = discord.SelectOption(label=name, value=key)
            if key == current_system:
                option.default = True
            options.append(option)

        placeholder = _tr(
            "npc.system.select.ph",
            self._loc,
            "Selecione o sistema de RPG para este NPC..."
        )
        super().__init__(placeholder=placeholder, options=options, custom_id="npc:system:select")

    async def callback(self, interaction: discord.Interaction):
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        await interaction.response.defer()

        loc = resolve_locale(
            interaction,
            user_pref=getattr(self.npc_context, "user_pref", None),
            guild_pref=getattr(self.npc_context, "guild_pref", None),
            fallback=self._loc,
        )

        selected_system = self.values[0]
        npc_data = self.npc_context.load()
        npc_data.setdefault("informacoes_basicas", {})["sistema_rpg"] = selected_system
        self.npc_context.save(npc_data)

        view = NPCMainMenuView(npc_context=self.npc_context)

        msg = _tr(
            "npc.system.select.done",
            loc,
            "✅ Sistema de **{name}** alterado para **{system}**!\n\n📜 Editando NPC: **{name}**",
            name=self.npc_context.npc_name,
            system=rpg_rules.SUPPORTED_SYSTEMS[selected_system]
        )

        await interaction.edit_original_response(
            content=msg,
            view=view
        )


class NPCSystemSelectView(discord.ui.View):
    def __init__(self, npc_context: npc_utils.NPCContext):
        super().__init__(timeout=180)
        self.npc_context = npc_context
        self._loc = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        self.add_item(NPCSystemSelect(npc_context=npc_context))

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, custom_id="npc:system:back")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        view = NPCMainMenuView(npc_context=self.npc_context)

        loc = resolve_locale(
            interaction,
            user_pref=getattr(self.npc_context, "user_pref", None),
            guild_pref=getattr(self.npc_context, "guild_pref", None),
            fallback=self._loc,
        )
        content = _tr(
            "npc.basic.editing",
            loc,
            "📜 Editando NPC: **{name}**",
            name=self.npc_context.npc_name
        )

        await interaction.response.edit_message(
            content=content,
            view=view
        )
