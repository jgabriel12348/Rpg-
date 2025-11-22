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
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCAttackPrimaryModal(discord.ui.Modal):
    def __init__(self, npc_context: NPCContext, interaction: discord.Interaction):
        self.npc_context = npc_context
        try:
            self.locale = resolve_locale(interaction)
        except Exception:
            self.locale = (
                getattr(npc_context, "user_pref", None)
                or getattr(npc_context, "guild_pref", None)
                or getattr(npc_context, "locale", None)
                or "pt"
            )

        super().__init__(title=t("npc.attack.primary.title", self.locale, name=npc_context.npc_name))

        self.nome_ataque = discord.ui.TextInput(
            label=t("npc.attack.name", self.locale),
            placeholder=t("npc.attack.ph.name", self.locale),
        )
        self.teste_de_acerto = discord.ui.TextInput(
            label=t("npc.attack.to_hit", self.locale),
            placeholder=t("npc.attack.ph.to_hit", self.locale),
        )
        self.dano = discord.ui.TextInput(
            label=t("npc.attack.damage", self.locale),
            placeholder=t("npc.attack.ph.damage", self.locale),
        )
        self.alcance = discord.ui.TextInput(
            label=t("npc.attack.range", self.locale),
            placeholder=t("npc.attack.ph.range", self.locale),
        )
        self.usos = discord.ui.TextInput(
            label=t("npc.attack.uses", self.locale),
            placeholder=t("npc.attack.ph.uses", self.locale),
            required=False,
        )

        self.add_item(self.nome_ataque)
        self.add_item(self.teste_de_acerto)
        self.add_item(self.dano)
        self.add_item(self.alcance)
        self.add_item(self.usos)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.stop()
