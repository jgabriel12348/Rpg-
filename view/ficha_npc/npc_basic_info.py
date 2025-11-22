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
from models.npc_modals.info_basicas.info_basicas import NPCBasicInfoModal
from models.npc_modals.info_basicas.info_gerais import NPCGeneralInfoModal
from models.npc_modals.info_basicas.info_extras import NPCExtraInfoModal
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
    """
    Wrapper para usar i18n.t com fallback.
    Se a chave não existir (retorna a própria key), usa o fallback informado.
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


def _loc_from_interaction(interaction: discord.Interaction, base_locale: str = "pt") -> str:
    try:
        loc = resolve_locale(interaction)
        return loc or base_locale
    except Exception:
        return base_locale


class NPCBasicInfoView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context

        base_locale = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        self._lbl_only_gm = _tr("npc.basic.only_gm", base_locale, "Apenas o mestre que criou este NPC pode editá-lo.")
        self._lbl_basic   = _tr("npc.basic.tabs.basic",   base_locale, "📜 Informações Básicas")
        self._lbl_general = _tr("npc.basic.tabs.general", base_locale, "📃 Informações Gerais")
        self._lbl_extra   = _tr("npc.basic.tabs.extra",   base_locale, "➕ Informações Extras")
        self._lbl_back    = _tr("common.back",            base_locale, "🔙 Voltar")

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "npc:basic:add_basic":
                    item.label = self._lbl_basic
                elif item.custom_id == "npc:basic:add_general":
                    item.label = self._lbl_general
                elif item.custom_id == "npc:basic:add_extra":
                    item.label = self._lbl_extra
                elif item.custom_id == "npc:basic:back":
                    item.label = self._lbl_back

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.npc_context.mestre_id:
            loc = _loc_from_interaction(interaction, "pt")
            only_gm_msg = _tr("npc.basic.only_gm", loc, "Apenas o mestre que criou este NPC pode editá-lo.")
            await interaction.response.send_message(only_gm_msg, ephemeral=True)
            return False
        return True

    @discord.ui.button(
        label="npc.basic.tabs.basic",
        style=discord.ButtonStyle.success,
        custom_id="npc:basic:add_basic"
    )
    async def add_basic_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            NPCBasicInfoModal(npc_context=self.npc_context, interaction=interaction)
        )

    @discord.ui.button(
        label="npc.basic.tabs.general",
        style=discord.ButtonStyle.secondary,
        custom_id="npc:basic:add_general"
    )
    async def add_general_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            NPCGeneralInfoModal(npc_context=self.npc_context, interaction=interaction)
        )

    @discord.ui.button(
        label="npc.basic.tabs.extra",
        style=discord.ButtonStyle.primary,
        custom_id="npc:basic:add_extra"
    )
    async def add_extra_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            NPCExtraInfoModal(npc_context=self.npc_context, interaction=interaction)
        )

    @discord.ui.button(
        label="common.back",
        style=discord.ButtonStyle.danger,
        custom_id="npc:basic:back"
    )
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = _loc_from_interaction(interaction, "pt")
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        view = NPCMainMenuView(npc_context=self.npc_context)

        content = _tr(
            "npc.basic.editing",
            loc,
            "📜 Editando NPC: **{name}**",
            name=self.npc_context.npc_name
        )

        await interaction.response.edit_message(content=content, view=view)
