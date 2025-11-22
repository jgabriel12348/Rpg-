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
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
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

class GMNPCSheetView(discord.ui.View):
  def __init__(self, npc_context: NPCContext):
    super().__init__(timeout=300)
    self.npc_context = npc_context
    self.current_section = "geral"

    base_locale = (
      getattr(npc_context, "user_pref", None)
      or getattr(npc_context, "guild_pref", None)
      or getattr(npc_context, "locale", None)
      or "pt"
    )

    self._lbl_geral      = _tr("npc.sheet.tabs.general",     base_locale, "Geral")
    self._lbl_atributos  = _tr("npc.sheet.tabs.attributes",  base_locale, "Atributos")
    self._lbl_combate    = _tr("npc.sheet.tabs.combat",      base_locale, "Combate")
    self._lbl_roleplay   = _tr("npc.sheet.tabs.roleplay",    base_locale, "Roleplay")
    self._lbl_pets       = _tr("npc.sheet.tabs.pets",        base_locale, "Pets")
    self._lbl_reveal     = _tr("npc.sheet.actions.reveal",   base_locale, "👁️ Revelar no Chat")
    self._lbl_hide       = _tr("npc.sheet.actions.hide",     base_locale, "🔒 Ocultar dos Jogadores")

    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "npc:sheet:general":
          item.label = self._lbl_geral
        elif item.custom_id == "npc:sheet:attributes":
          item.label = self._lbl_atributos
        elif item.custom_id == "npc:sheet:combat":
          item.label = self._lbl_combate
        elif item.custom_id == "npc:sheet:roleplay":
          item.label = self._lbl_roleplay
        elif item.custom_id == "npc:sheet:pets":
          item.label = self._lbl_pets
        elif item.custom_id == "npc:sheet:reveal":
          item.label = self._lbl_reveal
        elif item.custom_id == "npc:sheet:hide":
          item.label = self._lbl_hide

  async def create_embed(self, interaction: discord.Interaction) -> discord.Embed:
    loc = resolve_locale(interaction, fallback="pt")

    npc_data = self.npc_context.load()

    title = _tr("npc.sheet.title", loc, "Ficha Completa de {name}", name=self.npc_context.npc_name)
    embed = discord.Embed(title=title, color=discord.Color.dark_purple())

    aparencia_valor = npc_data.get("extras", {}).get("aparencia") or npc_data.get("informacoes_extras", {}).get("aparencia")
    if aparencia_valor and (aparencia_valor.startswith("http://") or aparencia_valor.startswith("https://")):
      embed.set_image(url=aparencia_valor)

    lbl_raca        = _tr("npc.sheet.fields.race",          loc, "Raça/Espécie")
    lbl_classe      = _tr("npc.sheet.fields.class",         loc, "Classe/Profissão")
    lbl_nivel       = _tr("npc.sheet.fields.level",         loc, "Nível/Rank")
    lbl_visibility  = _tr("npc.sheet.fields.visibility",    loc, "Visibilidade")
    lbl_relac       = _tr("npc.sheet.fields.relationship",  loc, "Relacionamento")
    lbl_aparencia   = _tr("npc.sheet.fields.appearance",    loc, "Aparência")
    lbl_attrs_desc  = _tr("npc.sheet.sections.attributes",  loc, "Atributos base do NPC.")
    lbl_combate_desc= _tr("npc.sheet.sections.combat",      loc, "Visão geral de combate.")
    lbl_hp          = _tr("npc.sheet.fields.hp",            loc, "❤️ Vida (PV)")
    lbl_mp          = _tr("npc.sheet.fields.mp",            loc, "💙 Mana (PM)")
    lbl_ca          = _tr("npc.sheet.fields.ac",            loc, "🛡️ Defesa/CA")
    lbl_ataques     = _tr("npc.sheet.fields.attacks",       loc, "⚔️ Ataques")
    lbl_magias      = _tr("npc.sheet.fields.spells",        loc, "🔮 Magias")
    lbl_person      = _tr("npc.sheet.fields.personality",   loc, "Personalidade:")
    lbl_tracos      = _tr("npc.sheet.fields.traits",        loc, "Traços")
    lbl_inimigos    = _tr("npc.sheet.fields.enemies",       loc, "Inimigos")
    lbl_segredos    = _tr("npc.sheet.fields.secrets",       loc, "Segredos")
    lbl_pets_desc   = _tr("npc.sheet.sections.pets",        loc, "Pets e Companheiros do NPC.")
    lbl_pets_none   = _tr("npc.sheet.none.pets",            loc, "Nenhum pet registrado.")
    lbl_none        = _tr("npc.sheet.none.generic",         loc, "Nenhum")
    lbl_none_f      = _tr("npc.sheet.none.generic_f",       loc, "Nenhuma")
    lbl_master      = _tr("npc.sheet.footer.master",        loc, "Mestre")
    lbl_viewing     = _tr("npc.sheet.footer.viewing",       loc, "Visualizando")
    visivel_label   = _tr("npc.sheet.visibility.visible",   loc, "👁️ Visível")
    oculto_label    = _tr("npc.sheet.visibility.hidden",    loc, "🔒 Oculto")

    section_display = {
      "geral":     self._lbl_geral,
      "atributos": self._lbl_atributos,
      "combate":   self._lbl_combate,
      "roleplay":  self._lbl_roleplay,
      "pets":      self._lbl_pets,
    }

    if self.current_section == "geral":
      info_basicas = npc_data.get("informacoes_basicas", {})
      info_gerais  = npc_data.get("informacoes_gerais", {})

      embed.description = f"**{info_basicas.get('titulo_apelido', _tr('npc.sheet.default.creature', loc, 'Criatura Misteriosa'))}**"
      embed.add_field(name=lbl_raca,   value=info_basicas.get('raca_especie', 'N/A'), inline=True)
      embed.add_field(name=lbl_classe, value=info_basicas.get('classe_profissao', 'N/A'), inline=True)
      embed.add_field(name=lbl_nivel,  value=info_gerais.get('nivel_rank', 'N/A'), inline=True)

      vis_txt = visivel_label if npc_data.get("visivel_para_players") else oculto_label
      embed.add_field(name=lbl_visibility, value=vis_txt, inline=True)

      embed.add_field(name=lbl_relac, value=npc_data.get("relacionamento", "Neutro"), inline=True)

      if aparencia_valor and not (aparencia_valor.startswith("http://") or aparencia_valor.startswith("https://")):
        embed.add_field(name=lbl_aparencia, value=aparencia_valor, inline=False)

    elif self.current_section == "atributos":
      attrs = npc_data.get("atributos", {})
      embed.description = lbl_attrs_desc
      for name, value in attrs.items():
        embed.add_field(name=str(name).capitalize(), value=f"`{value}`", inline=True)

    elif self.current_section == "combate":
      combate = npc_data.get("informacoes_combate", {})
      embed.description = lbl_combate_desc
      embed.add_field(name=lbl_hp, value=f"`{combate.get('vida_atual', 'N/A')} / {combate.get('vida_maxima', 'N/A')}`", inline=True)
      embed.add_field(name=lbl_mp, value=f"`{combate.get('magia_atual', 'N/A')} / {combate.get('magia_maxima', 'N/A')}`", inline=True)
      embed.add_field(name=lbl_ca, value=f"`{combate.get('defesa', 'N/A')}`", inline=True)

      ataques = npc_data.get("ataques", [])
      ataques_text = "\n".join(f"• **{a.get('nome')}** (`{a.get('dano')}`)" for a in ataques) or lbl_none
      embed.add_field(name=lbl_ataques, value=ataques_text, inline=False)

      magias = npc_data.get("magias", [])
      magias_text = "\n".join(f"• **{m.get('nome')}** (`{m.get('custo')}`)" for m in magias) or lbl_none_f
      embed.add_field(name=lbl_magias, value=magias_text, inline=False)

    elif self.current_section == "roleplay":
      personalidade = npc_data.get("personalidade", {})
      aliancas      = npc_data.get("aliancas", {})
      embed.description = f"**{lbl_person}** {personalidade.get('resumo', 'N/A')}"
      embed.add_field(name=lbl_tracos,   value=personalidade.get('tracos_marcantes', 'N/A'), inline=False)
      embed.add_field(name=lbl_inimigos, value=aliancas.get('inimigos', lbl_none), inline=False)

      segredos_list = npc_data.get('roleplay', {}).get('segredos', [])
      segredos_text = "\n".join(f"• {s.get('segredo')}" for s in segredos_list) or lbl_none
      embed.add_field(name=lbl_segredos, value=segredos_text, inline=False)

    elif self.current_section == "pets":
      pets = npc_data.get("pets", [])
      embed.description = lbl_pets_desc
      if not pets:
        embed.description += f"\n\n{lbl_pets_none}"
      else:
        for pet in pets:
          pet_title = f"🐾 {pet.get('nome', _tr('npc.sheet.default.pet_name', loc, 'Pet sem nome'))}"
          pet_info = (
            f"**{_tr('npc.sheet.pet.species', loc, 'Espécie')}:** {pet.get('especie', 'N/A')}\n"
            f"**{_tr('npc.sheet.pet.skills',  loc, 'Habilidades')}:** {pet.get('habilidades', 'N/A')}"
          )
          embed.add_field(name=pet_title, value=pet_info, inline=False)

    sec_disp = section_display.get(self.current_section, self.current_section.capitalize())
    embed.set_footer(text=f"{lbl_master}: {interaction.user.display_name} | {lbl_viewing}: {sec_disp}")
    return embed

  async def update_message(self, interaction: discord.Interaction):
    embed = await self.create_embed(interaction)
    await interaction.response.edit_message(embed=embed, view=self)

  @discord.ui.button(label="npc.sheet.tabs.general", style=discord.ButtonStyle.primary, custom_id="npc:sheet:general")
  async def geral_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "geral"
    await self.update_message(interaction)

  @discord.ui.button(label="npc.sheet.tabs.attributes", style=discord.ButtonStyle.secondary, custom_id="npc:sheet:attributes")
  async def atributos_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "atributos"
    await self.update_message(interaction)

  @discord.ui.button(label="npc.sheet.tabs.combat", style=discord.ButtonStyle.danger, custom_id="npc:sheet:combat")
  async def combate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "combate"
    await self.update_message(interaction)

  @discord.ui.button(label="npc.sheet.tabs.roleplay", style=discord.ButtonStyle.blurple, custom_id="npc:sheet:roleplay")
  async def roleplay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "roleplay"
    await self.update_message(interaction)

  @discord.ui.button(label="npc.sheet.tabs.pets", style=discord.ButtonStyle.secondary, custom_id="npc:sheet:pets")
  async def pets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "pets"
    await self.update_message(interaction)

  @discord.ui.button(label="npc.sheet.actions.reveal", style=discord.ButtonStyle.success, custom_id="npc:sheet:reveal")
  async def reveal_npc(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.defer()

    npc_data = self.npc_context.load()
    npc_data["visivel_para_players"] = True
    self.npc_context.save(npc_data)

    embed = create_npc_summary_embed(npc_data)
    await interaction.channel.send(embed=embed)

    self.current_section = "geral"
    new_embed = await self.create_embed(interaction)
    await interaction.edit_original_response(embed=new_embed, view=self)

  @discord.ui.button(label="npc.sheet.actions.hide", style=discord.ButtonStyle.danger, custom_id="npc:sheet:hide")
  async def hide_npc(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.defer()

    npc_data = self.npc_context.load()
    npc_data["visivel_para_players"] = False
    self.npc_context.save(npc_data)

    self.current_section = "geral"
    new_embed = await self.create_embed(interaction)
    await interaction.edit_original_response(embed=new_embed, view=self)
