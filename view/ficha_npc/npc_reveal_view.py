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
from utils.embed_utils import create_npc_summary_embed
from view.ficha_npc.gm_npc_sheet_view import GMNPCSheetView
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
  """
  Wrapper para usar i18n.t com fallback seguro.
  Se a chave não existir (t retorna a própria key), usamos o fallback informado.
  """
  try:
    text = t_raw(key, locale, **kwargs)
  except Exception:
    return fallback.format(**kwargs) if kwargs else fallback
  if text == key:
    try:
      return fallback.format(**kwargs) if kwargs else fallback
    except Exception:
      return fallback
  return text


class NPCRevealView(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=None)
    self.npc_context = npc_context

  @discord.ui.button(label="👁️ Revelar no Chat", style=discord.ButtonStyle.success, custom_id="npc:reveal:reveal")
  async def reveal_npc(self, interaction: discord.Interaction, button: discord.ui.Button):
    # Atualiza visibilidade e envia o resumo no canal
    npc_data = self.npc_context.load()
    npc_data["visivel_para_players"] = True
    self.npc_context.save(npc_data)

    embed = create_npc_summary_embed(npc_data)
    await interaction.channel.send(embed=embed)

    loc = resolve_locale(
      interaction,
      user_pref=getattr(self.npc_context, "user_pref", None),
      guild_pref=getattr(self.npc_context, "guild_pref", None),
      fallback="pt",
    )
    msg = _tr("npc.reveal.done", loc, "✅ NPC **{name}** foi revelado!", name=self.npc_context.npc_name)
    await interaction.response.send_message(msg, ephemeral=True)

  @discord.ui.button(label="🔒 Ocultar dos Jogadores", style=discord.ButtonStyle.danger, custom_id="npc:reveal:hide")
  async def hide_npc(self, interaction: discord.Interaction, button: discord.ui.Button):
    npc_data = self.npc_context.load()
    npc_data["visivel_para_players"] = False
    self.npc_context.save(npc_data)

    loc = resolve_locale(
      interaction,
      user_pref=getattr(self.npc_context, "user_pref", None),
      guild_pref=getattr(self.npc_context, "guild_pref", None),
      fallback="pt",
    )
    msg = _tr(
      "npc.reveal.hidden",
      loc,
      "🔒 NPC **{name}** foi ocultado e não aparecerá mais na lista dos jogadores.",
      name=self.npc_context.npc_name
    )
    await interaction.response.send_message(msg, ephemeral=True)
