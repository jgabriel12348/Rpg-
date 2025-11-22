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

import re
import discord
from models.npc_modals.npc_basic_modal import NPCModalBase
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCAddTestModifierModal(NPCModalBase):
  def __init__(self, npc_context):
    self._ = resolve_locale(getattr(npc_context, "interaction", None))

    super().__init__(
      npc_context,
      title=t("npc.tests.modal.title", self._).format(name=npc_context.npc_name)
    )

    # Inputs
    self.nome_teste = discord.ui.TextInput(
      label=t("npc.tests.fields.name.label", self._),
      placeholder=t("npc.tests.fields.name.ph", self._),
      required=True,
      max_length=120
    )
    self.modificador = discord.ui.TextInput(
      label=t("npc.tests.fields.mod.label", self._),
      placeholder=t("npc.tests.fields.mod.ph", self._),
      required=True,
      max_length=40
    )
    self.condicao = discord.ui.TextInput(
      label=t("npc.tests.fields.cond.label", self._),
      style=discord.TextStyle.paragraph,
      placeholder=t("npc.tests.fields.cond.ph", self._),
      required=False,
      max_length=500
    )

    self.add_item(self.nome_teste)
    self.add_item(self.modificador)
    self.add_item(self.condicao)
  @staticmethod
  def _normalize_modifier(text: str) -> str:
    s = text.strip()
    if re.fullmatch(r"[+-]?\d+", s):
      val = int(s)
      return f"{val:+d}"
    return s

  async def on_submit(self, interaction: discord.Interaction):
    _ = self._
    nome = (self.nome_teste.value or "").strip()
    mod  = (self.modificador.value or "").strip()
    cond = (self.condicao.value or "").strip()

    if not nome:
      return await interaction.response.send_message(
        t("npc.tests.errors.name_required", _),
        ephemeral=True
      )
    if not mod:
      return await interaction.response.send_message(
        t("npc.tests.errors.mod_required", _),
        ephemeral=True
      )

    mod_norm = self._normalize_modifier(mod)

    mods = self.npc_data.setdefault("testes_modificadores", [])

    nome_key = nome.casefold()
    cond_key = cond.casefold()
    updated = False
    for m in mods:
      if m.get("nome_teste", "").casefold() == nome_key and (m.get("condicao", "").casefold() == cond_key):
        m["modificador"] = mod_norm
        updated = True
        break

    if not updated:
      mods.append({
        "nome_teste": nome,
        "modificador": mod_norm,
        "condicao": cond
      })

    self.save()

    cond_txt = f" {t('npc.tests.confirm.cond_prefix', _)} {cond}" if cond else ""
    if updated:
      msg = t("npc.tests.confirm.updated", _).format(
        name=nome,
        mod=mod_norm,
        npc=self.npc_context.npc_name,
        cond=cond
      )
    else:
      msg = t("npc.tests.confirm.added", _).format(
        name=nome,
        mod=mod_norm,
        npc=self.npc_context.npc_name,
        cond=cond
      )

    await interaction.response.send_message(msg, ephemeral=True)
