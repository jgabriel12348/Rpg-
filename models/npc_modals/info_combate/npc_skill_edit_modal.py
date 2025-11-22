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

class NPCSkillEditModal(NPCModalBase):
  def __init__(self, npc_context, interaction: discord.Interaction, skill_name: str | None = None):
    self.locale = resolve_locale(interaction)

    super().__init__(
      npc_context,
      title=t("npc.skills.edit.title", self.locale, name=npc_context.npc_name)
    )

    self.skill_name_to_edit = skill_name
    pericia_data = (self.npc_data.get("pericias", {}) or {}).get(skill_name, {}) or {}

    self.nome = discord.ui.TextInput(
      label=t("npc.skills.edit.fields.name.label", self.locale),
      placeholder=t("npc.skills.edit.fields.name.placeholder", self.locale),
      default=skill_name or ""
    )
    self.bonus = discord.ui.TextInput(
      label=t("npc.skills.edit.fields.bonus.label", self.locale),
      placeholder=t("npc.skills.edit.fields.bonus.placeholder", self.locale),
      default=str(pericia_data.get("bonus", 0))
    )

    self.add_item(self.nome)
    self.add_item(self.bonus)

  async def on_submit(self, interaction: discord.Interaction):
    from view.ficha_npc.npc_skill_management_view import NPCAttributeLinkView
    try:
      bonus_val = int(self.bonus.value or 0)
      nome_val = (self.nome.value or "").strip()
      if not nome_val:
        raise ValueError(t("npc.skills.edit.errors.empty_name", self.locale))

      pericias = self.npc_data.setdefault("pericias", {})
      if self.skill_name_to_edit and self.skill_name_to_edit != nome_val:
        pericias.pop(self.skill_name_to_edit, None)
        self.save()

      view = NPCAttributeLinkView(
        npc_context=self.npc_context,
        skill_name=nome_val,
        skill_bonus=bonus_val
      )

      await interaction.response.edit_message(
        content=t(
          "npc.skills.edit.next_step",
          self.locale,
          skill=nome_val,
          bonus=bonus_val,
          name=self.npc_context.npc_name
        ),
        view=view,
        embed=None
      )

    except ValueError as e:
      await interaction.response.send_message(
        t("npc.skills.edit.errors.invalid_bonus", self.locale, error=str(e)),
        ephemeral=True
      )
