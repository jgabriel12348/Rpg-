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
from utils import npc_utils
from models.npc_modals.info_combate.view_base_builder import NPCBaseBuilderView
from models.npc_modals.info_combate.attack_modal import NPCAttackPrimaryModal
from models.npc_modals.info_combate.attack_modal_2 import NPCAttackDetailsModal
from utils.i18n import t

class NPCAttackBuilderView(NPCBaseBuilderView):
    def __init__(self, npc_context, attack_id: str):
        self.locale = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )
        super().__init__(npc_context, attack_id, build_type='ataque', build_type_plural='ataques')

    def _add_components(self):
        self.add_item(self.primary_button())
        self.add_item(self.details_button())
        self.add_item(self.item_select())
        self.add_item(self.attribute_select())
        self.add_item(self.save_button())
        self.add_item(self.cancel_button())
        self.add_item(self.back_button())
        self._update_components_state()

    def _update_components_state(self):
        details_btn = next(
            (c for c in self.children if isinstance(c, discord.ui.Button) and c.label == t("builder.part2", self.locale)),
            None
        )
        save_btn = next(
            (c for c in self.children if isinstance(c, discord.ui.Button) and c.label == t("builder.save_finish", self.locale)),
            None
        )
        nome_preenchido = bool(self.draft.get("nome"))
        if details_btn:
            details_btn.disabled = not nome_preenchido
        if save_btn:
            save_btn.disabled = not nome_preenchido

    def create_embed(self):
        embed = discord.Embed(
            title=t("npc.attack.builder.title", self.locale, name=self.npc_context.npc_name),
            color=discord.Color.gold()
        )
        embed.add_field(
            name=t("builder.name", self.locale),
            value=f"**{self.draft.get('nome', '...')}**",
            inline=False
        )
        embed.add_field(
            name=t("builder.damage", self.locale),
            value=f"`{self.draft.get('dano', '...')}`",
            inline=True
        )
        embed.add_field(
            name=t("builder.attribute", self.locale),
            value=f"`{self.draft.get('atributo', '...')}`",
            inline=True
        )

        itens_vinculados = self.draft.get('itens_vinculados', [])
        itens_text = "\n".join(f"• `{item}`" for item in itens_vinculados) or f"`{t('misc.none', self.locale)}`"
        embed.add_field(
            name=t("builder.linked_items", self.locale),
            value=itens_text,
            inline=False
        )
        embed.set_footer(text=t("builder.draft_id", self.locale, id=self.build_id))
        return embed

    def item_select(self):
        npc_data = self.npc_context.load()
        combat_items = npc_data.get("inventario", {}).get("combate", []) or []

        is_disabled = False
        if not combat_items:
            options = [
                discord.SelectOption(
                    label=t("npc.attack.select.no_items", self.locale),
                    value="NO_ITEMS"
                )
            ]
            is_disabled = True
        else:
            options = [discord.SelectOption(label=item['nome']) for item in combat_items]
            options.append(discord.SelectOption(
                label=t("npc.attack.select.unlink_all", self.locale),
                value="NENHUM"
            ))

        itens_atuais = self.draft.get("itens_vinculados", [])
        for opt in options:
            if opt.label in itens_atuais:
                opt.default = True

        select = discord.ui.Select(
            placeholder=t("npc.attack.select.ph", self.locale),
            min_values=0,
            max_values=len(options),
            options=options,
            disabled=is_disabled,
            row=2
        )

        async def callback(interaction: discord.Interaction):
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

    def primary_button(self):
        button = discord.ui.Button(
            label=t("builder.part1", self.locale),
            style=discord.ButtonStyle.primary,
            row=0
        )

        async def callback(interaction: discord.Interaction):
            modal = NPCAttackPrimaryModal(self.npc_context, interaction)
            await interaction.response.send_modal(modal)
            if await modal.wait():
                return

            self.draft.update({
                "nome": modal.nome_ataque.value,
                "teste_de_acerto": modal.teste_de_acerto.value,
                "dano": modal.dano.value,
                "alcance": modal.alcance.value,
                "usos": modal.usos.value
            })
            self.save_draft()
            self._update_components_state()
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

        button.callback = callback
        return button

    def details_button(self):
        button = discord.ui.Button(
            label=t("builder.part2", self.locale),
            style=discord.ButtonStyle.secondary,
            row=0
        )

        async def callback(interaction: discord.Interaction):
            modal = NPCAttackDetailsModal(self.npc_context, interaction)
            await interaction.response.send_modal(modal)
            if await modal.wait():
                return

            self.draft.update({
                "efeitos": modal.efeitos.value,
                "descricao": modal.descricao.value,
                "tipo_dano": modal.tipo_dano.value,
                "margem_critico": modal.margem_critico.value,
                "multiplicador_critico": modal.multiplicador_critico.value
            })
            self.save_draft()
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

        button.callback = callback
        return button

    def back_button(self):
        button = discord.ui.Button(
            label=t("builder.back", self.locale),
            style=discord.ButtonStyle.secondary,
            row=3
        )

        async def callback(interaction: discord.Interaction):
            from view.ficha_npc.npc_skills import NPCSkillsView
            npc_data = self.npc_context.load()
            drafts = npc_data.get(self.draft_key, {})
            if self.build_id in drafts:
                del drafts[self.build_id]
                self.npc_context.save(npc_data)

            view = NPCSkillsView(npc_context=self.npc_context)
            await interaction.response.edit_message(
                content=t("npc.attack.back_to_menu", self.locale, name=self.npc_context.npc_name),
                view=view,
                embed=None
            )

        button.callback = callback
        return button
