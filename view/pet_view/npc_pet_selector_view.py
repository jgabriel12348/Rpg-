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
from utils.npc_utils import NPCContext
from models.shared_models.add_pet_modal import AddPetModal
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
    """
    Wrapper para usar i18n.t com fallback seguro.
    Se a chave não existir (t retorna a própria key), usamos o fallback informado.
    """
    try:
        text = t_raw(key, locale, **kwargs)
    except Exception:
        return fallback.format(**kwargs) if kwargs else fallback
    if text == key:
        try:
            return fallback.format(**kwargs) if kwargs else fallback
        except Exception:
            return fallback
    return text


class NPCPetSelectorView(discord.ui.View):
    def __init__(self, guild_id: int, mestre_id: int, *, locale: str | None = None):
        super().__init__(timeout=180)
        self.guild_id = guild_id
        self.mestre_id = mestre_id
        self._loc = locale or "pt"
        self.add_item(self.NPCSelect(guild_id, mestre_id, locale=self._loc))

    class NPCSelect(discord.ui.Select):
        def __init__(self, guild_id: int, mestre_id: int, *, locale: str = "pt"):
            self.guild_id = guild_id
            self.mestre_id = mestre_id
            self._loc = locale

            npc_names = NPCContext.list_npcs(guild_id, mestre_id)
            options = [discord.SelectOption(label=name, value=name) for name in npc_names]

            placeholder = _tr(
                "npc.pet.select.ph",
                locale,
                "Selecione o NPC para atrelar o pet..."
            )
            if not options:
                placeholder = _tr(
                    "npc.pet.select.none",
                    locale,
                    "Nenhum NPC disponível para atrelar."
                )

            super().__init__(
                placeholder=placeholder,
                options=options,
                disabled=not options,
                custom_id="npc:pet:select"
            )

        async def callback(self, interaction: discord.Interaction):
            loc = resolve_locale(interaction, fallback=self._loc)

            npc_name = self.values[0]
            npc_context = NPCContext(self.guild_id, self.mestre_id, npc_name)

            modal = AddPetModal(interaction)
            await interaction.response.send_modal(modal)

            await modal.wait()

            if not getattr(modal, "pet_data", None):
                msg = _tr(
                    "npc.pet.add.canceled",
                    loc,
                    "A adição de pet foi cancelada."
                )
                try:
                    await interaction.followup.send(msg, ephemeral=True)
                except discord.InteractionResponded:
                    pass
                return

            npc_data = npc_context.load()
            pets_list = npc_data.setdefault("pets", [])
            pets_list.append(modal.pet_data)
            npc_context.save(npc_data)

            msg = _tr(
                "npc.pet.add.done",
                loc,
                "🐾 Pet **{pet}** foi registrado para o NPC **{name}**!",
                pet=modal.pet_data.get("nome", "Pet"),
                name=npc_name
            )
            await interaction.followup.send(msg, ephemeral=True)
