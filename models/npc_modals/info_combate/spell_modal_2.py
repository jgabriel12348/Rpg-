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

class NPCSpellDetailsModal(discord.ui.Modal):
    def __init__(self, npc_context, interaction: discord.Interaction, draft: dict | None = None):
        self.locale = resolve_locale(interaction)
        _ = self.locale

        super().__init__(title=t("npc.spell.details.title", _))

        self.npc_context = npc_context
        self.draft = draft or {}

        self.componentes = discord.ui.TextInput(
            label=t("npc.spell.details.fields.components.label", _),
            placeholder=t("npc.spell.details.fields.components.placeholder", _),
            default=self.draft.get("componentes", ""),
            max_length=100
        )
        self.alcance = discord.ui.TextInput(
            label=t("npc.spell.details.fields.range.label", _),
            placeholder=t("npc.spell.details.fields.range.placeholder", _),
            default=self.draft.get("alcance", ""),
            max_length=100
        )
        self.efeito = discord.ui.TextInput(
            label=t("npc.spell.details.fields.effect.label", _),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.spell.details.fields.effect.placeholder", _),
            default=self.draft.get("efeito", ""),
            max_length=1500
        )
        self.formula_acerto = discord.ui.TextInput(
            label=t("npc.spell.details.fields.hit_formula.label", _),
            placeholder=t("npc.spell.details.fields.hit_formula.placeholder", _),
            default=self.draft.get("formula_acerto", ""),
            max_length=120,
            required=False
        )
        self.formula_dano_cura = discord.ui.TextInput(
            label=t("npc.spell.details.fields.damage_formula.label", _),
            placeholder=t("npc.spell.details.fields.damage_formula.placeholder", _),
            default=self.draft.get("formula_dano_cura", ""),
            max_length=120,
            required=False
        )

        self.add_item(self.componentes)
        self.add_item(self.alcance)
        self.add_item(self.efeito)
        self.add_item(self.formula_acerto)
        self.add_item(self.formula_dano_cura)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
