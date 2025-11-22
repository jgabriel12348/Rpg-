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
from models.npc_modals.itens.dashboard import NPCItemDashboardView
from models.npc_modals.itens.combat import NPCAddItemCombatModal
from models.npc_modals.itens.defesa import NPCAddItemDefenseModal
from models.npc_modals.itens.consumivel import NPCAddItemConsumableModal
from models.npc_modals.itens.aleatorio import NPCAddItemRandomModal
from models.npc_modals.itens.carteira import NPCWalletModal
from view.ficha_npc.npc_remove_item_view import NPCRemoveItemView
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
    """
    Wrapper para usar i18n.t com fallback.
    Se a chave não existir (t retorna a própria key), usa o fallback informado.
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


class NPCInventoryView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context
        base_locale = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        self._lbl_tab_combat     = _tr("npc.inv.tabs.combat",     base_locale, "⚔️ Combate")
        self._lbl_tab_defense    = _tr("npc.inv.tabs.defense",    base_locale, "🛡️ Defesa")
        self._lbl_tab_consumable = _tr("npc.inv.tabs.consumable", base_locale, "🍷 Consumível")
        self._lbl_tab_random     = _tr("npc.inv.tabs.random",     base_locale, "🎒 Aleatório")
        self._lbl_wallet         = _tr("npc.inv.wallet",          base_locale, "💰 Carteira")
        self._lbl_remove         = _tr("npc.inv.remove_item",     base_locale, "➖ Remover Item")
        self._lbl_back           = _tr("common.back",             base_locale, "🔙 Voltar")

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "npc:inv:combat":
                    item.label = self._lbl_tab_combat
                elif item.custom_id == "npc:inv:defense":
                    item.label = self._lbl_tab_defense
                elif item.custom_id == "npc:inv:consumable":
                    item.label = self._lbl_tab_consumable
                elif item.custom_id == "npc:inv:random":
                    item.label = self._lbl_tab_random
                elif item.custom_id == "npc:inv:wallet":
                    item.label = self._lbl_wallet
                elif item.custom_id == "npc:inv:remove":
                    item.label = self._lbl_remove
                elif item.custom_id == "npc:inv:back":
                    item.label = self._lbl_back

    def _create_item_list_embed(self, category: str, category_name: str, icon: str, locale: str | None = None) -> discord.Embed:
        loc = locale or (
            getattr(self.npc_context, "user_pref", None)
            or getattr(self.npc_context, "guild_pref", None)
            or getattr(self.npc_context, "locale", None)
            or "pt"
        )
        npc_data = self.npc_context.load()
        items = npc_data.get("inventario", {}).get(category, [])

        title_tpl = _tr(
            "npc.inv.list.title", loc, "{icon} Itens de {category} de {name}",
            icon=icon, category=category_name, name=self.npc_context.npc_name
        )
        embed = discord.Embed(title=title_tpl, color=discord.Color.dark_gold())

        if not items:
            embed.description = _tr("npc.inv.list.none", loc, "Nenhum item desta categoria no inventário.")
        else:
            description = ""
            for item in items:
                description += f"**{item['nome']}** (x{item.get('quantidade', 1)})\n"
            embed.description = description
        return embed

    @discord.ui.button(label="npc.inv.tabs.combat", style=discord.ButtonStyle.danger, custom_id="npc:inv:combat")
    async def combat_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction)
        cat_display = _tr("npc.inv.cat.combat", loc, "Combate")
        embed = self._create_item_list_embed('combate', cat_display, '⚔️', loc)
        view = NPCItemDashboardView(self.npc_context, 'combate', cat_display, NPCAddItemCombatModal)
        await interaction.response.edit_message(embed=embed, view=view, content=None)

    @discord.ui.button(label="npc.inv.tabs.defense", style=discord.ButtonStyle.blurple, custom_id="npc:inv:defense")
    async def defense_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction)
        cat_display = _tr("npc.inv.cat.defense", loc, "Defesa")
        embed = self._create_item_list_embed('defesa', cat_display, '🛡️', loc)
        view = NPCItemDashboardView(self.npc_context, 'defesa', cat_display, NPCAddItemDefenseModal)
        await interaction.response.edit_message(embed=embed, view=view, content=None)

    @discord.ui.button(label="npc.inv.tabs.consumable", style=discord.ButtonStyle.secondary, custom_id="npc:inv:consumable")
    async def consumable_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction)
        cat_display = _tr("npc.inv.cat.consumable", loc, "Consumíveis")
        embed = self._create_item_list_embed('consumivel', cat_display, '🍷', loc)
        view = NPCItemDashboardView(self.npc_context, 'consumivel', cat_display, NPCAddItemConsumableModal)
        await interaction.response.edit_message(embed=embed, view=view, content=None)

    @discord.ui.button(label="npc.inv.tabs.random", style=discord.ButtonStyle.gray, custom_id="npc:inv:random")
    async def random_dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        loc = resolve_locale(interaction)
        cat_display = _tr("npc.inv.cat.random", loc, "Itens Aleatórios")
        embed = self._create_item_list_embed('aleatorio', cat_display, '🎒', loc)
        view = NPCItemDashboardView(self.npc_context, 'aleatorio', cat_display, NPCAddItemRandomModal)
        await interaction.response.edit_message(embed=embed, view=view, content=None)

    @discord.ui.button(label="npc.inv.wallet", style=discord.ButtonStyle.success, custom_id="npc:inv:wallet")
    async def wallet_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NPCWalletModal(self.npc_context, interaction))

    @discord.ui.button(label="npc.inv.remove_item", style=discord.ButtonStyle.danger, custom_id="npc:inv:remove")
    async def remove_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.npc_context.mestre_id:
            loc = resolve_locale(interaction)
            msg = _tr("npc.inv.only_gm", loc, "Apenas o mestre deste NPC pode interagir aqui.")
            return await interaction.response.send_message(msg, ephemeral=True)

        view = NPCRemoveItemView(npc_context=self.npc_context)

        loc = resolve_locale(interaction)
        content = _tr(
            "npc.inv.remove.prompt",
            loc,
            "Selecione um ou mais itens para remover da ficha de **{name}**:",
            name=self.npc_context.npc_name
        )

        await interaction.response.edit_message(
            content=content,
            view=view,
            embed=None
        )

    @discord.ui.button(label="common.back", style=discord.ButtonStyle.danger, custom_id="npc:inv:back")
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        view = NPCMainMenuView(self.npc_context)

        loc = resolve_locale(interaction)
        content = _tr("npc.basic.editing", loc, "📜 Editando NPC: **{name}**", name=self.npc_context.npc_name)

        await interaction.response.edit_message(
            content=content,
            view=view
        )
