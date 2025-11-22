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
import time
from utils.player_utils import load_player_sheet, save_player_sheet
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class BaseBuilderView(discord.ui.View):
    def __init__(self, user: discord.User, build_id: str, build_type: str, build_type_plural: str):
        super().__init__(timeout=None)
        self.user = user
        self.build_id = build_id
        self.build_type = build_type
        self.build_type_plural = build_type_plural

        self.character_name = f"{user.id}_{user.name.lower()}"
        self.locale = "pt"

        ficha = load_player_sheet(self.character_name)

        player_attributes_keys = ficha.get("atributos", {}).keys()
        self.player_attributes = list(player_attributes_keys)
        self.player_attributes.append(t("builder.attr.none", self.locale))
        self.draft_key = f"{self.build_type_plural}_em_progresso"
        self.draft = ficha.get(self.draft_key, {}).get(self.build_id, {})

        self._add_components()

    def _ensure_locale(self, interaction: discord.Interaction | None = None):
        if interaction:
            self.locale = resolve_locale(interaction)

    def _i(self, key: str, **kw) -> str:
        return t(key, self.locale, **kw)

    def _add_components(self):
        raise NotImplementedError

    def create_embed(self) -> discord.Embed:
        raise NotImplementedError

    def _update_components_state(self):
        raise NotImplementedError

    def save_button(self):
        button = discord.ui.Button(
            label=self._i("builder.save.label"),
            style=discord.ButtonStyle.success,
            row=3
        )

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)

            ficha = load_player_sheet(self.character_name)
            itens = ficha.setdefault(self.build_type_plural, [])
            nome_atual = (self.draft.get("nome") or "").strip().lower()
            if not nome_atual:
                await interaction.response.send_message(
                    self._i("builder.errors.name_required", item=self.build_type),
                    ephemeral=True
                )
                return

            for it in itens:
                if (it.get("nome") or "").strip().lower() == nome_atual:
                    await interaction.response.send_message(
                        self._i("builder.errors.duplicate_name", name=self.draft.get("nome")),
                        ephemeral=True
                    )
                    return

            itens.append(self.draft)

            if self.build_id in ficha.get(self.draft_key, {}):
                del ficha[self.draft_key][self.build_id]

            save_player_sheet(self.character_name, ficha)

            embed = self.create_embed()
            embed.title = self._i("builder.saved.title", item=self.build_type.capitalize())
            embed.color = discord.Color.green()
            embed.add_field(
                name=self._i("builder.saved.next_steps.title"),
                value=self._i("builder.saved.next_steps.body"),
                inline=False
            )

            self.draft = {}
            self._update_components_state()

            if interaction.response.is_done():
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.edit_message(embed=embed, view=self)

        button.callback = callback
        return button

    def cancel_button(self):
        button = discord.ui.Button(
            label=self._i("builder.cancel.label"),
            style=discord.ButtonStyle.danger,
            row=3
        )

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)

            ficha = load_player_sheet(self.character_name)
            if self.build_id in ficha.get(self.draft_key, {}):
                del ficha[self.draft_key][self.build_id]
                save_player_sheet(self.character_name, ficha)

            self.stop()
            embed = self.create_embed()
            embed.title = self._i("builder.cancelled.title")
            embed.description = self._i("builder.cancelled.desc", item=self.build_type)
            embed.color = discord.Color.red()
            await interaction.response.edit_message(embed=embed, view=self)

        button.callback = callback
        return button

    def attribute_select(self):
        if len(self.player_attributes) <= 1:
            options = [discord.SelectOption(label=self._i("builder.attr.error_label"), value="None")]
            placeholder, disabled = self._i("builder.attr.error_ph"), True
        else:
            options = [
                discord.SelectOption(label=str(attr).capitalize(), value=str(attr))
                for attr in self.player_attributes
            ]
            placeholder, disabled = self._i("builder.attr.ph"), False

        select = discord.ui.Select(placeholder=placeholder, options=options, row=1, disabled=disabled)

        async def callback(interaction: discord.Interaction):
            self._ensure_locale(interaction)
            self.draft["atributo"] = select.values[0]
            ficha = load_player_sheet(self.character_name)
            ficha.setdefault(self.draft_key, {})[self.build_id] = self.draft
            save_player_sheet(self.character_name, ficha)
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

        select.callback = callback
        return select
