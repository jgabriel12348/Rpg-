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
from models.npc_modals.npc_basic_modal import NPCModalBase
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCLearnSkillsModal(NPCModalBase):
  def __init__(self, npc_context, interaction: discord.Interaction | None = None):
    inter = interaction or getattr(npc_context, "interaction", None)
    _ = resolve_locale(inter)
    self._ = _

    super().__init__(
      npc_context,
      title=t("npc.skills.title", _).format(name=npc_context.npc_name)
    )

    self._existing_skills = self.npc_data.get("pericias") or {}
    skills_str = ", ".join(self._existing_skills.keys())

    self.skills_input = discord.ui.TextInput(
      label=t("npc.skills.input.label", _),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.skills.input.ph", _),
      default=skills_str,
      required=False,
      max_length=2000
    )
    self.add_item(self.skills_input)

  async def on_submit(self, interaction: discord.Interaction):
    raw = (self.skills_input.value or "").strip()
    names = [s.strip() for s in raw.split(",")] if raw else []
    seen, ordered = set(), []
    for n in names:
      if n and n not in seen:
        seen.add(n)
        ordered.append(n)

    new_skills = {}
    for name in ordered:
      new_skills[name] = self._existing_skills.get(name, "N/A")

    self.npc_data["pericias"] = new_skills
    self.save()

    count = len(new_skills)
    await interaction.response.send_message(
      t("npc.skills.saved", self._).format(name=self.npc_context.npc_name, count=count),
      ephemeral=True
    )
