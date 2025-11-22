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
from utils.dice_roller import roll_dice

class SimpleRollModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("roll.simple.title", self.locale))
        rolls_root = self.ficha.get("rolagens", {}) or {}
        drafts = rolls_root.get("drafts", {}) or {}
        saved = drafts.get("simple", {}) or {}

        self.dice_string = discord.ui.TextInput(
            label=t("roll.simple.input.label", self.locale),
            placeholder=t("roll.simple.input.ph", self.locale),
            default=saved.get("dice", ""),
            max_length=200,
            required=True,
        )

        self.add_item(self.dice_string)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            total, breakdown = roll_dice(self.dice_string.value)
        except Exception as e:
            await interaction.response.send_message(
                t("roll.simple.errors.parse", self.locale, msg=str(e)),
                ephemeral=True
            )
            return

        rolls_root = self.ficha.setdefault("rolagens", {})
        drafts = rolls_root.setdefault("drafts", {})
        drafts["simple"] = {"dice": self.dice_string.value}
        self.save()

        embed = discord.Embed(
            title=t("roll.simple.embed.title", self.locale),
            description=t("roll.simple.embed.result", self.locale, total=total),
            color=(interaction.user.color if hasattr(interaction.user, "color") else discord.Color.blurple())
        )
        embed.add_field(
            name=t("roll.simple.embed.details", self.locale),
            value=f"`{breakdown}`",
            inline=False
        )
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
