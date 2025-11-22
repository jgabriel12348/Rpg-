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

class NPCAllianceModal(NPCModalBase):
  def __init__(self, npc_context, interaction: discord.Interaction | None = None):
    inter = interaction or getattr(npc_context, "interaction", None)
    _ = resolve_locale(inter)
    self._ = _

    super().__init__(
      npc_context,
      title=t("npc.alliances.title", _).format(name=npc_context.npc_name)
    )

    alliance_data = self.npc_data.get("aliancas", {}) or {}

    self.faccao = discord.ui.TextInput(
      label=t("npc.alliances.fields.faction.label", _),
      placeholder=t("npc.alliances.fields.faction.ph", _),
      default=alliance_data.get("faccao") or "",
      required=False
    )
    self.status = discord.ui.TextInput(
      label=t("npc.alliances.fields.status.label", _),
      placeholder=t("npc.alliances.fields.status.ph", _),
      default=alliance_data.get("status") or "",
      required=False
    )
    self.contatos = discord.ui.TextInput(
      label=t("npc.alliances.fields.contacts.label", _),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.alliances.fields.contacts.ph", _),
      default=alliance_data.get("contatos") or "",
      required=False
    )
    self.inimigos = discord.ui.TextInput(
      label=t("npc.alliances.fields.enemies.label", _),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.alliances.fields.enemies.ph", _),
      default=alliance_data.get("inimigos") or "",
      required=False
    )

    self.add_item(self.faccao)
    self.add_item(self.status)
    self.add_item(self.contatos)
    self.add_item(self.inimigos)

  async def on_submit(self, interaction: discord.Interaction):
    self.npc_data["aliancas"] = {
      "faccao": self.faccao.value,
      "status": self.status.value,
      "contatos": self.contatos.value,
      "inimigos": self.inimigos.value
    }
    self.save()

    await interaction.response.send_message(
      t("npc.alliances.saved", self._).format(name=self.npc_context.npc_name),
      ephemeral=True
    )
