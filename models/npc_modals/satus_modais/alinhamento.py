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

class NPCAlignmentModal(NPCModalBase):
  def __init__(self, npc_context, interaction: discord.Interaction | None = None):
    inter = interaction or getattr(npc_context, "interaction", None)
    _ = resolve_locale(inter)
    self._ = _
    super().__init__(npc_context, title=t("npc.alignment.title", _).format(name=npc_context.npc_name))

    alignment_data = self.npc_data.get("alinhamento_crencas", {}) or {}

    self.alinhamento = discord.ui.TextInput(
      label=t("npc.alignment.fields.alignment.label", _),
      placeholder=t("npc.alignment.fields.alignment.ph", _),
      default=alignment_data.get("alinhamento") or "",
      required=False
    )
    self.ideais = discord.ui.TextInput(
      label=t("npc.alignment.fields.ideals.label", _),
      placeholder=t("npc.alignment.fields.ideals.ph", _),
      default=alignment_data.get("ideais") or "",
      required=False
    )
    self.defeitos = discord.ui.TextInput(
      label=t("npc.alignment.fields.flaws.label", _),
      placeholder=t("npc.alignment.fields.flaws.ph", _),
      default=alignment_data.get("defeitos") or "",
      required=False
    )
    self.vinculos = discord.ui.TextInput(
      label=t("npc.alignment.fields.bonds.label", _),
      placeholder=t("npc.alignment.fields.bonds.ph", _),
      default=alignment_data.get("vinculos") or "",
      required=False
    )

    self.add_item(self.alinhamento)
    self.add_item(self.ideais)
    self.add_item(self.defeitos)
    self.add_item(self.vinculos)

  async def on_submit(self, interaction: discord.Interaction):
    self.npc_data["alinhamento_crencas"] = {
      "alinhamento": self.alinhamento.value,
      "ideais": self.ideais.value,
      "defeitos": self.defeitos.value,
      "vinculos": self.vinculos.value
    }
    self.save()

    await interaction.response.send_message(
      t("npc.alignment.saved", self._).format(name=self.npc_context.npc_name),
      ephemeral=True
    )
