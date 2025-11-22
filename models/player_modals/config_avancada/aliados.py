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

class AddAllyModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction):
        self.locale = resolve_locale(interaction)
        super().__init__(interaction, title=t("add_ally.title", self.locale))

        roleplay = (self.ficha.get("roleplay") or {})
        drafts = (roleplay.get("drafts") or {})
        saved = (drafts.get("add_aliado") or {})

        self.nome = discord.ui.TextInput(
            label=t("add_ally.name.label", self.locale),
            placeholder=t("add_ally.name.ph", self.locale),
            required=True,
            max_length=100,
            default=saved.get("nome", "") or ""
        )
        self.descricao = discord.ui.TextInput(
            label=t("add_ally.desc.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("add_ally.desc.ph", self.locale),
            required=False,
            max_length=1000,
            default=saved.get("descricao", "") or ""
        )

        self.add_item(self.nome)
        self.add_item(self.descricao)

    async def on_submit(self, interaction: discord.Interaction):
        roleplay = self.ficha.setdefault("roleplay", {})
        drafts = roleplay.setdefault("drafts", {})
        aliados = roleplay.setdefault("aliados", [])

        drafts["add_aliado"] = {
            "nome": self.nome.value,
            "descricao": self.descricao.value
        }

        aliados.append({
            "nome": self.nome.value,
            "descricao": self.descricao.value
        })

        self.save()

        await interaction.response.send_message(
            t("add_ally.success", self.locale, name=self.nome.value),
            ephemeral=True
        )
