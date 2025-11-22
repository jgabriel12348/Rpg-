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

_CONDITION_SPECS = [
  ("burning",      "🔥"),
  ("frozen",       "🥶"),
  ("bleeding",     "🩸"),
  ("poisoned",     "🤢"),
  ("stunned",      "😵"),
  ("confused",     "🤯"),
  ("frightened",   "😱"),
  ("charmed",      "✨"),
  ("asleep",       "💤"),
  ("paralyzed",    "🧎‍♂️"),
  ("blinded",      "👁️"),
  ("deafened",     "🙉"),
  ("silenced",     "🔇"),
  ("prone",        "🏃‍♂️"),
  ("grappled",     "⛓️"),
  ("restrained",   "🕸️"),
  ("exhausted",    "💪"),
  ("petrified",    "💎"),
  ("invisible",    "👻"),
  ("unconscious",  "💀"),
]

def _build_condition_options(locale: str):
  options = []
  for key, emoji in _CONDITION_SPECS:
    label = t(f"npc.conditions.{key}.label", locale)
    desc  = t(f"npc.conditions.{key}.desc",  locale)
    options.append(discord.SelectOption(label=label, emoji=emoji, description=desc))
  return options


class NPCConditionSelect(discord.ui.Select):
  def __init__(self, npc_context: NPCContext):
    self.npc_context = npc_context
    self.locale = (
      getattr(npc_context, "user_pref", None)
      or getattr(npc_context, "guild_pref", None)
      or getattr(npc_context, "locale", None)
      or "pt"
    )
    options = _build_condition_options(self.locale)
    npc_data = self.npc_context.load()
    active_conditions = npc_data.get("condicoes_ativas", [])
    for option in options:
      if option.label in active_conditions:
        option.default = True

    super().__init__(
      placeholder=t("npc.conditions.placeholder", self.locale, name=self.npc_context.npc_name),
      min_values=0,
      max_values=len(options),
      options=options
    )

  async def callback(self, interaction: discord.Interaction):
    try:
      loc = resolve_locale(interaction) or self.locale
    except Exception:
      loc = self.locale
    npc_data = self.npc_context.load()
    npc_data["condicoes_ativas"] = self.values
    self.npc_context.save(npc_data)

    if not self.values:
      await interaction.response.send_message(
        t("npc.conditions.cleared", loc, name=self.npc_context.npc_name),
        ephemeral=True
      )
    else:
      conditions_text = ", ".join([f"**{v}**" for v in self.values])
      await interaction.response.send_message(
        t("npc.conditions.updated", loc, name=self.npc_context.npc_name, list=conditions_text),
        ephemeral=True
      )


class NPCConditionView(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=600)
    self.add_item(NPCConditionSelect(npc_context))
