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

class NPCCombatInfoModal(NPCModalBase):
  def __init__(self, npc_context, interaction: discord.Interaction):
    self.locale = resolve_locale(interaction)
    super().__init__(npc_context, title=t("npc.combat.title", self.locale, name=npc_context.npc_name))

    combat_info = self.npc_data.get("informacoes_combate", {}) or {}
    default_vida = f"{combat_info.get('vida_atual', '')} / {combat_info.get('vida_maxima', '')}".strip(" / ")
    default_magia = f"{combat_info.get('magia_atual', '')} / {combat_info.get('magia_maxima', '')}".strip(" / ")

    self.vida = discord.ui.TextInput(
      label=t("npc.combat.fields.hp.label", self.locale),
      placeholder=t("npc.combat.fields.hp.placeholder", self.locale),
      default=default_vida, required=False, max_length=21
    )
    self.magia = discord.ui.TextInput(
      label=t("npc.combat.fields.mp.label", self.locale),
      placeholder=t("npc.combat.fields.mp.placeholder", self.locale),
      default=default_magia, required=False, max_length=21
    )
    self.defesa = discord.ui.TextInput(
      label=t("npc.combat.fields.defense.label", self.locale),
      placeholder=t("npc.combat.fields.defense.placeholder", self.locale),
      default=combat_info.get("defesa") or "", required=False, max_length=100
    )
    self.resistencia_magica = discord.ui.TextInput(
      label=t("npc.combat.fields.magic_res.label", self.locale),
      placeholder=t("npc.combat.fields.magic_res.placeholder", self.locale),
      default=combat_info.get("resistencia_magica") or "", required=False, max_length=100
    )
    self.iniciativa = discord.ui.TextInput(
      label=t("npc.combat.fields.initiative.label", self.locale),
      placeholder=t("npc.combat.fields.initiative.placeholder", self.locale),
      default=combat_info.get("iniciativa") or "", required=False, max_length=50
    )

    self.add_item(self.vida)
    self.add_item(self.magia)
    self.add_item(self.defesa)
    self.add_item(self.resistencia_magica)
    self.add_item(self.iniciativa)

  async def on_submit(self, interaction: discord.Interaction):
    try:
      vida_value = self.vida.value or "0/0"
      magia_value = self.magia.value or "0/0"

      vida_parts = vida_value.replace(" ", "").split('/')
      if len(vida_parts) != 2:
        raise ValueError(t("npc.combat.errors.hp_format", self.locale))
      vida_atual, vida_maxima = int(vida_parts[0]), int(vida_parts[1])
      if vida_atual > vida_maxima:
        raise ValueError(t("npc.combat.errors.hp_gt_max", self.locale))

      magia_parts = magia_value.replace(" ", "").split('/')
      if len(magia_parts) != 2:
        raise ValueError(t("npc.combat.errors.mp_format", self.locale))
      magia_atual, magia_maxima = int(magia_parts[0]), int(magia_parts[1])
      if magia_atual > magia_maxima:
        raise ValueError(t("npc.combat.errors.mp_gt_max", self.locale))

    except (ValueError, TypeError) as e:
      await interaction.response.send_message(
        t("npc.combat.errors.generic", self.locale, msg=str(e)),
        ephemeral=True
      )
      return

    self.npc_data.setdefault("informacoes_combate", {}).update({
      "vida_atual": vida_atual, "vida_maxima": vida_maxima,
      "magia_atual": magia_atual, "magia_maxima": magia_maxima,
      "defesa": self.defesa.value,
      "resistencia_magica": self.resistencia_magica.value,
      "iniciativa": self.iniciativa.value,
    })
    self.save()

    embed = discord.Embed(
      title=t("npc.combat.embed.title", self.locale, name=self.npc_context.npc_name),
      color=discord.Color.red()
    )
    embed.set_footer(text=t("npc.combat.embed.footer", self.locale, user=interaction.user.display_name))
    embed.add_field(name=t("npc.combat.embed.hp", self.locale), value=f"`{vida_atual} / {vida_maxima}`", inline=True)
    embed.add_field(name=t("npc.combat.embed.mp", self.locale), value=f"`{magia_atual} / {magia_maxima}`", inline=True)
    embed.add_field(
      name=t("npc.combat.embed.defense", self.locale),
      value=self.defesa.value or t("common.na", self.locale),
      inline=False
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)
