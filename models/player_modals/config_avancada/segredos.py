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
from models.player_modals.player_basic_modal import PlayerModalBase
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class AddSecretModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("add_secret.title", self.locale))

        roleplay = (self.ficha.get("roleplay") or {})
        drafts = (roleplay.get("drafts") or {})
        saved = (drafts.get("add_segredo") or {})

        self.segredo = discord.ui.TextInput(
            label=t("add_secret.secret.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("add_secret.secret.ph", self.locale),
            required=True,
            max_length=2000,
            default=saved.get("segredo", "") or ""
        )
        self.quem_sabe = discord.ui.TextInput(
            label=t("add_secret.who.label", self.locale),
            placeholder=t("add_secret.who.ph", self.locale),
            required=False,
            max_length=200,
            default=saved.get("quem_sabe", "") or ""
        )

        self.add_item(self.segredo)
        self.add_item(self.quem_sabe)

    async def on_submit(self, interaction: discord.Interaction):
        roleplay = self.ficha.setdefault("roleplay", {})
        drafts = roleplay.setdefault("drafts", {})
        segredos = roleplay.setdefault("segredos", [])

        drafts["add_segredo"] = {
            "segredo": self.segredo.value,
            "quem_sabe": self.quem_sabe.value
        }

        segredos.append({
            "segredo": self.segredo.value,
            "quem_sabe": self.quem_sabe.value
        })

        self.save()

        await interaction.response.send_message(
            t("add_secret.success", self.locale),
            ephemeral=True
        )
