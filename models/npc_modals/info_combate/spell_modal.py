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
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCSpellPrimaryModal(discord.ui.Modal):
    def __init__(self, npc_context, interaction: discord.Interaction, draft: dict | None = None):
        self.locale = resolve_locale(interaction)
        _ = self.locale

        super().__init__(title=t("npc.spell.primary.title", _))
        self.npc_context = npc_context
        self.draft = draft or {}

        self.nome_magia = discord.ui.TextInput(
            label=t("npc.spell.primary.fields.name.label", _),
            placeholder=t("npc.spell.primary.fields.name.placeholder", _),
            default=self.draft.get("nome", ""),
            max_length=80
        )
        self.nivel = discord.ui.TextInput(
            label=t("npc.spell.primary.fields.level.label", _),
            placeholder=t("npc.spell.primary.fields.level.placeholder", _),
            default=self.draft.get("nivel", self.draft.get("custo", "")),
            max_length=40
        )
        self.escola = discord.ui.TextInput(
            label=t("npc.spell.primary.fields.school.label", _),
            placeholder=t("npc.spell.primary.fields.school.placeholder", _),
            default=self.draft.get("escola", ""),
            max_length=40,
            required=False
        )
        self.tempo_conjuracao = discord.ui.TextInput(
            label=t("npc.spell.primary.fields.cast_time.label", _),
            placeholder=t("npc.spell.primary.fields.cast_time.placeholder", _),
            default=self.draft.get("tempo_conjuracao", self.draft.get("tempo", "")),
            max_length=40
        )
        self.concentracao = discord.ui.TextInput(
            label=t("npc.spell.primary.fields.concentration.label", _),
            placeholder=t("npc.spell.primary.fields.concentration.placeholder", _),
            default=self.draft.get("concentracao", ""),
            max_length=20,
            required=False
        )

        self.add_item(self.nome_magia)
        self.add_item(self.nivel)
        self.add_item(self.escola)
        self.add_item(self.tempo_conjuracao)
        self.add_item(self.concentracao)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
