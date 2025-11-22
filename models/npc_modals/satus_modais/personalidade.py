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

class NPCPersonalityModal(NPCModalBase):
  def __init__(self, npc_context, interaction: discord.Interaction | None = None):
    inter = interaction or getattr(npc_context, "interaction", None)
    _ = resolve_locale(inter)
    self._ = _

    super().__init__(
      npc_context,
      title=t("npc.personality.title", _).format(name=npc_context.npc_name)
    )
    personality_data = self.npc_data.get("personalidade") or {}
    self.personalidade = discord.ui.TextInput(
      label=t("npc.personality.summary.label", _),
      placeholder=t("npc.personality.summary.ph", _),
      default=personality_data.get("resumo", "") or "",
      required=False,
      max_length=100
    )
    self.tracos = discord.ui.TextInput(
      label=t("npc.personality.traits.label", _),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.personality.traits.ph", _),
      default=personality_data.get("tracos_marcantes", "") or "",
      required=False,
      max_length=1500
    )

    self.add_item(self.personalidade)
    self.add_item(self.tracos)

  async def on_submit(self, interaction: discord.Interaction):
    resumo = (self.personalidade.value or "").strip()
    tracos = (self.tracos.value or "").strip()
    self.npc_data["personalidade"] = {
      "resumo": resumo,
      "tracos_marcantes": tracos
    }
    self.save()
    embed = discord.Embed(
      title=t("npc.personality.saved.title", self._).format(name=self.npc_context.npc_name),
      description=t("npc.personality.saved.desc", self._),
      color=discord.Color.purple()
    )
    embed.add_field(
      name=t("npc.personality.summary.field", self._),
      value=(resumo or "—"),
      inline=False
    )
    if tracos:
      preview = (tracos[:700] + "…") if len(tracos) > 700 else tracos
      embed.add_field(
        name=t("npc.personality.traits.field", self._),
        value=preview,
        inline=False
      )
    embed.set_footer(text=t("npc.updated_by", self._).format(user=interaction.user.display_name))

    await interaction.response.send_message(embed=embed, ephemeral=True)
