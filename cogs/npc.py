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
from discord.ext import commands
from discord import app_commands
from typing import List
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale
from utils import mestre_utils
from utils.npc_utils import NPCContext
from utils.embed_utils import create_npc_summary_embed
from view.ficha_npc.gm_npc_sheet_view import GMNPCSheetView
from view.rolling.npc_dice_hub_view import NPCDiceHubView
from view.ficha_npc.npc_main_menu_view import NPCSelectView

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


def localized_command_en_base(name_en: str, desc_en: str, *, pt_name: str, pt_desc: str):
    def decorator(func):
        cmd = app_commands.command(name=name_en, description=desc_en)(func)
        cmd.name_localizations = {
            "pt-BR": pt_name,
            "en-US": name_en,
            "en-GB": name_en,
        }
        cmd.description_localizations = {
            "pt-BR": pt_desc,
            "en-US": desc_en,
            "en-GB": desc_en,
        }
        return cmd
    return decorator


class NPCCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _autocomplete_npc_names(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> List[app_commands.Choice[str]]:
        guild = interaction.guild
        if guild is None:
            return []

        query = (current or "").lower()
        user_id = interaction.user.id
        guild_id = guild.id

        choices: List[app_commands.Choice[str]] = []

        if mestre_utils.verificar_mestre(guild.name, user_id):
            names = NPCContext.list_npcs(guild_id, user_id)
            for n in names:
                if (not query) or (query in n.lower()):
                    choices.append(app_commands.Choice(name=n, value=n))
        else:
            names = NPCContext.list_npcs(guild_id, user_id)
            for n in names:
                try:
                    data = NPCContext(guild_id, user_id, n).load()
                    if data.get("visivel_para_players"):
                        if (not query) or (query in n.lower()):
                            choices.append(app_commands.Choice(name=n, value=n))
                except Exception:
                    continue

        return choices[:25]

    @localized_command_en_base(
        name_en="npc_menu",
        desc_en="Open the NPC menu (create/edit/manage).",
        pt_name="npc_menu",
        pt_desc="Abrir o menu de NPCs (criar/editar/gerenciar).",
    )
    async def npc_menu(self, interaction: discord.Interaction):
        loc = resolve_locale(interaction, fallback="pt")
        guild = interaction.guild
        if guild is None:
            msg = _tr("npc.menu.guild_only", loc, "❌ This command can only be used in a server.")
            return await interaction.response.send_message(msg, ephemeral=True)

        if not mestre_utils.verificar_mestre(guild.name, interaction.user.id):
            msg = _tr("npc.menu.only_master", loc, "❌ Only GMs can open the NPC menu.")
            return await interaction.response.send_message(msg, ephemeral=True)

        title = _tr("npc.menu.title", loc, "📜 Select an NPC or create a new one:")
        view = NPCSelectView(guild_id=guild.id, mestre_id=interaction.user.id)
        await interaction.response.send_message(content=title, view=view, ephemeral=True)

    @localized_command_en_base(
        name_en="view_npc",
        desc_en="Show an NPC sheet.",
        pt_name="ver_npc",
        pt_desc="Exibe a ficha de um NPC.",
    )
    @app_commands.describe(nome="NPC name / Nome do NPC")
    @app_commands.autocomplete(nome=_autocomplete_npc_names)
    async def ver_npc(self, interaction: discord.Interaction, nome: str):
        loc = resolve_locale(interaction, fallback="pt")
        guild = interaction.guild
        if guild is None:
            msg = _tr("npc.view.guild_only", loc, "❌ This command can only be used in a server.")
            return await interaction.response.send_message(msg, ephemeral=True)

        ctx = NPCContext(guild.id, interaction.user.id, nome)
        try:
            npc_data = ctx.load()
        except FileNotFoundError:
            msg = _tr("npc.view.not_found", loc, "❌ NPC **{name}** was not found.", name=nome)
            return await interaction.response.send_message(msg, ephemeral=True)

        if mestre_utils.verificar_mestre(guild.name, interaction.user.id):
            view = GMNPCSheetView(npc_context=ctx)
            embed = await view.create_embed(interaction)
            header = _tr("npc.view.master_header", loc, "👁️ GM View: **{name}** sheet", name=nome)
            return await interaction.response.send_message(content=header, embed=embed, view=view, ephemeral=True)

        if not npc_data.get("visivel_para_players"):
            msg = _tr("npc.view.hidden", loc, "🔒 This NPC is hidden from players.")
            return await interaction.response.send_message(msg, ephemeral=True)

        embed = create_npc_summary_embed(npc_data)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @localized_command_en_base(
        name_en="roll_npc",
        desc_en="Open the rolling hub for an NPC.",
        pt_name="rolar_npc",
        pt_desc="Abrir o hub de rolagens para um NPC.",
    )
    @app_commands.describe(nome="NPC name / Nome do NPC")
    @app_commands.autocomplete(nome=_autocomplete_npc_names)
    async def rolar_npc(self, interaction: discord.Interaction, nome: str):
        loc = resolve_locale(interaction, fallback="pt")
        guild = interaction.guild
        if guild is None:
            msg = _tr("npc.roll.guild_only", loc, "❌ This command can only be used in a server.")
            return await interaction.response.send_message(msg, ephemeral=True)

        if not mestre_utils.verificar_mestre(guild.name, interaction.user.id):
            msg = _tr("npc.roll.only_master", loc, "❌ Only GMs can roll for NPCs.")
            return await interaction.response.send_message(msg, ephemeral=True)

        ctx = NPCContext(guild.id, interaction.user.id, nome)
        try:
            ctx.load()
        except FileNotFoundError:
            msg = _tr("npc.roll.not_found", loc, "❌ NPC **{name}** was not found.", name=nome)
            return await interaction.response.send_message(msg, ephemeral=True)

        view = NPCDiceHubView(npc_context=ctx)
        header = _tr("npc.roll.header", loc, "🎲 Rolls for **{name}**:", name=nome)
        await interaction.response.send_message(content=header, view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(NPCCog(bot))