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
from utils.i18n import t
from utils.locale_resolver import resolve_locale
from utils.npc_utils import NPCContext

class NPCBaseBuilderView(discord.ui.View):
    def __init__(self, npc_context: NPCContext, build_id: str, build_type: str, build_type_plural: str):
        super().__init__(timeout=None)
        self.locale = resolve_locale(getattr(npc_context, "interaction", None))
        self.npc_context = npc_context
        self.build_id = build_id
        self.build_type = build_type
        self.build_type_plural = build_type_plural
        self.npc_data = self.npc_context.load()
        player_attributes_keys = self.npc_data.get("atributos", {}).keys()
        self.npc_attributes = list(player_attributes_keys)
        self.npc_attributes.append("Nenhum")
        self.draft_key = f"{self.build_type_plural}_em_progresso"
        self.draft = self.npc_data.get(self.draft_key, {}).get(self.build_id, {})
        self._add_components()

    def _add_components(self):
        raise NotImplementedError

    def create_embed(self) -> discord.Embed:
        raise NotImplementedError

    def _update_components_state(self):
        raise NotImplementedError

    def save_draft(self):
        current_data = self.npc_context.load()
        current_data.setdefault(self.draft_key, {})[self.build_id] = self.draft
        self.npc_context.save(current_data)

    def attribute_select(self):
        _ = self.locale
        options = [discord.SelectOption(label=attr.capitalize(), value=attr) for attr in self.npc_attributes]
        select = discord.ui.Select(
            placeholder=t("npc.builder.attribute_select.placeholder", _),
            options=options,
            row=1,
            disabled=(len(self.npc_attributes) <= 1)
        )

        async def callback(interaction: discord.Interaction):
            self.draft["atributo"] = select.values[0]
            self.save_draft()
            await interaction.response.edit_message(embed=self.create_embed(), view=self)

        select.callback = callback
        return select

    def save_button(self):
        _ = self.locale
        button = discord.ui.Button(
            label=t("npc.builder.actions.save_finish", _),
            style=discord.ButtonStyle.success,
            row=4
        )

        async def callback(interaction: discord.Interaction):
            npc_data = self.npc_context.load()
            npc_data.setdefault(self.build_type_plural, []).append(self.draft)

            drafts = npc_data.get(self.draft_key, {})
            if self.build_id in drafts:
                del drafts[self.build_id]
                npc_data[self.draft_key] = drafts

            self.npc_context.save(npc_data)
            self.stop()

            embed = self.create_embed()
            embed.title = t("npc.builder.feedback.saved_title", _).format(
                item=self.build_type.capitalize()
            )
            embed.color = discord.Color.green()
            await interaction.response.edit_message(embed=embed, view=self)

        button.callback = callback
        return button

    def cancel_button(self):
        _ = self.locale
        button = discord.ui.Button(
            label=t("npc.builder.actions.cancel", _),
            style=discord.ButtonStyle.danger,
            row=4
        )

        async def callback(interaction: discord.Interaction):
            npc_data = self.npc_context.load()
            drafts = npc_data.get(self.draft_key, {})
            if self.build_id in drafts:
                del drafts[self.build_id]
                npc_data[self.draft_key] = drafts
                self.npc_context.save(npc_data)

            self.stop()
            embed = self.create_embed()
            embed.title = t("npc.builder.feedback.canceled_title", _)
            embed.color = discord.Color.red()
            await interaction.response.edit_message(embed=embed, view=self)

        button.callback = callback
        return button

    def back_button(self):
        _ = self.locale
        button = discord.ui.Button(
            label=t("common.actions.back", _),
            style=discord.ButtonStyle.secondary,
            row=4
        )

        async def callback(interaction: discord.Interaction):
            from view.ficha_npc.npc_skills import NPCSkillsView

            npc_data = self.npc_context.load()
            drafts = npc_data.get(self.draft_key, {})
            if self.build_id in drafts:
                del drafts[self.build_id]
                npc_data[self.draft_key] = drafts
                self.npc_context.save(npc_data)

            view = NPCSkillsView(npc_context=self.npc_context)
            await interaction.response.edit_message(
                content=t("npc.builder.back_to_menu", _).format(name=self.npc_context.npc_name),
                view=view,
                embed=None
            )

        button.callback = callback
        return button
