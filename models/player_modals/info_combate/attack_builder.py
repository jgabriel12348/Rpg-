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
from models.player_modals.info_combate.attack_modal import AttackPrimaryModal
from models.player_modals.info_combate.attack_modal_2 import AttackDetailsModal
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class AttackBuilderView(BaseBuilderView):
    def __init__(self, user: discord.User, attack_id: str):
        super().__init__(user, attack_id, build_type='ataque', build_type_plural='ataques')
        self.locale: str | None = None
        self.btn_primary: discord.ui.Button | None = None
        self.btn_details: discord.ui.Button | None = None
        self.btn_save: discord.ui.Button | None = None
        self.btn_cancel: discord.ui.Button | None = None
        self.btn_back: discord.ui.Button | None = None

    def _ensure_locale(self, interaction: discord.Interaction | None = None):
        if not self.locale:
            self.locale = resolve_locale(interaction) if interaction else "pt"

    def _i(self, key: str, **kw) -> str:
        return t(key, self.locale or "pt", **kw)

    def _add_components(self):
        self.btn_primary = self.primary_button()
        self.btn_details = self.details_button()
        self.btn_weapon_select = self.weapon_select()
        self.btn_attribute_select = self.attribute_select()
        self.btn_save = self.save_button()
        self.btn_cancel = self.cancel_button()
        self.btn_back = self.back_button()
        self.add_item(self.btn_primary)
        self.add_item(self.btn_details)
        self.add_item(self.btn_weapon_select)
        self.add_item(self.btn_attribute_select)
        self.add_item(self.btn_save)
        self.add_item(self.btn_cancel)
        self.add_item(self.btn_back)

        self._update_components_state()

    def _update_components_state(self):
        has_name = bool(self.draft.get("nome"))
        if self.btn_details:
            self.btn_details.disabled = not has_name
        if self.btn_save:
            self.btn_save.disabled = not has_name

    def create_embed(self):
        self._ensure_locale()
        na = self._i("common.na")
        title = self._i("attack_builder.title", user=self.user.display_name)

        embed = discord.Embed(title=title, color=discord.Color.gold())
        embed.add_field(
            name=self._i("attack_builder.field.name"),
            value=f"**{self.draft.get('nome') or '...'}**",
            inline=False
        )
        embed.add_field(
            name=self._i("attack_builder.field.damage"),
            value=f"`{self.draft.get('dano') or '...'}`",
            inline=True
        )
        embed.add_field(
            name=self._i("attack_builder.field.attribute"),
            value=f"`{self.draft.get('atributo') or '...'}`",
            inline=True
        )

        itens_vinculados = self.draft.get('itens_vinculados', []) or []
        itens_text = "\n".join(f"• `{item}`" for item in itens_vinculados) or f"`{self._i('attack_builder.none')}`"
        embed.add_field(
            name=self._i("attack_builder.field.linked_items"),
            value=itens_text,
            inline=False
        )
        embed.set_footer(text=self._i("attack_builder.footer_id", build_id=self.build_id))
        return embed

    def weapon_select(self):
        self._ensure_locale()
        ficha = player_utils.load_player_sheet(self.character_name)
        combat_items = ficha.get("inventario", {}).get("combate", [])
        is_disabled = False

        if not combat_items:
            options = [discord.SelectOption(
                label=self._i("attack_builder.select.no_items"),
                value="NO_ITEMS"
            )]
            is_disabled = True
        else:
            options = [discord.SelectOption(label=item['nome']) for item in combat_items]
            options.append(discord.SelectOption(
                label=self._i("attack_builder.select.unlink_all"),
                value="NENHUM"
            ))

        itens_atuais = self.draft.get("itens_vinculados", []) or []
        for option in options:
            if option.label in itens_atuais:
                option.default = True

        select = discord.ui.Select(
            placeholder=self._i("attack_builder.select.placeholder"),
            min_values=0,
            max_values=len(options),
            options=options,
            disabled=is_disabled,
            row=2
        )

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            if "NENHUM" in select.values:
                self.draft["itens_vinculados"] = []
            else:
                self.draft["itens_vinculados"] = [v for v in select.values if v != "NO_ITEMS"]
            self.save_draft()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

        select.callback = callback
        return select

    def primary_button(self):
        self._ensure_locale()
        button = discord.ui.Button(
            label=self._i("attack_builder.btn.primary"),
            style=discord.ButtonStyle.primary,
            row=0
        )

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            modal = AttackPrimaryModal(interaction)
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
        self._ensure_locale()
        button = discord.ui.Button(
            label=self._i("attack_builder.btn.details"),
            style=discord.ButtonStyle.secondary,
            row=0,
            disabled=True
        )

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            modal = AttackDetailsModal(interaction, self.draft)
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

    def save_draft(self):
        ficha = player_utils.load_player_sheet(self.character_name)
        ataques = ficha.setdefault(self.draft_key, {})
        nome_novo = (self.draft.get("nome") or "").strip().lower()

        for atk_id, atk_data in ataques.items():
            if atk_id != self.build_id and (atk_data.get("nome") or "").strip().lower() == nome_novo:
                raise ValueError(self._i(
                    "attack_builder.errors.duplicate_name",
                    name=self.draft.get('nome') or ""
                ))

        ataques[self.build_id] = self.draft
        player_utils.save_player_sheet(self.character_name, ficha)

    def back_button(self):
        self._ensure_locale()
        button = discord.ui.Button(
            label=self._i("attack_builder.btn.back"),
            style=discord.ButtonStyle.secondary,
            row=3
        )

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            try:
                from view.ficha_player.player_skills import PlayerAtaquesMenuView
                ficha = player_utils.load_player_sheet(self.character_name)
                drafts = ficha.get(self.draft_key, {})
                if self.build_id in drafts:
                    del drafts[self.build_id]
                    player_utils.save_player_sheet(self.character_name, ficha)

                view = PlayerAtaquesMenuView(user=self.user)

                if interaction.response.is_done():
                    await interaction.edit_original_response(
                        content=self._i("attack_builder.menu_title"),
                        view=view,
                        embed=None
                    )
                else:
                    await interaction.response.edit_message(
                        content=self._i("attack_builder.menu_title"),
                        view=view,
                        embed=None
                    )
            except Exception as e:
                await interaction.followup.send(self._i("attack_builder.errors.back_fail"), ephemeral=True)

        button.callback = callback
        return button
