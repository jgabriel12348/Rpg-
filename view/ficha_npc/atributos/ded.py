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
from models.npc_modals.atributos_modais.ded_atributos.atributos_fisicos import NPCDnDAtributosFisicosModal
from models.npc_modals.atributos_modais.ded_atributos.atributos_mentais import NPCDnDAtributosMentaisModal
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale


def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
    """
    Wrapper para usar i18n.t com fallback seguro.
    Sua i18n.t retorna a PRÓPRIA chave quando não encontra; se acontecer, usamos o fallback.
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


class NPCDnDAtributosView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context
        self._base_loc = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )
        self._label_phys = _tr("npc.menu.attributes.physical", self._base_loc, "💪 Atributos Físicos")
        self._label_ment = _tr("npc.menu.attributes.mental",   self._base_loc, "🧠 Atributos Mentais/Sociais")
        self._label_back = _tr("common.back",                  self._base_loc, "🔙 Voltar")

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "npc:dnd:attrs:physical":
                    item.label = self._label_phys
                elif item.custom_id == "npc:dnd:attrs:mental":
                    item.label = self._label_ment
                elif item.custom_id == "npc:back":
                    item.label = self._label_back

    @discord.ui.button(
        label="💪 Atributos Físicos",
        style=discord.ButtonStyle.primary,
        custom_id="npc:dnd:attrs:physical"
    )
    async def fisicos(self, interaction: discord.Interaction, button: discord.ui.Button):
        # >>> PASSAR interaction para o modal <<<
        await interaction.response.send_modal(NPCDnDAtributosFisicosModal(self.npc_context, interaction))

    @discord.ui.button(
        label="🧠 Atributos Mentais/Sociais",
        style=discord.ButtonStyle.secondary,
        custom_id="npc:dnd:attrs:mental"
    )
    async def mentais(self, interaction: discord.Interaction, button: discord.ui.Button):
        # >>> PASSAR interaction para o modal <<<
        await interaction.response.send_modal(NPCDnDAtributosMentaisModal(self.npc_context, interaction))

    @discord.ui.button(
        label="🔙 Voltar",
        style=discord.ButtonStyle.danger,
        custom_id="npc:back"
    )
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction)

        from view.ficha_npc.npc_submenu import NPCMainMenuView
        view = NPCMainMenuView(npc_context=self.npc_context)

        content = _tr(
            "npc.menu.attributes.prompt",
            loc,
            "💪 Escolha um sistema para editar os atributos de **{npc_name}**:",
            npc_name=self.npc_context.npc_name
        )

        await interaction.response.edit_message(content=content, view=view)
