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

class NPCMovementInfoModal(NPCModalBase):
  def __init__(self, npc_context, interaction: discord.Interaction):
    self.locale = resolve_locale(interaction)

    super().__init__(
      npc_context,
      title=t("npc.movement.title", self.locale, name=npc_context.npc_name)
    )

    movement_info = self.npc_data.get("informacoes_deslocamento", {}) or {}

    self.velocidade = discord.ui.TextInput(
      label=t("npc.movement.fields.speed.label", self.locale),
      placeholder=t("npc.movement.fields.speed.placeholder", self.locale),
      default=movement_info.get("velocidade") or "",
      required=False,
      max_length=100
    )
    self.regeneracao = discord.ui.TextInput(
      label=t("npc.movement.fields.regen.label", self.locale),
      placeholder=t("npc.movement.fields.regen.placeholder", self.locale),
      default=movement_info.get("regeneracao") or "",
      required=False,
      max_length=100
    )
    self.resistencias = discord.ui.TextInput(
      label=t("npc.movement.fields.resist.label", self.locale),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.movement.fields.resist.placeholder", self.locale),
      default=movement_info.get("resistencias") or "",
      required=False
    )
    self.fraquezas = discord.ui.TextInput(
      label=t("npc.movement.fields.weak.label", self.locale),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.movement.fields.weak.placeholder", self.locale),
      default=movement_info.get("fraquezas") or "",
      required=False
    )
    self.imunidades = discord.ui.TextInput(
      label=t("npc.movement.fields.immune.label", self.locale),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.movement.fields.immune.placeholder", self.locale),
      default=movement_info.get("imunidades") or "",
      required=False
    )

    self.add_item(self.velocidade)
    self.add_item(self.regeneracao)
    self.add_item(self.resistencias)
    self.add_item(self.fraquezas)
    self.add_item(self.imunidades)

  async def on_submit(self, interaction: discord.Interaction):
    self.npc_data.setdefault("informacoes_deslocamento", {}).update({
      "velocidade": self.velocidade.value,
      "regeneracao": self.regeneracao.value,
      "resistencias": self.resistencias.value,
      "fraquezas": self.fraquezas.value,
      "imunidades": self.imunidades.value,
    })
    self.save()

    embed = discord.Embed(
      title=t("npc.movement.embed.title", self.locale, name=self.npc_context.npc_name),
      description=t("npc.movement.embed.desc", self.locale),
      color=discord.Color.green()
    )
    embed.set_footer(text=t("npc.movement.embed.footer", self.locale, user=interaction.user.display_name))

    embed.add_field(
      name=t("npc.movement.embed.speed", self.locale),
      value=self.velocidade.value or t("common.na", self.locale),
      inline=False
    )
    embed.add_field(
      name=t("npc.movement.embed.regen", self.locale),
      value=self.regeneracao.value or t("common.na", self.locale),
      inline=False
    )
    embed.add_field(
      name=t("npc.movement.embed.resist", self.locale),
      value=self.resistencias.value or t("common.none", self.locale),
      inline=False
    )
    embed.add_field(
      name=t("npc.movement.embed.weak", self.locale),
      value=self.fraquezas.value or t("common.none", self.locale),
      inline=False
    )
    embed.add_field(
      name=t("npc.movement.embed.immune", self.locale),
      value=self.imunidades.value or t("common.none", self.locale),
      inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)
