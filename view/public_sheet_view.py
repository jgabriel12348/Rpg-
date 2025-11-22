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


class PublicSheetView(discord.ui.View):
    def __init__(self, user_to_view: discord.User):
        super().__init__(timeout=None)
        self.user_to_view = user_to_view
        self.current_section = "geral"
        self._loc = "pt"
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "public:sheet:general":
                    item.label = _tr("public.sheet.btn.general", self._loc, "Geral")
                elif item.custom_id == "public:sheet:attrs":
                    item.label = _tr("public.sheet.btn.attrs", self._loc, "Atributos")
                elif item.custom_id == "public:sheet:combat":
                    item.label = _tr("public.sheet.btn.combat", self._loc, "Combate")
                elif item.custom_id == "public:sheet:inventory":
                    item.label = _tr("public.sheet.btn.inventory", self._loc, "Inventário")

    async def create_embed(self) -> discord.Embed:
        character_name = f"{self.user_to_view.id}_{self.user_to_view.name.lower()}"
        ficha = player_utils.load_player_sheet(character_name)

        title = _tr("public.sheet.title", self._loc, "Ficha de {name}", name=self.user_to_view.display_name)
        embed = discord.Embed(title=title, color=getattr(self.user_to_view, "color", discord.Color.blurple()))
        embed.set_thumbnail(url=self.user_to_view.display_avatar.url)

        if self.current_section == "geral":
            info_basicas = ficha.get("informacoes_basicas", {})
            info_gerais = ficha.get("informacoes_gerais", {})

            nickname = info_basicas.get('titulo_apelido', _tr("public.sheet.nickname.default", self._loc, "Aventureiro"))
            embed.description = f"**{nickname}**"

            field_raca = _tr("public.sheet.field.race", self._loc, "Raça/Espécie")
            field_classe = _tr("public.sheet.field.class", self._loc, "Classe/Profissão")
            field_nivel = _tr("public.sheet.field.level", self._loc, "Nível/Rank")
            na = _tr("common.na", self._loc, "N/A")

            embed.add_field(name=field_raca, value=info_basicas.get('raca_especie', na), inline=True)
            embed.add_field(name=field_classe, value=info_basicas.get('classe_profissao', na), inline=True)
            embed.add_field(name=field_nivel, value=info_gerais.get('nivel_rank', na), inline=True)

        elif self.current_section == "atributos":
            attrs = ficha.get("atributos", {})
            embed.description = _tr("public.sheet.attrs.desc", self._loc, "Atributos base do personagem.")
            for name, value in attrs.items():
                embed.add_field(name=name.capitalize(), value=f"`{value}`", inline=True)

        elif self.current_section == "combate":
            combate = ficha.get("informacoes_combate", {})
            embed.description = _tr("public.sheet.combat.desc", self._loc, "Visão geral de combate.")

            field_hpmax = _tr("public.sheet.combat.hpmax", self._loc, "❤️ Vida Máxima")
            field_mpmax = _tr("public.sheet.combat.mpmax", self._loc, "💙 Mana Máxima")
            field_def   = _tr("public.sheet.combat.ac",    self._loc, "🛡️ Defesa/CA")
            field_atk   = _tr("public.sheet.combat.known_attacks", self._loc, "⚔️ Ataques Conhecidos")
            na = _tr("common.na", self._loc, "N/A")
            none_txt = _tr("common.none", self._loc, "Nenhum")

            embed.add_field(name=field_hpmax, value=f"`{combate.get('vida_maxima', na)}`", inline=True)
            embed.add_field(name=field_mpmax, value=f"`{combate.get('magia_maxima', na)}`", inline=True)
            embed.add_field(name=field_def,   value=f"`{combate.get('defesa', na)}`", inline=True)

            ataques = ficha.get("ataques", [])
            ataques_text = "\n".join(f"• **{a.get('nome')}**" for a in ataques) or none_txt
            embed.add_field(name=field_atk, value=ataques_text, inline=False)

        elif self.current_section == "inventario":
            inv = ficha.get("inventario", {})
            carga = ficha.get("carga", {})

            carga_max_label = _tr("public.sheet.inv.cargamax", self._loc, "**Carga Máxima:** `{val}`")
            embed.description = carga_max_label.format(val=carga.get('maxima', _tr("common.na", self._loc, "N/A")))

            for category, items in inv.items():
                if category == 'carteira':
                    continue
                if isinstance(items, list) and items:
                    item_list = "\n".join(f"• {item['nome']}" for item in items)
                    embed.add_field(name=f"**{category.capitalize()}**", value=item_list, inline=True)

        footer = _tr(
            "public.sheet.footer",
            self._loc,
            "Visualizando: {section}",
            section=self.current_section.capitalize()
        )
        embed.set_footer(text=footer)
        return embed

    async def update_message(self, interaction: discord.Interaction):
        self._loc = resolve_locale(interaction, fallback=self._loc)
        await interaction.response.defer()
        embed = await self.create_embed()
        await interaction.edit_original_response(embed=embed, view=self)

    @discord.ui.button(label="Geral", style=discord.ButtonStyle.primary, custom_id="public:sheet:general")
    async def geral_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_section = "geral"
        await self.update_message(interaction)

    @discord.ui.button(label="Atributos", style=discord.ButtonStyle.secondary, custom_id="public:sheet:attrs")
    async def atributos_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_section = "atributos"
        await self.update_message(interaction)

    @discord.ui.button(label="Combate", style=discord.ButtonStyle.danger, custom_id="public:sheet:combat")
    async def combate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_section = "combate"
        await self.update_message(interaction)

    @discord.ui.button(label="Inventário", style=discord.ButtonStyle.success, custom_id="public:sheet:inventory")
    async def inventario_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_section = "inventario"
        await self.update_message(interaction)
