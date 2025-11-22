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
from models.npc_modals.npc_basic_modal import NPCModalBase
from utils.i18n import t
from utils.locale_resolver import resolve_locale

class NPCAddSecretModal(NPCModalBase):
    def __init__(self, npc_context):
        _ = resolve_locale(getattr(npc_context, "interaction", None))
        self._ = _

        super().__init__(
            npc_context,
            title=t("npc.secret.add.title", _, name=npc_context.npc_name)
        )

        roleplay = (self.npc_data.get("roleplay") or {})
        drafts = (roleplay.get("drafts") or {})
        saved = (drafts.get("add_segredo") or {})

        self.segredo = discord.ui.TextInput(
            label=t("npc.secret.add.secret.label", _),
            style=discord.TextStyle.paragraph,
            placeholder=t("npc.secret.add.secret.ph", _),
            required=True,
            max_length=2000,
            default=saved.get("segredo", "") or ""
        )
        self.quem_sabe = discord.ui.TextInput(
            label=t("npc.secret.add.whoknows.label", _),
            placeholder=t("npc.secret.add.whoknows.ph", _),
            required=False,
            max_length=200,
            default=saved.get("quem_sabe", "") or ""
        )

        self.add_item(self.segredo)
        self.add_item(self.quem_sabe)

    async def on_submit(self, interaction: discord.Interaction):
        roleplay = self.npc_data.setdefault("roleplay", {})
        drafts = roleplay.setdefault("drafts", {})
        secrets_list = roleplay.setdefault("segredos", [])
        drafts["add_segredo"] = {
            "segredo": self.segredo.value,
            "quem_sabe": self.quem_sabe.value
        }

        secrets_list.append({
            "segredo": self.segredo.value,
            "quem_sabe": self.quem_sabe.value
        })

        self.save()

        await interaction.response.send_message(
            t("npc.secret.add.saved", self._, name=self.npc_context.npc_name),
            ephemeral=True
        )
