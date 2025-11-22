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
from utils import player_utils, mestre_utils
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale
from view.ficha_player.ficha_player_menu import PlayerMainMenuView
from view.ficha_player.personal_sheet_view import PersonalSheetView
from utils.embed_utils import create_player_summary_embed
from models.shared_models.add_pet_modal import AddPetModal
from view.pet_view.npc_pet_selector_view import NPCPetSelectorView

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
    try:
        text = t_raw(key, locale, **kwargs)
    except Exception:
        return fallback.format(**kwargs) if kwargs else fallback
    if text == key:
        return fallback.format(**kwargs) if kwargs else fallback
    return text

def localized_command(name_pt, desc_pt, name_en, desc_en):
    def decorator(func):
        cmd = app_commands.command(name=name_pt, description=desc_pt)(func)
        cmd.name_localizations = {"en-US": name_en, "en-GB": name_en}
        cmd.description_localizations = {"en-US": desc_en, "en-GB": desc_en}
        return cmd
    return decorator

class PlayerCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @localized_command(
        name_pt="player_menu", desc_pt="Abrir o menu do player",
        name_en="player_menu", desc_en="Open the player menu"
    )
    async def player_menu(self, interaction: discord.Interaction):
        loc = resolve_locale(interaction, fallback="pt")
        title = _tr("player.menu.main.title", loc, "🎮 Menu Principal do Player")
        await interaction.response.send_message(
            content=title,
            view=PlayerMainMenuView(user=interaction.user),
            ephemeral=True
        )

    @localized_command(
        name_pt="minha_ficha", desc_pt="Exibe sua ficha de personagem interativa.",
        name_en="my_sheet", desc_en="Show your interactive character sheet."
    )
    async def minha_ficha(self, interaction: discord.Interaction):
        loc = resolve_locale(interaction, fallback="pt")
        character_name = f"{interaction.user.id}_{interaction.user.name.lower()}"
        if not player_utils.player_sheet_exists(character_name):
            msg = _tr("player.sheet.missing", loc, "❌ Você ainda não tem uma ficha! Use `/player_menu` para começar.")
            return await interaction.response.send_message(msg, ephemeral=True)
        view = PersonalSheetView(user=interaction.user)
        initial = await view.create_embed()
        await interaction.response.send_message(embed=initial, view=view, ephemeral=True)

    @localized_command(
        name_pt="ver_player", desc_pt="Exibe a ficha de um jogador.",
        name_en="view_player", desc_en="Show a player's sheet."
    )
    @app_commands.describe(jogador="Jogador alvo / Target player")
    async def ver_player(self, interaction: discord.Interaction, jogador: discord.Member):
        loc = resolve_locale(interaction, fallback="pt")
        character_name = f"{jogador.id}_{jogador.name.lower()}"
        if not player_utils.player_sheet_exists(character_name):
            msg = _tr("player.sheet.other_missing", loc, "❌ O jogador **{name}** ainda não possui uma ficha.",
                      name=jogador.display_name)
            return await interaction.response.send_message(msg, ephemeral=True)

        if mestre_utils.verificar_mestre(interaction.guild.name, interaction.user.id):
            view = PersonalSheetView(user=jogador)
            embed = await view.create_embed()
            header = _tr("player.sheet.master_view", loc, "👁️ Visão de Mestre: Ficha completa de **{name}**",
                         name=jogador.display_name)
            await interaction.response.send_message(header, embed=embed, view=view, ephemeral=True)
        else:
            ps = player_utils.load_player_sheet(character_name)
            embed = create_player_summary_embed(ps, jogador)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @localized_command(
        name_pt="registrar_pet", desc_pt="Registra um novo pet para seu personagem ou para um NPC.",
        name_en="register_pet", desc_en="Register a new pet for your character or an NPC."
    )
    async def registrar_pet(self, interaction: discord.Interaction):
        loc = resolve_locale(interaction, fallback="pt")
        guild_name = interaction.guild.name
        user_id = interaction.user.id

        if mestre_utils.verificar_mestre(guild_name, user_id):
            view = NPCPetSelectorView(interaction.guild_id, user_id)
            msg = _tr("pet.master.prompt", loc, "Você é um mestre. Selecione um NPC para registrar um pet para ele:")
            await interaction.response.send_message(msg, view=view, ephemeral=True)
            return

        modal = AddPetModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.pet_data:
            character_name = f"{user_id}_{interaction.user.name.lower()}"
            player_sheet = player_utils.load_player_sheet(character_name)
            pets_list = player_sheet.setdefault("pets", [])
            pets_list.append(modal.pet_data)
            player_utils.save_player_sheet(character_name, player_sheet)
            msg = _tr("pet.player.saved", loc, "🐾 Pet **{pet}** foi registrado para seu personagem!",
                      pet=modal.pet_data['nome'])
            await interaction.followup.send(msg, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PlayerCog(bot))
