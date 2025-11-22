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
from utils import player_utils
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
  """
  Wrapper para i18n.t com fallback seguro.
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


class PersonalSheetView(discord.ui.View):
  def __init__(self, user: discord.User):
    super().__init__(timeout=300)
    self.user = user
    self.current_section = "geral"
    self._loc = "pt"

    for item in self.children:
      if isinstance(item, discord.ui.Button):
        if item.custom_id == "player:sheet:general":
          item.label = _tr("player.sheet.btn.general", self._loc, "Geral")
        elif item.custom_id == "player:sheet:attributes":
          item.label = _tr("player.sheet.btn.attributes", self._loc, "Atributos")
        elif item.custom_id == "player:sheet:combat":
          item.label = _tr("player.sheet.btn.combat", self._loc, "Combate")
        elif item.custom_id == "player:sheet:abilities":
          item.label = _tr("player.sheet.btn.abilities", self._loc, "Habilidades")
        elif item.custom_id == "player:sheet:inventory":
          item.label = _tr("player.sheet.btn.inventory", self._loc, "Inventário")
        elif item.custom_id == "player:sheet:roleplay":
          item.label = _tr("player.sheet.btn.roleplay", self._loc, "Roleplay")
        elif item.custom_id == "player:sheet:skills":
          item.label = _tr("player.sheet.btn.skills", self._loc, "Perícias")
        elif item.custom_id == "player:sheet:pets":
          item.label = _tr("player.sheet.btn.pets", self._loc, "Pets")

  async def create_embed(self) -> discord.Embed:
    character_name = f"{self.user.id}_{self.user.name.lower()}"
    ficha = player_utils.load_player_sheet(character_name)

    title = _tr("player.sheet.title", self._loc, "Ficha de {name}", name=self.user.display_name)
    embed = discord.Embed(title=title, color=getattr(self.user, "color", discord.Color.blurple()))

    aparencia_link = ficha.get("extras", {}).get("aparencia") or ficha.get("informacoes_extras", {}).get("aparencia")
    if aparencia_link and (aparencia_link.startswith("http")):
      embed.set_thumbnail(url=aparencia_link)
    else:
      embed.set_thumbnail(url=self.user.display_avatar.url)

    n_a = _tr("player.common.na", self._loc, "N/A")
    none_text = _tr("player.common.none", self._loc, "Nenhum")

    if self.current_section == "geral":
      info_basicas = ficha.get("informacoes_basicas", {})
      info_gerais = ficha.get("informacoes_gerais", {})
      alinhamento = ficha.get("alinhamento_crencas", {})

      desc_title = info_basicas.get('titulo_apelido', _tr("player.sheet.general.adventurer", self._loc, "Aventureiro"))
      embed.description = f"### {desc_title}"

      if aparencia_link and aparencia_link.startswith("http"):
        embed.set_image(url=aparencia_link)
      else:
        embed.add_field(
          name=_tr("player.sheet.general.appearance", self._loc, "🎨 Aparência"),
          value=aparencia_link or n_a,
          inline=False
        )

      embed.add_field(name="\u200b", value=_tr("player.sheet.general.main_info", self._loc, "--- **Informações Principais** ---"), inline=False)
      embed.add_field(name=_tr("player.sheet.general.race", self._loc, "🧬 Raça/Espécie"), value=info_basicas.get('raca_especie', n_a), inline=True)
      embed.add_field(name=_tr("player.sheet.general.class", self._loc, "⚔️ Classe/Profissão"), value=info_basicas.get('classe_profissao', n_a), inline=True)
      embed.add_field(name=_tr("player.sheet.general.level", self._loc, "⭐ Nível/Rank"), value=info_gerais.get('nivel_rank', n_a), inline=True)
      embed.add_field(name=_tr("player.sheet.general.age", self._loc, "🎂 Idade"), value=info_gerais.get('idade', n_a), inline=True)
      embed.add_field(name=_tr("player.sheet.general.height_weight", self._loc, "📏 Altura/Peso"), value=info_gerais.get('altura_peso', n_a), inline=True)
      embed.add_field(name=_tr("player.sheet.general.alignment", self._loc, "🧠 Alinhamento"), value=alinhamento.get('alinhamento', n_a), inline=True)

    elif self.current_section == "atributos":
      attrs = ficha.get("atributos", {})
      embed.description = _tr("player.sheet.attributes.desc", self._loc, "Estes são os atributos base do seu personagem.")
      for name, value in attrs.items():
        embed.add_field(name=name.capitalize(), value=f"`{value}`", inline=True)

    elif self.current_section == "combate":
      combate = ficha.get("informacoes_combate", {})
      deslocamento = ficha.get("informacoes_deslocamento", {})
      embed.description = _tr("player.sheet.combat.desc", self._loc, "Visão geral de combate e status.")

      embed.add_field(
        name=_tr("player.sheet.combat.hp", self._loc, "❤️ Vida"),
        value=f"`{combate.get('vida_atual', n_a)} / {combate.get('vida_maxima', n_a)}`",
        inline=True
      )
      embed.add_field(
        name=_tr("player.sheet.combat.mp", self._loc, "💙 Mana"),
        value=f"`{combate.get('magia_atual', n_a)} / {combate.get('magia_maxima', n_a)}`",
        inline=True
      )
      embed.add_field(
        name=_tr("player.sheet.combat.speed", self._loc, "👟 Deslocamento"),
        value=f"`{deslocamento.get('velocidade', n_a)}`",
        inline=True
      )
      embed.add_field(
        name=_tr("player.sheet.combat.ac", self._loc, "🛡️ Defesa/CA"),
        value=f"`{combate.get('defesa', n_a)}`",
        inline=True
      )
      embed.add_field(
        name=_tr("player.sheet.combat.mres", self._loc, "✨ Resist. Mágica"),
        value=f"`{combate.get('resistencia_magica', n_a)}`",
        inline=True
      )
      embed.add_field(
        name=_tr("player.sheet.combat.init", self._loc, "⚡ Iniciativa"),
        value=f"`{combate.get('iniciativa', n_a)}`",
        inline=True
      )
      embed.add_field(
        name=_tr("player.sheet.combat.resistances", self._loc, "🛡️ Resistências"),
        value=deslocamento.get('resistencias') or _tr("player.sheet.combat.none", self._loc, "Nenhuma"),
        inline=False
      )
      embed.add_field(
        name=_tr("player.sheet.combat.weak", self._loc, "☠️ Fraquezas"),
        value=deslocamento.get('fraquezas') or _tr("player.sheet.combat.none", self._loc, "Nenhuma"),
        inline=False
      )
      embed.add_field(
        name=_tr("player.sheet.combat.immune", self._loc, "✅ Imunidades"),
        value=deslocamento.get('imunidades') or _tr("player.sheet.combat.none", self._loc, "Nenhuma"),
        inline=False
      )

    elif self.current_section == "habilidades":
      ataques = ficha.get("ataques", [])
      magias = ficha.get("magias", [])
      embed.description = _tr("player.sheet.abilities.desc", self._loc, "Todos os ataques e magias registrados.")
      if not ataques and not magias:
        embed.description += "\n\n" + _tr("player.sheet.abilities.none", self._loc, "Nenhuma habilidade registrada.")

      if ataques:
        for ataque in ataques:
          dano = ataque.get('dano', 'N/A')
          acerto = ataque.get('teste_de_acerto', 'N/A')
          tipo = ataque.get('tipo_dano', 'N/A')
          alcance = ataque.get('alcance', 'N/A')
          desc = (_tr("player.sheet.abilities.attack.line1", self._loc, "**Dano:** `{d}` | **Acerto:** `{a}`", d=dano, a=acerto)
                  + "\n" +
                  _tr("player.sheet.abilities.attack.line2", self._loc, "**Tipo:** `{t}` | **Alcance:** `{r}`", t=tipo, r=alcance))
          embed.add_field(
            name=_tr("player.sheet.abilities.attack.title", self._loc, "⚔️ {name}", name=ataque.get('nome', _tr("player.sheet.abilities.attack.untitled", self._loc, "Ataque sem nome"))),
            value=desc,
            inline=False
          )

      if magias:
        for magia in magias:
          custo = magia.get('custo', 'N/A')
          alcance = magia.get('alcance', 'N/A')
          dur = magia.get('duracao', 'N/A')
          efeito = magia.get('efeito', 'N/A')
          desc = (_tr("player.sheet.abilities.spell.line1", self._loc, "**Custo:** `{c}` | **Alcance:** `{r}`", c=custo, r=alcance)
                  + "\n" +
                  _tr("player.sheet.abilities.spell.line2", self._loc, "**Duração:** `{d}`", d=dur)
                  + "\n" +
                  _tr("player.sheet.abilities.spell.line3", self._loc, "**Efeito:** {e}", e=efeito))
          embed.add_field(
            name=_tr("player.sheet.abilities.spell.title", self._loc, "🔮 {name}", name=magia.get('nome', _tr("player.sheet.abilities.spell.untitled", self._loc, "Magia sem nome"))),
            value=desc,
            inline=False
          )

    elif self.current_section == "inventario":
      inv = ficha.get("inventario", {})
      carga = ficha.get("carga", {})
      embed.description = _tr("player.sheet.inventory.load", self._loc, "**Carga:** `{cur}` / `{max}`", cur=carga.get('atual', 'N/A'), max=carga.get('maxima', 'N/A'))

      carteira = inv.get("carteira", {})
      carteira_text = (_tr("player.sheet.wallet.coins", self._loc, "**Moedas:** {v}", v=carteira.get('moedas', 'N/A'))
                       + "\n" +
                       _tr("player.sheet.wallet.gems", self._loc, "**Gemas:** {v}", v=carteira.get('gemas', 'N/A')))
      embed.add_field(name=_tr("player.sheet.wallet.title", self._loc, "💰 Carteira"), value=carteira_text, inline=False)

      for category in ["combate", "defesa", "consumivel", "aleatorio"]:
        items = inv.get(category, [])
        if items:
          item_list = "\n".join(
            f"• **{item.get('nome')}** (x{item.get('quantidade', 1)}): `{item.get('dano') or item.get('defesa') or item.get('efeito') or '...'}`"
            for item in items
          )
          embed.add_field(name=f"**{category.capitalize()}**", value=item_list, inline=False)

    elif self.current_section == "roleplay":
      personalidade = ficha.get("personalidade", {})
      aliancas = ficha.get("aliancas", {})
      objetivos = ficha.get("objetivos", {})
      roleplay = ficha.get("roleplay", {})
      extras = ficha.get("extras", {})

      desc = _tr(
        "player.sheet.roleplay.desc",
        self._loc,
        "**Personalidade:** {p}\n**Traços:** {t}",
        p=personalidade.get('resumo', 'N/A'),
        t=personalidade.get('tracos_marcantes', 'N/A')
      )
      embed.description = desc
      embed.add_field(name=_tr("player.sheet.roleplay.history", self._loc, "História"), value=extras.get('historia', 'N/A'), inline=False)
      embed.add_field(
        name=_tr("player.sheet.roleplay.objectives", self._loc, "Objetivos"),
        value=(_tr("player.sheet.roleplay.goal.short", self._loc, "**Curto Prazo:** {v}", v=objetivos.get('curto_prazo', 'N/A')) + "\n" +
               _tr("player.sheet.roleplay.goal.long", self._loc, "**Longo Prazo:** {v}", v=objetivos.get('longo_prazo', 'N/A'))),
        inline=False
      )
      aliados_nome = roleplay.get('aliados', [])[0]['nome'] if roleplay.get('aliados') else _tr("player.common.none", self._loc, "Nenhum")
      inimigos_nome = roleplay.get('inimigos', [])[0]['nome'] if roleplay.get('inimigos') else _tr("player.common.none", self._loc, "Nenhum")
      embed.add_field(
        name=_tr("player.sheet.roleplay.allies_enemies", self._loc, "Aliados e Inimigos"),
        value=_tr("player.sheet.roleplay.allies_enemies.value", self._loc, "**Aliados:** {a}\n**Inimigos:** {i}", a=aliados_nome, i=inimigos_nome),
        inline=False
      )

    elif self.current_section == "pets":
      pets = ficha.get("pets", [])
      embed.description = _tr("player.sheet.pets.desc", self._loc, "Pets e Companheiros.")
      if not pets:
        embed.description += "\n\n" + _tr("player.sheet.pets.none", self._loc, "Nenhum pet registrado.")
      for pet in pets:
        pet_info = (_tr("player.sheet.pets.species", self._loc, "**Espécie:** {v}", v=pet.get('especie', 'N/A'))
                    + "\n" +
                    _tr("player.sheet.pets.personality", self._loc, "**Personalidade:** {v}", v=pet.get('personalidade', 'N/A'))
                    + "\n" +
                    _tr("player.sheet.pets.skills", self._loc, "**Habilidades:** {v}", v=pet.get('habilidades', 'N/A')))
        embed.add_field(
          name=_tr("player.sheet.pets.title", self._loc, "🐾 {name}", name=pet.get('nome', _tr("player.sheet.pets.untitled", self._loc, "Pet sem nome"))),
          value=pet_info,
          inline=False
        )

    footer = _tr(
      "player.sheet.footer",
      self._loc,
      "Visualizando: {section} | Use os botões para navegar.",
      section=self.current_section.capitalize()
    )
    embed.set_footer(text=footer)
    return embed

  async def update_message(self, interaction: discord.Interaction):
    await interaction.response.defer()
    self._loc = resolve_locale(interaction, fallback=self._loc)
    embed = await self.create_embed()
    await interaction.edit_original_response(embed=embed, view=self)

  @discord.ui.button(label="Geral", style=discord.ButtonStyle.primary, custom_id="player:sheet:general")
  async def geral_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "geral"
    await self.update_message(interaction)

  @discord.ui.button(label="Atributos", style=discord.ButtonStyle.secondary, custom_id="player:sheet:attributes")
  async def atributos_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "atributos"
    await self.update_message(interaction)

  @discord.ui.button(label="Combate", style=discord.ButtonStyle.danger, custom_id="player:sheet:combat")
  async def combate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "combate"
    await self.update_message(interaction)

  @discord.ui.button(label="Habilidades", style=discord.ButtonStyle.danger, custom_id="player:sheet:abilities")
  async def habilidades_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "habilidades"
    await self.update_message(interaction)

  @discord.ui.button(label="Inventário", style=discord.ButtonStyle.success, custom_id="player:sheet:inventory")
  async def inventario_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "inventario"
    await self.update_message(interaction)

  @discord.ui.button(label="Roleplay", style=discord.ButtonStyle.blurple, custom_id="player:sheet:roleplay")
  async def roleplay_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "roleplay"
    await self.update_message(interaction)

  @discord.ui.button(label="Perícias", style=discord.ButtonStyle.secondary, custom_id="player:sheet:skills")
  async def pericias_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "pericias"
    await self.update_message(interaction)

  @discord.ui.button(label="Pets", style=discord.ButtonStyle.success, custom_id="player:sheet:pets")
  async def pets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.current_section = "pets"
    await self.update_message(interaction)
