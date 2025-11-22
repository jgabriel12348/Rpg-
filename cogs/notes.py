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
from discord.utils import get as dget
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
    try:
        txt = t_raw(key, locale, **kwargs)
    except Exception:
        return fallback.format(**kwargs) if kwargs else fallback
    if txt == key:
        try:
            return fallback.format(**kwargs) if kwargs else fallback
        except Exception:
            return fallback
    return txt

def localized_command(name_pt, desc_pt, name_en, desc_en):
    def decorator(func):
        cmd = app_commands.command(name=name_pt, description=desc_pt)(func)
        cmd.name_localizations = {"en-US": name_en, "en-GB": name_en}
        cmd.description_localizations = {"en-US": desc_en, "en-GB": desc_en}
        return cmd
    return decorator


class NotesChannelCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @localized_command(
        name_pt="notas", desc_pt="Cria ou encontra seu canal de anotações pessoal.",
        name_en="notes", desc_en="Create or locate your personal notes channel."
    )
    async def notas(self, interaction: discord.Interaction):
        loc = resolve_locale(interaction, fallback="pt")

        guild: discord.Guild | None = interaction.guild
        if guild is None:
            msg = _tr("notes.cmd.guild_only", loc, "❌ Este comando só pode ser usado em um servidor.")
            return await interaction.response.send_message(msg, ephemeral=True)

        member: discord.Member = interaction.user

        mestre_role = dget(guild.roles, name=_tr("admin.role.name", loc, "Mestre")) \
                      or dget(guild.roles, name="Mestre") \
                      or dget(guild.roles, name="GM")

        category_name = _tr("notes.category", loc, "Anotações dos Jogadores")
        chan_prefix = _tr("notes.channel.prefix", loc, "📝-notas-")
        channel_name = f"{chan_prefix}{member.name.lower()}"

        await interaction.response.defer(ephemeral=True)

        category = dget(guild.categories, name=category_name)
        if category is None:
            try:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                }
                if mestre_role:
                    overwrites[mestre_role] = discord.PermissionOverwrite(read_messages=True)

                category = await guild.create_category(category_name, overwrites=overwrites)
            except discord.Forbidden:
                err = _tr("notes.err.create_category.perm", loc,
                          "❌ O bot não tem permissão para criar categorias. Verifique as permissões do cargo dele.")
                return await interaction.followup.send(err)
            except discord.HTTPException:
                err = _tr("notes.err.create_category.http", loc,
                          "❌ Ocorreu um erro ao criar a categoria de anotações.")
                return await interaction.followup.send(err)

        channel = dget(guild.text_channels, name=channel_name, category=category)
        if channel is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                self.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
            if mestre_role:
                overwrites[mestre_role] = discord.PermissionOverwrite(read_messages=True)

            topic = _tr(
                "notes.topic",
                loc,
                "Canal de anotações pessoal para {display}",
                display=member.display_name
            )

            try:
                new_channel = await guild.create_text_channel(
                    channel_name,
                    category=category,
                    overwrites=overwrites,
                    topic=topic
                )

                welcome = _tr(
                    "notes.welcome",
                    loc,
                    "### 📔 Bem-vindo ao seu Diário de Campanha, {mention}!\n\n"
                    "Este é o seu canal de anotações pessoal. Use-o para registrar informações da campanha, "
                    "desenvolver a história do seu personagem, guardar segredos e o que mais você quiser. "
                    "Apenas você e os mestres podem ver este canal.",
                    mention=member.mention
                )
                await new_channel.send(welcome)

                ok = _tr(
                    "notes.created.ok",
                    loc,
                    "✅ Seu canal de anotações pessoal foi criado! Confira: {chan}",
                    chan=new_channel.mention
                )
                await interaction.followup.send(ok)
                return
            except discord.Forbidden:
                err = _tr(
                    "notes.err.create_channel.perm",
                    loc,
                    "❌ O bot não tem permissão para criar canais de texto. Verifique as permissões do cargo dele."
                )
                return await interaction.followup.send(err)
            except discord.HTTPException:
                err = _tr(
                    "notes.err.create_channel.http",
                    loc,
                    "❌ Ocorreu um erro ao criar o seu canal de anotações."
                )
                return await interaction.followup.send(err)
        else:
            info = _tr(
                "notes.exists",
                loc,
                "ℹ️ Você já tem um canal de anotações. Aqui está ele: {chan}",
                chan=channel.mention
            )
            await interaction.followup.send(info)


async def setup(bot: commands.Bot):
    await bot.add_cog(NotesChannelCog(bot))
