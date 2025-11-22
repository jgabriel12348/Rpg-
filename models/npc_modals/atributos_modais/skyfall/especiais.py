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

class NPCSkifallRecursosModal(NPCModalBase):
    def __init__(self, npc_context):
        super().__init__(npc_context, title=f"✨ Recursos de {npc_context.npc_name}")
        recursos = self.npc_data.get("recursos", {})
        self.enfase = self.create_input("Pontos de Ênfase", "0-10", recursos.get("enfase_total"))
        self.dano_sangue = self.create_input("Dano de Sangue Total", "0-5", recursos.get("dano_sangue_total"))
        self.corrupcao = self.create_input("Corrupção Total", "0-5", recursos.get("corrupcao_total"))
        self.add_item(self.enfase)
        self.add_item(self.dano_sangue)
        self.add_item(self.corrupcao)

    def create_input(self, label, placeholder, default_value):
        return discord.ui.TextInput(
            label=label,
            placeholder=placeholder,
            default=str(default_value or ""),
            required=False,
        )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            enfase_total = int(self.enfase.value or 0)
            ds_total = int(self.dano_sangue.value or 0)
            cor_total = int(self.corrupcao.value or 0)

            if not (0 <= enfase_total <= 1000):
                raise ValueError("Ênfase deve ser entre 0 e 10")
            if not (0 <= ds_total <= 5000):
                raise ValueError("Dano de Sangue deve ser entre 0 e 5")
            if not (0 <= cor_total <= 5000):
                raise ValueError("Corrupção deve ser entre 0 e 5")

            self.npc_data.setdefault("recursos", {}).update({
                "enfase_total": enfase_total,
                "dano_sangue_total": ds_total,
                "corrupcao_total": cor_total
            })
            self.save()

            embed = discord.Embed(
                title=f"✨ Recursos Especiais de {self.npc_context.npc_name}",
                description="**SkiFall RPG**",
                color=0x9932CC
            )
            embed.add_field(name="🎯 Ênfase Total", value=f"`{enfase_total}`", inline=True)
            embed.add_field(name="🩸 Dano de Sangue", value=f"`{ds_total}/5`", inline=True)
            embed.add_field(name="☠️ Corrupção", value=f"`{cor_total}/5`", inline=True)
            embed.set_footer(text=f"NPC atualizado por {interaction.user.display_name}")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError as e:
            await interaction.response.send_message(f"❌ Erro: {e}. Certifique-se de digitar apenas números válidos.", ephemeral=True)