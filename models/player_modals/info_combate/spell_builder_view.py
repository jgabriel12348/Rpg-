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
from models.player_modals.info_combate.view_base_builder import BaseBuilderView
from models.player_modals.info_combate.spell_modal import SpellPrimaryModal
from models.player_modals.info_combate.spell_modal_2 import SpellDetailsModal
from models.player_modals.info_combate.spell_modal_3 import SpellExtraModal
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class SpellBuilderView(BaseBuilderView):
    def __init__(self, user: discord.User, spell_id: str):
        super().__init__(user, spell_id, build_type="magia", build_type_plural="magias")
        self.locale: str | None = None
        self.btn_primary: discord.ui.Button | None = None
        self.btn_details: discord.ui.Button | None = None
        self.btn_extra: discord.ui.Button | None = None
        self.btn_save: discord.ui.Button | None = None
        self.btn_back: discord.ui.Button | None = None

        self.sel_catalyst: discord.ui.Select | None = None
        self.sel_attribute: discord.ui.Select | None = None

    def _ensure_locale(self, interaction: discord.Interaction | None = None):
        if not self.locale:
            self.locale = resolve_locale(interaction) if interaction else "pt"

    def _i(self, key: str, **kw) -> str:
        return t(key, self.locale or "pt", **kw)

    def _add_components(self):
        self._ensure_locale()

        self.btn_primary = self.primary_button()     # row=0
        self.btn_details = self.details_button()     # row=0
        self.btn_extra = self.extra_button()         # row=0
        self.sel_catalyst = self.catalyst_select()   # row=2
        self.sel_attribute = self.attribute_select() # row=3
        self.btn_save = self.save_button()           # row=4
        self.btn_back = self.back_button()           # row=4

        self.add_item(self.btn_primary)
        self.add_item(self.btn_details)
        self.add_item(self.btn_extra)
        self.add_item(self.sel_catalyst)
        self.add_item(self.sel_attribute)
        self.add_item(self.btn_save)
        self.add_item(self.btn_back)

        self._update_components_state()

    def _update_components_state(self):
        nome_preenchido = bool(self.draft.get("nome"))
        if self.btn_details: self.btn_details.disabled = not nome_preenchido
        if self.btn_extra: self.btn_extra.disabled = not nome_preenchido
        if self.btn_save: self.btn_save.disabled = not nome_preenchido

    def create_embed(self):
        self._ensure_locale()
        na = self._i("common.na")

        embed = discord.Embed(
            title=self._i("spell_builder.title", user=self.user.display_name),
            color=discord.Color.purple()
        )
        embed.add_field(name=self._i("spell_builder.field.name"),
                        value=f"**{self.draft.get('nome', '...')}**", inline=False)
        embed.add_field(name=self._i("spell_builder.field.level"),
                        value=f"`{self.draft.get('nivel', '...')}`", inline=True)
        embed.add_field(name=self._i("spell_builder.field.school"),
                        value=f"`{self.draft.get('escola', '...')}`", inline=True)
        embed.add_field(name=self._i("spell_builder.field.cast_time"),
                        value=f"`{self.draft.get('tempo_conjuracao', '...')}`", inline=True)
        embed.add_field(name=self._i("spell_builder.field.hit"),
                        value=f"`{self.draft.get('acerto', na)}`", inline=True)

        if self.draft.get("formula_acerto"):
            embed.add_field(name=self._i("spell_builder.field.hit_formula"),
                            value=f"`{self.draft['formula_acerto']}`", inline=False)
        if self.draft.get("formula_dano_cura"):
            embed.add_field(name=self._i("spell_builder.field.dmgheal_formula"),
                            value=f"`{self.draft['formula_dano_cura']}`", inline=False)

        efeito = self.draft.get("efeito", "")
        if efeito:
            efeito = (efeito[:200] + "...") if len(efeito) > 200 else efeito
        embed.add_field(name=self._i("spell_builder.field.effect"),
                        value=(efeito or "..."), inline=False)

        itens_vinculados = self.draft.get("itens_vinculados", []) or []
        itens_text = "\n".join(f"• `{item}`" for item in itens_vinculados) or f"`{self._i('spell_builder.none')}`"
        embed.add_field(name=self._i("spell_builder.field.catalysts"), value=itens_text, inline=False)

        embed.set_footer(text=self._i("spell_builder.footer_id", build_id=self.build_id))
        return embed

    def catalyst_select(self):
        self._ensure_locale()
        ficha = player_utils.load_player_sheet(self.character_name)
        inventario = ficha.get("inventario", {})
        all_items = (inventario.get("combate", []) +
                     inventario.get("magico", []) +
                     inventario.get("geral", []))

        is_disabled = not bool(all_items)
        if not all_items:
            options = [discord.SelectOption(label=self._i("spell_builder.select.no_items"), value="NO_ITEMS")]
        else:
            options = [discord.SelectOption(label=item["nome"]) for item in all_items]
            options.append(discord.SelectOption(label=self._i("spell_builder.select.unlink_all"), value="NENHUM"))

        for opt in options:
            if opt.label in (self.draft.get("itens_vinculados", []) or []):
                opt.default = True

        select = discord.ui.Select(
            placeholder=self._i("spell_builder.select.placeholder"),
            min_values=0,
            max_values=len(options),
            options=options,
            disabled=is_disabled,
            row=2
        )

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            if "NO_ITEMS" in select.values:
                await interaction.response.defer()
                return
            if "NENHUM" in select.values:
                self.draft["itens_vinculados"] = []
            else:
                self.draft["itens_vinculados"] = select.values
            self.save_draft()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

        select.callback = callback
        return select

    def attribute_select(self):
        self._ensure_locale()
        if len(self.player_attributes) <= 1:
            options = [discord.SelectOption(label=self._i("spell_builder.attr.err_label"), value="None")]
            placeholder, disabled = self._i("spell_builder.attr.err_ph"), True
        else:
            options = [discord.SelectOption(label=attr.capitalize(), value=attr) for attr in self.player_attributes]
            placeholder, disabled = self._i("spell_builder.attr.ph"), False

        select = discord.ui.Select(placeholder=placeholder, options=options, row=3, disabled=disabled)

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            self.draft["atributo"] = select.values[0]
            ficha = player_utils.load_player_sheet(self.character_name)
            ficha.setdefault(self.draft_key, {})[self.build_id] = self.draft
            player_utils.save_player_sheet(self.character_name, ficha)
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

        select.callback = callback
        return select

    def primary_button(self):
        self._ensure_locale()
        button = discord.ui.Button(label=self._i("spell_builder.btn.primary"),
                                   style=discord.ButtonStyle.primary, row=0)

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            modal = SpellPrimaryModal(interaction, self.draft)
            await interaction.response.send_modal(modal)
            if await modal.wait(): return
            self.draft.update({
                "nome": modal.nome_magia.value,
                "nivel": modal.nivel.value,
                "escola": modal.escola.value,
                "tempo_conjuracao": modal.tempo_conjuracao.value,
                "concentracao": modal.concentracao.value
            })
            self.save_draft()
            self._update_components_state()
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

        button.callback = callback
        return button

    def details_button(self):
        self._ensure_locale()
        button = discord.ui.Button(label=self._i("spell_builder.btn.details"),
                                   style=discord.ButtonStyle.secondary, row=0, disabled=True)

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            modal = SpellDetailsModal(interaction, self.draft)
            await interaction.response.send_modal(modal)
            if await modal.wait(): return
            self.draft.update({
                "componentes": modal.componentes.value,
                "alcance": modal.alcance.value,
                "efeito": modal.efeito.value,
                "formula_acerto": modal.formula_acerto.value,
                "formula_dano_cura": modal.formula_dano_cura.value,
            })
            self.save_draft()
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

        button.callback = callback
        return button

    def extra_button(self):
        self._ensure_locale()
        button = discord.ui.Button(label=self._i("spell_builder.btn.extra"),
                                   style=discord.ButtonStyle.secondary, row=0, disabled=True)

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            modal = SpellExtraModal(interaction, self.draft)
            await interaction.response.send_modal(modal)
            if await modal.wait(): return
            self.draft.update({
                "area_acao": modal.area_acao.value,
                "duracao": modal.duracao.value,
                "em_niveis_superiores": modal.em_niveis_superiores.value,
                "classe_conjurador": modal.classe_conjurador.value,
                "descricao": modal.descricao.value
            })
            self.save_draft()
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

        button.callback = callback
        return button

    def save_draft(self):
        ficha = player_utils.load_player_sheet(self.character_name)
        ficha.setdefault(self.draft_key, {})[self.build_id] = self.draft
        player_utils.save_player_sheet(self.character_name, ficha)

    def save_button(self):
        self._ensure_locale()
        button = discord.ui.Button(label=self._i("spell_builder.btn.save"),
                                   style=discord.ButtonStyle.success, row=4, disabled=True)

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            ficha = player_utils.load_player_sheet(self.character_name)

            ataques = ficha.get("ataques")
            if ataques is None:
                ataques = []
            elif isinstance(ataques, dict):
                ataques = list(ataques.values())
            elif not isinstance(ataques, list):
                ataques = []

            nome_novo = (self.draft.get("nome") or "").strip()
            if not nome_novo:
                await interaction.response.send_message(self._i("spell_builder.errors.no_name"), ephemeral=True)
                return

            expr_acerto = (self.draft.get("formula_acerto") or "").strip()
            expr_dano   = (self.draft.get("formula_dano_cura") or "").strip()

            ataque_like = {
                "nome": nome_novo,
                "teste_de_acerto": expr_acerto,
                "dano": expr_dano,
                "alcance": self.draft.get("alcance", ""),
                "usos": self.draft.get("usos", ""),
                "efeitos": self.draft.get("efeito", ""),
                "descricao": self.draft.get("descricao", ""),
                "tipo_dano": self.draft.get("tipo_dano", "mágico"),
                "margem_critico": self.draft.get("margem_critico", "20"),
                "multiplicador_critico": self.draft.get("multiplicador_critico", "2"),
                "tipo": "magia",
                "nivel": self.draft.get("nivel", ""),
                "escola": self.draft.get("escola", ""),
                "tempo_conjuracao": self.draft.get("tempo_conjuracao", ""),
                "concentracao": self.draft.get("concentracao", ""),
                "area_acao": self.draft.get("area_acao", ""),
                "duracao": self.draft.get("duracao", ""),
                "em_niveis_superiores": self.draft.get("em_niveis_superiores", ""),
                "classe_conjurador": self.draft.get("classe_conjurador", ""),
                "componentes": self.draft.get("componentes", ""),
            }

            updated = False
            for i, atk in enumerate(ataques):
                if isinstance(atk, dict) and (atk.get("nome") or "").strip().lower() == nome_novo.lower():
                    ataques[i] = ataque_like
                    updated = True
                    break
            if not updated:
                ataques.append(ataque_like)

            ficha["ataques"] = ataques

            if self.build_id in ficha.get(self.draft_key, {}):
                del ficha[self.draft_key][self.build_id]
            player_utils.save_player_sheet(self.character_name, ficha)

            embed = self.create_embed()
            embed.title = self._i("spell_builder.saved.title")
            embed.color = discord.Color.green()
            await interaction.response.edit_message(embed=embed, view=self)

        button.callback = callback
        return button

    def back_button(self):
        self._ensure_locale()
        button = discord.ui.Button(label=self._i("spell_builder.btn.back"),
                                   style=discord.ButtonStyle.secondary, row=4)

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            try:
                from view.ficha_player.player_skills import PlayerAtaquesMenuView
                ficha = player_utils.load_player_sheet(self.character_name)
                if self.build_id in ficha.get(self.draft_key, {}):
                    del ficha[self.draft_key][self.build_id]
                    player_utils.save_player_sheet(self.character_name, ficha)
                view = PlayerAtaquesMenuView(user=self.user)
                await interaction.response.edit_message(
                    content=self._i("spell_builder.menu_title"),
                    view=view,
                    embed=None
                )
            except Exception as e:
                print(f"[ERRO AO VOLTAR]: {e.__class__.__name__}: {e}")
                await interaction.followup.send(self._i("spell_builder.errors.back_fail"), ephemeral=True)

        button.callback = callback
        return button
