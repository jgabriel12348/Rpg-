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
from utils.player_utils import load_player_sheet, save_player_sheet
from utils.i18n import t
from utils.locale_resolver import resolve_locale

_CONDITIONS_SPEC = [
    ("burning", "🔥"),
    ("frozen", "🥶"),
    ("bleeding", "🩸"),
    ("poisoned", "🤢"),
    ("stunned", "😵"),
    ("confused", "🤯"),
    ("frightened", "😱"),
    ("charmed", "✨"),
    ("asleep", "💤"),
    ("paralyzed", "🧎‍♂️"),
    ("blinded", "👁️"),
    ("deafened", "🙉"),
    ("silenced", "🔇"),
    ("prone", "🏃‍♂️"),
    ("grappled", "⛓️"),
    ("restrained", "🕸️"),
    ("exhausted", "💪"),
    ("petrified", "💎"),
    ("invisible", "👻"),
    ("unconscious", "💀"),
]

def build_condition_options(locale: str) -> list[discord.SelectOption]:
    options: list[discord.SelectOption] = []
    for cond_id, emoji in _CONDITIONS_SPEC:
        label = t(f"conditions.{cond_id}.label", locale)
        desc  = t(f"conditions.{cond_id}.desc", locale)
        options.append(discord.SelectOption(label=label, value=cond_id, emoji=emoji, description=desc))
    return options

class ConditionSelect(discord.ui.Select):
    def __init__(self, character_name: str, locale: str = "pt"):
        self.character_name = character_name
        self.locale = locale

        ficha = load_player_sheet(self.character_name)
        active_conditions = ficha.get("condicoes_ativas", []) or []
        options = build_condition_options(self.locale)
        localized_label_to_id = {opt.label: opt.value for opt in options}
        def _is_active(opt: discord.SelectOption) -> bool:
            return (
                opt.value in active_conditions
                or opt.label in active_conditions
                or any(lbl in active_conditions for lbl in localized_label_to_id.keys())
            )

        for opt in options:
            if _is_active(opt):
                opt.default = True

        placeholder = t("conditions.placeholder", self.locale)

        super().__init__(
            placeholder=placeholder,
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if not getattr(self, "locale", None):
            self.locale = resolve_locale(interaction)

        ficha = load_player_sheet(self.character_name)

        ficha["condicoes_ativas"] = list(self.values)
        save_player_sheet(self.character_name, ficha)

        if not self.values:
            await interaction.response.send_message(
                t("conditions.cleared", self.locale),
                ephemeral=True
            )
        else:
            names = [t(f"conditions.{vid}.label", self.locale) for vid in self.values]
            conditions_text = ", ".join(f"**{n}**" for n in names)
            await interaction.response.send_message(
                t("conditions.updated", self.locale, conditions=conditions_text),
                ephemeral=True
            )

class ConditionView(discord.ui.View):
    def __init__(self, user: discord.User, locale: str | None = None):
        super().__init__(timeout=600)
        character_name = f"{user.id}_{user.name.lower()}"
        self.add_item(ConditionSelect(character_name, locale=locale or "pt"))
