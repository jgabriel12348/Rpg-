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
from models.npc_modals.teste_modifier import NPCAddTestModifierModal
from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCTestsDashboardView(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=None)
    self.npc_context = npc_context
    self._ = (
      getattr(npc_context, "user_pref", None)
      or getattr(npc_context, "guild_pref", None)
      or getattr(npc_context, "locale", None)
      or resolve_locale(getattr(npc_context, "interaction", None))
      or "pt"
    )

    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "npc:tests:add":
          item.label = t("npc.tests.btn.add", self._)
        elif item.custom_id == "npc:tests:back":
          item.label = t("common.back", self._)

  def create_embed(self) -> discord.Embed:
    _ = self._
    npc_data = self.npc_context.load()
    modificadores = npc_data.get("testes_modificadores", []) or []

    embed = discord.Embed(
      title=t("npc.tests.title", _).format(name=self.npc_context.npc_name),
      color=discord.Color.dark_teal()
    )

    if not modificadores:
      embed.description = t("npc.tests.empty", _)
      return embed

    lines = []
    for mod in modificadores:
      nome = mod.get("nome_teste", t("npc.tests.unknown", _))
      bonus = mod.get("modificador", "0")
      cond = mod.get("condicao")
      cond_txt = f" *({cond})*" if cond else ""
      lines.append(f"• **{nome}**: `{bonus}`{cond_txt}")

    description = "\n".join(lines)
    if len(description) > 3900:
      description = description[:3900].rsplit("\n", 1)[0] + "\n…"
    embed.description = description
    return embed

  @discord.ui.button(
    label="➕ Adicionar Modificador",
    style=discord.ButtonStyle.success,
    custom_id="npc:tests:add"
  )
  async def add_modifier(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(
      interaction,
      user_pref=getattr(self.npc_context, "user_pref", None),
      guild_pref=getattr(self.npc_context, "guild_pref", None),
      fallback=self._
    )
    if interaction.user.id != self.npc_context.mestre_id:
      return await interaction.response.send_message(
        t("npc.perm.denied", loc),
        ephemeral=True
      )
    await interaction.response.send_modal(NPCAddTestModifierModal(npc_context=self.npc_context))

  @discord.ui.button(
    label="🔙 Voltar",
    style=discord.ButtonStyle.danger,
    custom_id="npc:tests:back"
  )
  async def back_to_main_menu(self, interaction: discord.Interaction, button: discord.ui.Button):
    loc = resolve_locale(
      interaction,
      user_pref=getattr(self.npc_context, "user_pref", None),
      guild_pref=getattr(self.npc_context, "guild_pref", None),
      fallback=self._
    )
    if interaction.user.id != self.npc_context.mestre_id:
      return await interaction.response.send_message(
        t("npc.perm.denied", loc),
        ephemeral=True
      )

    view = NPCMainMenuView(npc_context=self.npc_context)
    await interaction.response.edit_message(
      content=t("npc.main.editing", loc).format(name=self.npc_context.npc_name),
      view=view,
      embed=None
    )
