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
from models.npc_modals.satus_modais.carga_modal import NPCCargaModal
from models.npc_modals.satus_modais.alinhamento import NPCAlignmentModal
from models.npc_modals.satus_modais.alianca import NPCAllianceModal
from models.npc_modals.satus_modais.objetivos import NPCObjectivesModal
from models.npc_modals.satus_modais.personalidade import NPCPersonalityModal
from models.npc_modals.satus_modais.extras import NPCExtrasModal
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


class NPCStatusCondicoesView(discord.ui.View):
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
                if item.custom_id == "npc:status:carga":
                    item.label = _tr("npc.status.btn.carga", self._loc, "💪 Carga")
                elif item.custom_id == "npc:status:alinhamento":
                    item.label = _tr("npc.status.btn.alignment", self._loc, "🧠 Alinhamento")
                elif item.custom_id == "npc:status:aliancas":
                    item.label = _tr("npc.status.btn.alliances", self._loc, "🔰 Alianças")
                elif item.custom_id == "npc:status:objetivos":
                    item.label = _tr("npc.status.btn.objectives", self._loc, "📌 Objetivos")
                elif item.custom_id == "npc:status:personalidade":
                    item.label = _tr("npc.status.btn.personality", self._loc, "🎭 Personalidade")
                elif item.custom_id == "npc:status:extras":
                    item.label = _tr("npc.status.btn.extras", self._loc, "➕ Extras")
                elif item.custom_id == "npc:status:back":
                    item.label = _tr("common.back", self._loc, "🔙 Voltar")

    @discord.ui.button(label="npc.status.btn.carga", style=discord.ButtonStyle.primary, row=0, custom_id="npc:status:carga")
    async def carga(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NPCCargaModal(self.npc_context, interaction))

    @discord.ui.button(label="npc.status.btn.alignment", style=discord.ButtonStyle.secondary, row=0, custom_id="npc:status:alinhamento")
    async def alinhamento(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NPCAlignmentModal(self.npc_context, interaction))

    @discord.ui.button(label="npc.status.btn.alliances", style=discord.ButtonStyle.success, row=0, custom_id="npc:status:aliancas")
    async def aliancas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NPCAllianceModal(self.npc_context, interaction))

    @discord.ui.button(label="npc.status.btn.objectives", style=discord.ButtonStyle.primary, row=1, custom_id="npc:status:objetivos")
    async def objetivos(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NPCObjectivesModal(self.npc_context, interaction))

    @discord.ui.button(label="npc.status.btn.personality", style=discord.ButtonStyle.secondary, row=1, custom_id="npc:status:personalidade")
    async def personalidade(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NPCPersonalityModal(self.npc_context, interaction))

    @discord.ui.button(label="npc.status.btn.extras", style=discord.ButtonStyle.success, row=1, custom_id="npc:status:extras")
    async def extras(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NPCExtrasModal(self.npc_context, interaction))

    @discord.ui.button(label="common.back", style=discord.ButtonStyle.danger, row=2, custom_id="npc:status:back")
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        view = NPCMainMenuView(self.npc_context)
        loc = resolve_locale(interaction) or self._loc
        content = _tr("npc.basic.editing", loc, "📜 Editando NPC: **{name}**", name=self.npc_context.npc_name)

        await interaction.response.edit_message(
            content=content,
            view=view
        )
