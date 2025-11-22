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

class AddPetModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction, *, locale: str | None = None):
        self.locale = locale or resolve_locale(interaction)
        super().__init__(interaction, title=t("pet.add.title", self.locale))
        drafts_root = self.ficha.get("pets_drafts", {}) or {}
        saved = drafts_root.get("add", {}) or {}

        self.pet_data: dict | None = None

        self.nome = discord.ui.TextInput(
            label=t("pet.add.name.label", self.locale),
            placeholder=t("pet.add.name.ph", self.locale),
            default=saved.get("nome", ""),
            max_length=100,
            required=True,
        )
        self.especie = discord.ui.TextInput(
            label=t("pet.add.species.label", self.locale),
            placeholder=t("pet.add.species.ph", self.locale),
            default=saved.get("especie", ""),
            max_length=120,
            required=True,
        )
        self.aparencia = discord.ui.TextInput(
            label=t("pet.add.appearance.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("pet.add.appearance.ph", self.locale),
            default=saved.get("aparencia", ""),
            max_length=800,
            required=False,
        )
        self.personalidade = discord.ui.TextInput(
            label=t("pet.add.personality.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("pet.add.personality.ph", self.locale),
            default=saved.get("personalidade", ""),
            max_length=800,
            required=False,
        )
        self.habilidades = discord.ui.TextInput(
            label=t("pet.add.skills.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("pet.add.skills.ph", self.locale),
            default=saved.get("habilidades", ""),
            max_length=800,
            required=False,
        )

        self.add_item(self.nome)
        self.add_item(self.especie)
        self.add_item(self.aparencia)
        self.add_item(self.personalidade)
        self.add_item(self.habilidades)

    async def on_submit(self, interaction: discord.Interaction):
        self.pet_data = {
            "nome": self.nome.value.strip(),
            "especie": self.especie.value.strip(),
            "aparencia": self.aparencia.value.strip(),
            "personalidade": self.personalidade.value.strip(),
            "habilidades": self.habilidades.value.strip(),
        }
        drafts_root = self.ficha.setdefault("pets_drafts", {})
        drafts_root["add"] = dict(self.pet_data)
        self.save()

        await interaction.response.defer(ephemeral=True)
        self.stop()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        try:
            await interaction.response.send_message(
                t("errors.http", self.locale) or "❌ Ocorreu um erro inesperado. Tente novamente.",
                ephemeral=True,
            )
        except discord.InteractionResponded:
            await interaction.followup.send(
                t("errors.http", self.locale) or "❌ Ocorreu um erro inesperado. Tente novamente.",
                ephemeral=True,
            )
