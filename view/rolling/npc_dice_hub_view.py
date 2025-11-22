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
import re
from utils.npc_utils import NPCContext
from view.rolling.npc_attack_roll_view import NPCAttackRollView
from view.rolling.npc_attribute_check_view import NPCAttributeCheckView
from models.shared_models.simple_roll_modal import SimpleRollModal
from utils import dice_roller
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


class NPCDiceHubView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context

        self._loc = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "npc:dicehub:roll_attack":
                    item.label = _tr("npc.dicehub.btn.roll_attack", self._loc, "⚔️ Rolar um Ataque de NPC")
                elif item.custom_id == "npc:dicehub:roll_check":
                    item.label = _tr("npc.dicehub.btn.roll_check", self._loc, "🛡️ Fazer um Teste de NPC")
                elif item.custom_id == "npc:dicehub:roll_init":
                    item.label = _tr("npc.dicehub.btn.roll_init", self._loc, "⚡ Rolar Iniciativa")

    @discord.ui.button(label="npc.dicehub.btn.roll_attack", style=discord.ButtonStyle.danger, custom_id="npc:dicehub:roll_attack")
    async def roll_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        npc_data = self.npc_context.load()
        ataques = npc_data.get("ataques", [])
        loc = resolve_locale(interaction, fallback=self._loc)

        if not ataques:
            msg = _tr(
                "npc.dicehub.no_attacks",
                loc,
                "❌ O NPC **{name}** não possui ataques registrados na ficha.",
                name=self.npc_context.npc_name
            )
            await interaction.response.send_message(msg, ephemeral=True)
            return

        view = NPCAttackRollView(npc_context=self.npc_context)
        content = _tr(
            "npc.dicehub.select_attack",
            loc,
            "Selecione um ataque de **{name}**:",
            name=self.npc_context.npc_name
        )
        await interaction.response.edit_message(content=content, view=view)

    @discord.ui.button(label="npc.dicehub.btn.roll_check", style=discord.ButtonStyle.primary, custom_id="npc:dicehub:roll_check")
    async def roll_check(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = NPCAttributeCheckView(npc_context=self.npc_context)
        loc = resolve_locale(interaction, fallback=self._loc)
        content = _tr(
            "npc.dicehub.prepare_check",
            loc,
            "Prepare o teste para **{name}**:",
            name=self.npc_context.npc_name
        )
        await interaction.response.edit_message(content=content, view=view)

    @discord.ui.button(label="npc.dicehub.btn.roll_init", style=discord.ButtonStyle.success, custom_id="npc:dicehub:roll_init")
    async def roll_initiative(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

        loc = resolve_locale(interaction, fallback=self._loc)

        npc_data = self.npc_context.load()
        iniciativa_bonus = (npc_data.get("informacoes_combate", {}).get("iniciativa") or "0").strip()

        def _norm_bonus(expr: str) -> str:
            if not expr:
                return "0"
            expr = re.sub(r'(^|[^0-9a-zA-Z_])d(\d+)', r'\g<1>1d\2', expr.strip())
            return expr

        def _build_roll_string(bonus_raw: str) -> str:
            b = _norm_bonus(bonus_raw)
            suffix = f" {b}" if b.startswith(('+', '-')) else f" + {b}"
            return f"1d20{suffix}"

        roll_string = _build_roll_string(iniciativa_bonus)
        total, breakdown = await dice_roller.roll_dice(roll_string)

        title = _tr("npc.initiative.title", loc, "⚡ Iniciativa de {name}", name=self.npc_context.npc_name)
        details_label = _tr("npc.common.details", loc, "Detalhes")
        rolled_by = _tr("npc.attack.rolled_by", loc, "Rolado por {user}", user=interaction.user.display_name)

        embed = discord.Embed(
            title=title,
            description=f"## {total}",
            color=discord.Color.dark_green()
        )
        embed.add_field(name=details_label, value=f"`{breakdown}`", inline=False)
        embed.set_author(name=rolled_by, icon_url=interaction.user.display_avatar.url)

        class NPCInitiativeAgainView(discord.ui.View):
            def __init__(self, roll_str: str, npc_name: str, locale: str):
                super().__init__(timeout=120)
                self.roll_str = roll_str
                self.npc_name = npc_name
                self._loc = locale

            @discord.ui.button(label="🔁 Rolar novamente", style=discord.ButtonStyle.secondary, custom_id="npc:init:again")
            async def again(self, inter: discord.Interaction, btn: discord.ui.Button):
                new_total, new_breakdown = await dice_roller.roll_dice(self.roll_str)
                title = _tr("npc.initiative.title", self._loc, "⚡ Iniciativa de {name}", name=self.npc_name)
                details_label = _tr("npc.common.details", self._loc, "Detalhes")
                rolled_by = _tr("npc.attack.rolled_by", self._loc, "Rolado por {user}", user=inter.user.display_name)

                new_embed = discord.Embed(
                    title=title,
                    description=f"## {new_total}",
                    color=discord.Color.dark_green()
                )
                new_embed.add_field(name=details_label, value=f"`{new_breakdown}`", inline=False)
                new_embed.set_author(name=rolled_by, icon_url=inter.user.display_avatar.url)
                await inter.response.edit_message(embed=new_embed, view=self)

        await interaction.followup.send(
            embed=embed,
            view=NPCInitiativeAgainView(roll_string, self.npc_context.npc_name, loc)
        )
