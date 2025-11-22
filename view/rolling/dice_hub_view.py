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
from view.ficha_player.attack_roll_view import AttackRollView
from view.rolling.attribute_check_view import AttributeCheckView
from utils import player_utils, dice_roller
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


class DiceHubView(discord.ui.View):
    def __init__(self, user: discord.User, loc: str | None = None, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
        self.user = user
        self._loc = (loc or "pt").split("-")[0].lower()
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "player:dicehub:roll_attack":
                    item.label = _tr("player.dicehub.btn.roll_attack", self._loc, "⚔️ Rolar um Ataque")
                elif item.custom_id == "player:dicehub:roll_check":
                    item.label = _tr("player.dicehub.btn.roll_check", self._loc, "🛡️ Fazer um Teste")
                elif item.custom_id == "player:dicehub:roll_init":
                    item.label = _tr("player.dicehub.btn.roll_init", self._loc, "⚡ Rolar Iniciativa")

    @discord.ui.button(label="⚔️ Rolar um Ataque", style=discord.ButtonStyle.danger, custom_id="player:dicehub:roll_attack")
    async def roll_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        loc = resolve_locale(interaction, fallback=self._loc)

        view = AttackRollView(user=self.user)
        content = _tr(
            "player.dicehub.select_attack",
            loc,
            "Selecione um ataque da sua ficha para rolar:"
        )
        await interaction.edit_original_response(content=content, view=view)

    @discord.ui.button(label="🛡️ Fazer um Teste", style=discord.ButtonStyle.primary, custom_id="player:dicehub:roll_check")
    async def roll_check(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        loc = resolve_locale(interaction, fallback=self._loc)

        view = AttributeCheckView(user=self.user)
        content = _tr("player.dicehub.prepare_check", loc, "Prepare seu teste:")
        await interaction.edit_original_response(content=content, view=view)

    @discord.ui.button(label="⚡ Rolar Iniciativa", style=discord.ButtonStyle.success, custom_id="player:dicehub:roll_init")
    async def roll_initiative(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        loc = resolve_locale(interaction, fallback=self._loc)

        character_name = f"{self.user.id}_{self.user.name.lower()}"
        ficha = player_utils.load_player_sheet(character_name)
        iniciativa_bonus = (ficha.get("informacoes_combate", {}).get("iniciativa") or "0").strip()

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

        title = _tr("player.initiative.title", loc, "⚡ Iniciativa de {name}", name=self.user.display_name)
        details_label = _tr("player.common.details", loc, "Detalhes")

        embed = discord.Embed(
            title=title,
            description=f"## {total}",
            color=discord.Color.green()
        )
        embed.add_field(name=details_label, value=f"`{breakdown}`", inline=False)

        class InitiativeAgainView(discord.ui.View):
            def __init__(self, roll_str: str, owner_name: str, locale: str):
                super().__init__(timeout=120)
                self.roll_str = roll_str
                self.owner_name = owner_name
                self._loc = locale

            @discord.ui.button(label="🔁 Rolar novamente", style=discord.ButtonStyle.secondary, custom_id="player:init:again")
            async def again(self, inter: discord.Interaction, btn: discord.ui.Button):
                new_total, new_breakdown = await dice_roller.roll_dice(self.roll_str)
                title = _tr("player.initiative.title", self._loc, "⚡ Iniciativa de {name}", name=self.owner_name)
                details_label = _tr("player.common.details", self._loc, "Detalhes")

                new_embed = discord.Embed(
                    title=title,
                    description=f"## {new_total}",
                    color=discord.Color.green()
                )
                new_embed.add_field(name=details_label, value=f"`{new_breakdown}`", inline=False)
                await inter.response.edit_message(embed=new_embed, view=self)

        await interaction.followup.send(
            embed=embed,
            view=InitiativeAgainView(roll_string, self.user.display_name, loc)
        )
