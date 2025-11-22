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

class AttackEditModal(PlayerModalBase):
    def __init__(self, interaction: discord.Interaction, attack_to_edit: dict):
        self.locale = resolve_locale(interaction)
        self.attack_to_edit = attack_to_edit or {}
        title = t("attack_edit.title", self.locale, name=self.attack_to_edit.get("nome") or t("common.na", self.locale))
        super().__init__(interaction, title=title)
        self.original_attack_name = self.attack_to_edit.get("nome")
        self.nome = discord.ui.TextInput(
            label=t("attack_edit.name.label", self.locale),
            placeholder=t("attack_edit.name.ph", self.locale),
            default=self.attack_to_edit.get("nome", "") or "",
            required=True,
            max_length=120
        )
        self.teste_de_acerto = discord.ui.TextInput(
            label=t("attack_edit.hit.label", self.locale),
            placeholder=t("attack_edit.hit.ph", self.locale),
            default=self.attack_to_edit.get("teste_de_acerto", "1d20+MOD") or "1d20+MOD",
            required=True,
            max_length=120
        )
        self.dano = discord.ui.TextInput(
            label=t("attack_edit.damage.label", self.locale),
            placeholder=t("attack_edit.damage.ph", self.locale),
            default=self.attack_to_edit.get("dano", "") or "",
            required=True,
            max_length=120
        )
        self.tipo_dano = discord.ui.TextInput(
            label=t("attack_edit.damage_type.label", self.locale),
            placeholder=t("attack_edit.damage_type.ph", self.locale),
            default=self.attack_to_edit.get("tipo_dano", "") or "",
            required=False,
            max_length=60
        )
        self.efeitos = discord.ui.TextInput(
            label=t("attack_edit.effects.label", self.locale),
            style=discord.TextStyle.paragraph,
            placeholder=t("attack_edit.effects.ph", self.locale),
            default=self.attack_to_edit.get("efeitos", "") or "",
            required=False,
            max_length=1500
        )

        self.add_item(self.nome)
        self.add_item(self.teste_de_acerto)
        self.add_item(self.dano)
        self.add_item(self.tipo_dano)
        self.add_item(self.efeitos)

    async def on_submit(self, interaction: discord.Interaction):
        ataques = self.ficha.get("ataques", [])
        if isinstance(ataques, dict):
            ataques_iter = list(ataques.values())
        else:
            ataques_iter = list(ataques)
        new_name_norm = (self.nome.value or "").strip().lower()
        for atk in ataques_iter:
            if (atk.get("nome") or "").strip().lower() == new_name_norm and atk.get("nome") != self.original_attack_name:
                await interaction.response.send_message(
                    t("attack_edit.errors.duplicate_name", self.locale, name=self.nome.value),
                    ephemeral=True
                )
                return
        updated = False
        if isinstance(ataques, list):
            for ataque in ataques:
                if ataque.get("nome") == self.original_attack_name:
                    ataque["nome"] = self.nome.value
                    ataque["teste_de_acerto"] = self.teste_de_acerto.value
                    ataque["dano"] = self.dano.value
                    ataque["tipo_dano"] = self.tipo_dano.value
                    ataque["efeitos"] = self.efeitos.value
                    updated = True
                    break
        elif isinstance(ataques, dict):
            for key, ataque in ataques.items():
                if ataque.get("nome") == self.original_attack_name:
                    ataque["nome"] = self.nome.value
                    ataque["teste_de_acerto"] = self.teste_de_acerto.value
                    ataque["dano"] = self.dano.value
                    ataque["tipo_dano"] = self.tipo_dano.value
                    ataque["efeitos"] = self.efeitos.value
                    ataques[key] = ataque
                    updated = True
                    break

        if not updated:
            await interaction.response.send_message(
                t("attack_edit.errors.not_found", self.locale),
                ephemeral=True
            )
            return

        self.save()

        await interaction.response.send_message(
            t("attack_edit.success", self.locale, name=self.nome.value),
            ephemeral=True
        )
