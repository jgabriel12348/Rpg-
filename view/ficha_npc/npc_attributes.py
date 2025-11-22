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
from view.ficha_npc.atributos.cthulhu import NPCCthulhuAtributosView
from view.ficha_npc.atributos.cyberpunk import NPCCyberpunkMenu
from view.ficha_npc.atributos.ded import NPCDnDAtributosView
from view.ficha_npc.atributos.skifall import NPCSkifallAtributosView
from view.ficha_npc.atributos.vampiro import NPCVampiroAtributosView
from view.ficha_npc.atributos.ordem import NPCOrdemAtributosView

class NPCAtributosMenuView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context

    @discord.ui.button(label="⚔️ D&D", style=discord.ButtonStyle.primary, row=1)
    async def dnd_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCDnDAtributosView(self.npc_context)
        await interaction.response.edit_message(
            content=f"💠 Editando atributos de D&D/T20 para **{self.npc_context.npc_name}**:",
            view=view
        )

    @discord.ui.button(label="💀 Ordem Paranormal", style=discord.ButtonStyle.secondary, row=1, disabled=False)
    async def ordem_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCOrdemAtributosView(self.npc_context)
        await interaction.response.edit_message(
            content=f"💠 Editando atributos de Ordem Paranormal para **{self.npc_context.npc_name}**:",
            view=view
        )

    @discord.ui.button(label="🤖 Cyberpunk", style=discord.ButtonStyle.primary, row=2)
    async def cyberpunk_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCCyberpunkMenu(self.npc_context)
        await interaction.response.edit_message(
            content=f"💠 Editando atributos de Cyberpunk para **{self.npc_context.npc_name}**:",
            view=view
        )

    @discord.ui.button(label="🐙 Call of Cthulhu", style=discord.ButtonStyle.blurple, row=1)
    async def coc_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCCthulhuAtributosView(self.npc_context)
        await interaction.response.edit_message(
            content=f"💠 Editando atributos de Call of Cthulhu para **{self.npc_context.npc_name}**:",
            view=view
        )

    @discord.ui.button(label="❄️ SkiFall RPG", style=discord.ButtonStyle.secondary, row=2)
    async def skifall_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCSkifallAtributosView(self.npc_context)
        await interaction.response.edit_message(
            content=f"💠 Editando atributos de SkiFall RPG para **{self.npc_context.npc_name}**:",
            view=view
        )

    @discord.ui.button(label="🧛 Vampiro: A Máscara", style=discord.ButtonStyle.danger, row=1)
    async def vampire_attributes(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCVampiroAtributosView(self.npc_context)
        await interaction.response.edit_message(
            content=f"💠 Editando atributos de Vampiro: A Máscara para **{self.npc_context.npc_name}**:",
            view=view
        )

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.danger, row=2)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        view = NPCMainMenuView(npc_context=self.npc_context)
        await interaction.response.edit_message(
            content=f"📜 Editando NPC: **{self.npc_context.npc_name}**",
            view=view
        )