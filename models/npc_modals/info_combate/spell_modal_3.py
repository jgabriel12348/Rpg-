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

class NPCSpellExtraModal(discord.ui.Modal):
    def __init__(self, npc_context, interaction: discord.Interaction, draft: dict | None = None):
        self.locale = resolve_locale(interaction)
        _ = self.locale

        super().__init__(title=t("npc.spell.extra.title", _))

        self.npc_context = npc_context
        self.draft = draft or {}

        self.area_acao = discord.ui.TextInput(
            label=t("npc.spell.extra.fields.area.label", _),
            placeholder=t("npc.spell.extra.fields.area.placeholder", _),
            default=self.draft.get("area_acao", ""),
            max_length=100
        )
        self.duracao = discord.ui.TextInput(
            label=t("npc.spell.extra.fields.duration.label", _),
            placeholder=t("npc.spell.extra.fields.duration.placeholder", _),
            default=self.draft.get("duracao", ""),
            max_length=100
        )
        self.em_niveis_superiores = discord.ui.TextInput(
            label=t("npc.spell.extra.fields.higher_levels.label", _),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.spell.extra.fields.higher_levels.placeholder", _),
            default=self.draft.get("em_niveis_superiores", ""),
            max_length=800,
            required=False
        )
        self.classe_conjurador = discord.ui.TextInput(
            label=t("npc.spell.extra.fields.caster_class.label", _),
            placeholder=t("npc.spell.extra.fields.caster_class.placeholder", _),
            default=self.draft.get("classe_conjurador", ""),
            max_length=100,
            required=False
        )
        self.descricao = discord.ui.TextInput(
            label=t("npc.spell.extra.fields.description.label", _),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.spell.extra.fields.description.placeholder", _),
            default=self.draft.get("descricao", ""),
            max_length=1500,
            required=False
        )

        self.add_item(self.area_acao)
        self.add_item(self.duracao)
        self.add_item(self.em_niveis_superiores)
        self.add_item(self.classe_conjurador)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
