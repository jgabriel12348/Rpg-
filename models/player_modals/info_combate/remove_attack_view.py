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
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class RemoveAttackView(discord.ui.View):
    def __init__(self, user: discord.User, previous_view: discord.ui.View):
        super().__init__(timeout=180)
        self.user = user
        self.character_name = f"{user.id}_{user.name.lower()}"
        self.previous_view = previous_view

        self.locale: str = "en"

        ficha = player_utils.load_player_sheet(self.character_name)
        ataques = ficha.get("ataques", [])

        if ataques:
            self.add_item(self.AttackSelect(ataques, owner=self))
            self.add_item(self.ConfirmRemoveButton(owner=self))

        self.add_item(self.BackButton(owner=self))

    def _ensure_locale(self, interaction: discord.Interaction | None):
        if interaction is None:
            return
        self.locale = resolve_locale(interaction)

    def sync_locale(self, interaction: discord.Interaction):
        self._ensure_locale(interaction)
        for child in self.children:
            if isinstance(child, RemoveAttackView.AttackSelect):
                child.placeholder = t("remove_attack.select.ph", self.locale)
            elif isinstance(child, RemoveAttackView.ConfirmRemoveButton):
                child.label = t("remove_attack.confirm.label", self.locale)
            elif isinstance(child, RemoveAttackView.BackButton):
                child.label = t("remove_attack.back.label", self.locale)

    class AttackSelect(discord.ui.Select):
        def __init__(self, ataques: list[dict], owner: "RemoveAttackView"):
            self.owner = owner
            options = [
                discord.SelectOption(label=a.get("nome", "—"), value=a.get("nome", "—"))
                for a in ataques
                if isinstance(a, dict) and a.get("nome")
            ]
            super().__init__(
                placeholder=t("remove_attack.select.ph", owner.locale),
                min_values=1,
                max_values=max(1, len(options)),
                options=options,
            )

        async def callback(self, interaction: discord.Interaction):
            self.owner._ensure_locale(interaction)
            self.placeholder = t("remove_attack.select.ph", self.owner.locale)
            await interaction.response.defer()

    class ConfirmRemoveButton(discord.ui.Button):
        def __init__(self, owner: "RemoveAttackView"):
            self.owner = owner
            super().__init__(
                label=t("remove_attack.confirm.label", owner.locale),
                style=discord.ButtonStyle.danger,
                row=1,
            )

        async def callback(self, interaction: discord.Interaction):
            self.owner._ensure_locale(interaction)

            select: RemoveAttackView.AttackSelect | None = None
            for child in self.view.children:
                if isinstance(child, RemoveAttackView.AttackSelect):
                    select = child
                    break

            if not select or not getattr(select, "values", None):
                await interaction.response.edit_message(
                    content=t("remove_attack.select.ph", self.owner.locale),
                    view=self.view,
                )
                return

            attacks_to_remove = set(select.values)

            ficha = player_utils.load_player_sheet(self.view.character_name)
            current = ficha.get("ataques", [])
            ficha["ataques"] = [
                ataque for ataque in current
                if not (isinstance(ataque, dict) and ataque.get("nome") in attacks_to_remove)
            ]
            player_utils.save_player_sheet(self.view.character_name, ficha)

            await interaction.response.edit_message(
                content=t("remove_attack.success", self.owner.locale, count=len(attacks_to_remove)),
                view=None,
            )

    class BackButton(discord.ui.Button):
        def __init__(self, owner: "RemoveAttackView"):
            self.owner = owner
            super().__init__(
                label=t("remove_attack.back.label", owner.locale),
                style=discord.ButtonStyle.secondary,
            )

        async def callback(self, interaction: discord.Interaction):
            self.owner._ensure_locale(interaction)
            await interaction.response.edit_message(
                content=t("remove_attack.menu_title", self.owner.locale),
                view=self.view.previous_view,
            )