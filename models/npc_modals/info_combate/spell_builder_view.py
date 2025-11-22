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
from models.npc_modals.info_combate.view_base_builder import NPCBaseBuilderView
from models.npc_modals.info_combate.spell_modal import NPCSpellPrimaryModal
from models.npc_modals.info_combate.spell_modal_2 import NPCSpellDetailsModal
from models.npc_modals.info_combate.spell_modal_3 import NPCSpellExtraModal
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCSpellBuilderView(NPCBaseBuilderView):
    def __init__(self, npc_context, spell_id: str):
        self.locale = resolve_locale(npc_context.interaction)
        super().__init__(npc_context, spell_id, build_type='magia', build_type_plural='magias')
    def _add_components(self):
        self.add_item(self.primary_button())
        self.add_item(self.details_button())
        self.add_item(self.extra_button())
        self.add_item(self.catalyst_select())
        self.add_item(self.attribute_select())
        self.add_item(self.save_button())
        self.add_item(self.back_button())
        self._update_components_state()

    def create_embed(self):
        _ = self.locale
        embed = discord.Embed(
            title=t("npc.spell.builder.title", _, name=self.npc_context.npc_name),
            color=discord.Color.purple()
        )
        embed.add_field(
            name=t("common.fields.name", _),
            value=f"**{self.draft.get('nome', '...')}**", inline=False
        )
        embed.add_field(
            name=t("npc.spell.builder.level", _),
            value=f"`{self.draft.get('nivel', self.draft.get('custo','...'))}`",
            inline=True
        )
        embed.add_field(
            name=t("npc.spell.builder.school", _),
            value=f"`{self.draft.get('escola', '...')}`",
            inline=True
        )
        embed.add_field(
            name=t("npc.spell.builder.cast_time", _),
            value=f"`{self.draft.get('tempo_conjuracao', self.draft.get('tempo','...'))}`",
            inline=True
        )
        embed.add_field(
            name=t("npc.spell.builder.duration", _),
            value=f"`{self.draft.get('duracao', '...')}`",
            inline=True
        )
        embed.add_field(
            name=t("npc.spell.builder.range_area", _),
            value=f"`{self.draft.get('alcance','...')}`",
            inline=True
        )

        if self.draft.get("formula_acerto"):
            embed.add_field(
                name=t("npc.spell.builder.hit_formula", _),
                value=f"`{self.draft['formula_acerto']}`",
                inline=False
            )
        if self.draft.get("formula_dano_cura"):
            embed.add_field(
                name=t("npc.spell.builder.damage_heal", _),
                value=f"`{self.draft['formula_dano_cura']}`",
                inline=False
            )

        efeito = self.draft.get("efeito", "")
        if efeito:
            efeito = (efeito[:200] + "...") if len(efeito) > 200 else efeito
        embed.add_field(
            name=t("npc.spell.builder.effect", _),
            value=(efeito or "`...`"),
            inline=False
        )

        itens = self.draft.get("itens_vinculados", [])
        if isinstance(itens, str):
            itens = [itens] if itens else []
        itens_text = "\n".join(f"• `{i}`" for i in itens) or f"`{t('common.none', _)}`"
        embed.add_field(
            name=t("npc.spell.builder.bound_catalysts", _),
            value=itens_text,
            inline=False
        )

        embed.set_footer(text=t("common.draft_id", _, id=self.build_id))
        return embed

    def catalyst_select(self):
        _ = self.locale
        npc_data = self.npc_context.load()
        inventario = npc_data.get("inventario", {})
        combat_items = inventario.get("combate", []) or []
        random_items = inventario.get("aleatorio", []) or []
        all_items = [i for i in (combat_items + random_items) if isinstance(i, dict) and i.get("nome")]

        options = []
        if not all_items:
            options.append(discord.SelectOption(
                label=t("npc.spell.builder.no_bindable_items", _), value="NO_ITEMS"))
        else:
            options = [discord.SelectOption(label=item["nome"]) for item in all_items]
            options.append(discord.SelectOption(
                label=t("common.unbind_all_option", _), value="NENHUM"))

        vinculados = self.draft.get("itens_vinculados", [])
        if isinstance(vinculados, str):
            vinculados = [vinculados] if vinculados else []
        for opt in options:
            if opt.value not in ("NO_ITEMS", "NENHUM") and opt.label in vinculados:
                opt.default = True

        select = discord.ui.Select(
            placeholder=t("npc.spell.builder.catalyst_placeholder", _),
            min_values=0,
            max_values=max(1, len(options)),  # evita 0
            options=options,
            disabled=(len(options) == 1 and options[0].value == "NO_ITEMS"),
            row=2
        )

        async def callback(interaction: discord.Interaction):
            vals = select.values
            if "NO_ITEMS" in vals:
                await interaction.response.defer()
                return
            if "NENHUM" in vals:
                self.draft["itens_vinculados"] = []
            else:
                self.draft["itens_vinculados"] = [v for v in vals if v not in ("NO_ITEMS", "NENHUM")]
            self.save_draft()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

        select.callback = callback
        return select

    def attribute_select(self):
        base_select = super().attribute_select()
        base_select.row = 3
        return base_select

    def _update_components_state(self):
        _ = self.locale
        details_btn = next((c for c in self.children
                            if isinstance(c, discord.ui.Button)
                            and c.label == t("common.steps.part2", _)), None)
        extra_btn = next((c for c in self.children
                          if isinstance(c, discord.ui.Button)
                          and c.label == t("common.steps.part3", _)), None)
        save_btn = next((c for c in self.children
                         if isinstance(c, discord.ui.Button)
                         and c.label == t("common.actions.save_finish", _)), None)
        ok = bool(self.draft.get("nome"))
        if details_btn: details_btn.disabled = not ok
        if extra_btn:   extra_btn.disabled = not ok
        if save_btn:    save_btn.disabled = not ok

    def primary_button(self):
        _ = self.locale
        button = discord.ui.Button(
            label=t("common.steps.part1", _),
            style=discord.ButtonStyle.primary,
            row=0
        )

        async def callback(interaction: discord.Interaction):
            modal = NPCSpellPrimaryModal(self.npc_context, interaction, self.draft)
            await interaction.response.send_modal(modal)
            if await modal.wait():
                return

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
        _ = self.locale
        button = discord.ui.Button(
            label=t("common.steps.part2", _),
            style=discord.ButtonStyle.secondary,
            row=0
        )

        async def callback(interaction: discord.Interaction):
            modal = NPCSpellDetailsModal(self.npc_context, interaction, self.draft)
            await interaction.response.send_modal(modal)
            if await modal.wait():
                return

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
        _ = self.locale
        button = discord.ui.Button(
            label=t("common.steps.part3", _),
            style=discord.ButtonStyle.secondary,
            row=0
        )

        async def callback(interaction: discord.Interaction):
            modal = NPCSpellExtraModal(self.npc_context, interaction, self.draft)
            await interaction.response.send_modal(modal)
            if await modal.wait():
                return

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
        data = self.npc_context.load()
        drafts = data.setdefault(getattr(self, "draft_key", "rascunhos"), {})
        drafts[self.build_id] = self.draft
        self.npc_context.save(data)

    def save_button(self):
        _ = self.locale
        button = discord.ui.Button(
            label=t("common.actions.save_finish", _),
            style=discord.ButtonStyle.success,
            row=4
        )

        async def callback(interaction: discord.Interaction):
            data = self.npc_context.load()

            ataques = data.get("ataques")
            if ataques is None:
                ataques = []
            elif isinstance(ataques, dict):
                ataques = list(ataques.values())
            elif not isinstance(ataques, list):
                ataques = []

            nome = (self.draft.get("nome") or "").strip()
            if not nome:
                await interaction.response.send_message(
                    t("npc.spell.builder.errors.missing_name", _),
                    ephemeral=True
                )
                return

            expr_acc = (self.draft.get("formula_acerto") or "").strip()
            expr_dmg = (self.draft.get("formula_dano_cura") or "").strip()

            ataque_like = {
                "nome": nome,
                "teste_de_acerto": expr_acc,
                "dano": expr_dmg,
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
                "tempo_conjuracao": self.draft.get("tempo_conjuracao", self.draft.get("tempo","")),
                "concentracao": self.draft.get("concentracao", ""),
                "area_acao": self.draft.get("area_acao", ""),
                "duracao": self.draft.get("duracao", ""),
                "em_niveis_superiores": self.draft.get("em_niveis_superiores", ""),
                "classe_conjurador": self.draft.get("classe_conjurador", ""),
                "componentes": self.draft.get("componentes", ""),
                "itens_vinculados": self.draft.get("itens_vinculados", []),
                "atributo": self.draft.get("atributo", "")
            }

            updated = False
            for i, a in enumerate(ataques):
                if isinstance(a, dict) and a.get("nome","").strip().lower() == nome.lower():
                    ataques[i] = ataque_like
                    updated = True
                    break
            if not updated:
                ataques.append(ataque_like)

            data["ataques"] = ataques
            dkey = getattr(self, "draft_key", "rascunhos")
            drafts = data.get(dkey, {})
            if isinstance(drafts, dict) and self.build_id in drafts:
                del drafts[self.build_id]
                data[dkey] = drafts

            self.npc_context.save(data)

            embed = self.create_embed()
            embed.title = t("npc.spell.builder.saved_as_attack_title", _)
            embed.color = discord.Color.green()
            await interaction.response.edit_message(embed=embed, view=self)

        button.callback = callback
        return button

    def back_button(self):
        btn = super().back_button()
        btn.row = 4
        return btn
