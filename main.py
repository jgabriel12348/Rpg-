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

import os
import asyncio
import logging
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils.checks import is_app_owner

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("rpg-bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

EXTENSIONS = [
    "cogs.npc",
    "cogs.admin",
    "cogs.notes",
    "cogs.core",
    "cogs.player"
]

GUILD_ID_FOR_FAST_SYNC = None

class RPGbot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            application_id=int(os.getenv("DISCORD_APP_ID", "0")) or None
        )

    async def setup_hook(self):
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                log.info(f"[cogs] loaded: {ext}")
            except Exception as e:
                log.exception(f"[cogs] failed to load {ext}: {e}")

        try:
            if GUILD_ID_FOR_FAST_SYNC:
                guild_obj = discord.Object(id=int(GUILD_ID_FOR_FAST_SYNC))
                self.tree.copy_global_to(guild=guild_obj)
                synced = await self.tree.sync(guild=guild_obj)
                log.info(f"[sync] guild-only ({guild_obj.id}) ok: {len(synced)} commands")
            else:
                synced = await self.tree.sync()
                log.info(f"[sync] global ok: {len(synced)} commands")
        except Exception:
            log.exception("[sync] error on app command sync")

    async def on_ready(self):
        log.info(f"Logged in as {self.user} (id={self.user.id})")
        await self.change_presence(
            activity=discord.Game(name="/npc_menu • /notas")
        )

bot = RPGbot()

@bot.tree.command(name="sync_commands", description="Sincroniza os comandos do bot (apenas dono).")
@is_app_owner()
@app_commands.describe(
    scope="Opcional: 'global' ou um ID de guild para sync rápido"
)
async def sync_commands(interaction: discord.Interaction, scope: str | None = None):
    await interaction.response.defer(ephemeral=True)
    try:
        if scope and scope.isdigit():
            gid = int(scope)
            guild_obj = discord.Object(id=gid)
            bot.tree.copy_global_to(guild=guild_obj)
            synced = await bot.tree.sync(guild=guild_obj)
            return await interaction.followup.send(f"✅ Sync de guild `{gid}` ok: {len(synced)} comandos.")
        elif scope == "global":
            synced = await bot.tree.sync()
            return await interaction.followup.send(f"✅ Sync global ok: {len(synced)} comandos.")
        else:
            if GUILD_ID_FOR_FAST_SYNC:
                guild_obj = discord.Object(id=int(GUILD_ID_FOR_FAST_SYNC))
                bot.tree.copy_global_to(guild=guild_obj)
                synced = await bot.tree.sync(guild=guild_obj)
                return await interaction.followup.send(f"✅ Sync de guild `{guild_obj.id}` ok: {len(synced)} comandos.")
            synced = await bot.tree.sync()
            return await interaction.followup.send(f"✅ Sync global ok: {len(synced)} comandos.")
    except Exception as e:
        logging.exception("sync error")
        await interaction.followup.send(f"❌ Erro no sync: {e}", ephemeral=True)

def main():
    token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
    if not token:
        raise RuntimeError("Defina DISCORD_TOKEN (ou TOKEN) no .env com o token do seu bot.")
    bot.run(token)

if __name__ == "__main__":
    main()
