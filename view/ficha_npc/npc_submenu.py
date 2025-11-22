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
from view.ficha_npc.npc_basic_info import NPCBasicInfoView
from view.ficha_npc.atributos.ded import NPCDnDAtributosView
from view.ficha_npc.npc_skills import NPCSkillsView
from view.ficha_npc.npc_itens import NPCInventoryView
from view.ficha_npc.npc_status import NPCStatusCondicoesView
from view.ficha_npc.npc_config_avancada import NPCConfigAvancadasView
from view.ficha_npc.npc_skill_management_view import NPCSkillManagementView
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


class NPCMainMenuView(discord.ui.View):
    def __init__(self, npc_context):
        super().__init__(timeout=None)
        self.npc_context = npc_context

        self._loc = (
            getattr(npc_context, "locale", None)
            or getattr(npc_context, "user_locale", None)
            or getattr(npc_context, "guild_locale", None)
            or "pt"
        )

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "npc:menu:info":
                    item.label = _tr("npc.menu.info", self._loc, "📜 Informações")
                elif item.custom_id == "npc:menu:attributes":
                    item.label = _tr("npc.menu.attributes", self._loc, "💪 Atributos")
                elif item.custom_id == "npc:menu:inventory":
                    item.label = _tr("npc.menu.inventory", self._loc, "🎒 Inventário")
                elif item.custom_id == "npc:menu:combat":
                    item.label = _tr("npc.menu.combat", self._loc, "⚔️ Combate")
                elif item.custom_id == "npc:menu:status":
                    item.label = _tr("npc.menu.status", self._loc, "❤️ Status & Condições")
                elif item.custom_id == "npc:menu:skills":
                    item.label = _tr("npc.menu.skills", self._loc, "💡 Perícias")
                elif item.custom_id == "npc:menu:advanced":
                    item.label = _tr("npc.menu.advanced", self._loc, "⚙️ Configurações Avançadas")
                elif item.custom_id == "npc:menu:change_base_attr":
                    item.label = _tr("npc.menu.change_base_attr", self._loc, "⚙️ Alterar Atributo Base")

    @discord.ui.button(label="npc.menu.info", style=discord.ButtonStyle.primary, custom_id="npc:menu:info")
    async def info_basicas(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(
            interaction,
            fallback=self._loc,
        )
        content = _tr("npc.menu.edit.info", loc, "📜 Editando informações de **{name}**:", name=self.npc_context.npc_name)
        await interaction.response.edit_message(
            content=content,
            view=NPCBasicInfoView(self.npc_context)
        )

    @discord.ui.button(label="npc.menu.attributes", style=discord.ButtonStyle.secondary,
                       custom_id="npc:menu:attributes")
    async def atributos(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction)
        content = _tr(
            "npc.menu.edit.attributes",
            loc,
            "💪 Editando atributos de **{name}**:",
            name=self.npc_context.npc_name
        )

        await interaction.response.edit_message(
            content=content,
            view=NPCDnDAtributosView(self.npc_context)
        )

    @discord.ui.button(label="npc.menu.inventory", style=discord.ButtonStyle.primary, custom_id="npc:menu:inventory")
    async def inventario(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction)

        content = _tr(
            "npc.menu.edit.inventory",
            loc,
            "🎒 Editando inventário de **{name}**:",
            name=self.npc_context.npc_name
        )

        await interaction.response.edit_message(
            content=content,
            view=NPCInventoryView(self.npc_context)
        )

    @discord.ui.button(label="npc.menu.combat", style=discord.ButtonStyle.success, custom_id="npc:menu:combat")
    async def ataques_habilidades(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction

        loc = resolve_locale(interaction)
        content = _tr("npc.menu.edit.combat", loc, "⚔️ Editando ataques e habilidades de **{name}**:",
                      name=self.npc_context.npc_name)

        from view.ficha_npc.npc_skills import NPCSkillsView
        await interaction.response.edit_message(
            content=content,
            view=NPCSkillsView(self.npc_context)
        )

    @discord.ui.button(label="npc.menu.status", style=discord.ButtonStyle.secondary, custom_id="npc:menu:status")
    async def status_condicoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction) or getattr(self, "_loc", "pt")

        content = _tr(
            "npc.menu.edit.status",
            loc,
            "❤️ Editando status e condições de **{name}**:",
            name=self.npc_context.npc_name
        )
        await interaction.response.edit_message(
            content=content,
            view=NPCStatusCondicoesView(self.npc_context)
        )

    @discord.ui.button(label="npc.menu.skills", style=discord.ButtonStyle.success, custom_id="npc:menu:skills")
    async def manage_skills(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCSkillManagementView(self.npc_context)
        embed = view.create_embed()
        await interaction.response.edit_message(
            content=None,
            embed=embed,
            view=view
        )

    @discord.ui.button(label="npc.menu.advanced", style=discord.ButtonStyle.primary, custom_id="npc:menu:advanced")
    async def config_avancadas(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction) or getattr(self, "_loc", "pt")
        content = _tr(
            "npc.menu.edit.advanced",
            loc,
            "⚙️ Editando configurações avançadas de **{name}**:",
            name=self.npc_context.npc_name
        )
        await interaction.response.edit_message(
            content=content,
            view=NPCConfigAvancadasView(self.npc_context),
            embed=None
        )

    @discord.ui.button(label="npc.menu.change_base_attr", style=discord.ButtonStyle.primary, custom_id="npc:menu:change_base_attr")
    async def alterar_atributo_base(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction) or getattr(self, "_loc", "pt")
        content = _tr("npc.menu.edit.change_base_attr", loc, "Selecione a perícia que deseja alterar para **{name}**:", name=self.npc_context.npc_name)
        await interaction.response.edit_message(
            content=content,
            view=NPCSkillManagementView(self.npc_context)
        )
