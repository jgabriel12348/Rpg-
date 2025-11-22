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
from models.npc_modals.config_avancada.notas import NPCNotesModal
from models.npc_modals.config_avancada.aliados import NPCAddAllyModal
from models.npc_modals.config_avancada.inimigos import NPCAddEnemyModal
from models.npc_modals.config_avancada.medos import NPCAddFearModal
from models.npc_modals.config_avancada.segredos import NPCAddSecretModal
from models.npc_modals.config_avancada.extras import NPCExtrasModal
from models.npc_modals.config_avancada.dashboard import NPCRoleplayDashboardView
from utils.i18n import t as t_raw
from utils.locale_resolver import resolve_locale

def _tr(key: str, locale: str, fallback: str, **kwargs) -> str:
    """Wrapper para usar i18n.t com fallback."""
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


def resolve_loc_safe(
    interaction: discord.Interaction,
    default_locale: str = "pt",
    npc_context: NPCContext | None = None
) -> str:
    """
    Usa resolve_locale(interaction) e, se vier None ou falhar, cai para preferências do contexto ou default.
    Evita TypeError por kwargs desconhecidos.
    """
    loc = None
    try:
        loc = resolve_locale(interaction)
    except TypeError:
        loc = None
    except Exception:
        loc = None

    if loc:
        return loc

    if npc_context is not None:
        return (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or default_locale
        )
    return default_locale


class NPCConfigAvancadasView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context

        base_locale = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        self._lbl_edit_notes   = _tr("npc.adv.edit_notes", base_locale, "✏️ Editar Notas")
        self._lbl_allies       = _tr("npc.adv.allies",     base_locale, "👥 Aliados")
        self._lbl_enemies      = _tr("npc.adv.enemies",    base_locale, "🥷 Inimigos")
        self._lbl_fears        = _tr("npc.adv.fears",      base_locale, "😱 Medos/Fobias")
        self._lbl_secrets      = _tr("npc.adv.secrets",    base_locale, "🔒 Segredos")
        self._lbl_set_rel      = _tr("npc.adv.set_rel",    base_locale, "🤝 Definir Relacionamento")
        self._lbl_extras       = _tr("npc.adv.extras",     base_locale, "➕ Extras")
        self._lbl_back         = _tr("common.back",        base_locale, "🔙 Voltar")

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == "npc:adv:edit_notes":
                    item.label = self._lbl_edit_notes
                elif item.custom_id == "npc:adv:allies":
                    item.label = self._lbl_allies
                elif item.custom_id == "npc:adv:enemies":
                    item.label = self._lbl_enemies
                elif item.custom_id == "npc:adv:fears":
                    item.label = self._lbl_fears
                elif item.custom_id == "npc:adv:secrets":
                    item.label = self._lbl_secrets
                elif item.custom_id == "npc:adv:set_rel":
                    item.label = self._lbl_set_rel
                elif item.custom_id == "npc:adv:extras":
                    item.label = self._lbl_extras
                elif item.custom_id == "npc:adv:back":
                    item.label = self._lbl_back

    def format_config(self) -> str:
        base_locale = (
            getattr(self.npc_context, "user_pref", None)
            or getattr(self.npc_context, "guild_pref", None)
            or getattr(self.npc_context, "locale", None)
            or "pt"
        )
        npc_data = self.npc_context.load()
        relacionamento = npc_data.get("relacionamento", _tr("npc.adv.rel.undefined", base_locale, "Não definido"))
        lbl_rel = _tr("npc.adv.rel.label", base_locale, "Relacionamento")
        config_text = f"**{lbl_rel}:** `{relacionamento}`"
        return config_text

    @discord.ui.button(label="✏️ Editar Notas", style=discord.ButtonStyle.primary, custom_id="npc:adv:edit_notes")
    async def edit_notas(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        await interaction.response.send_modal(NPCNotesModal(self.npc_context))

    @discord.ui.button(label="👥 Aliados", style=discord.ButtonStyle.success, custom_id="npc:adv:allies")
    async def add_friends(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        loc = resolve_loc_safe(interaction, default_locale="pt", npc_context=self.npc_context)
        title = _tr("npc.adv.title.allies", loc, "Aliados")
        embed = self.create_list_embed('aliados', title, '👥', loc)
        view = NPCRoleplayDashboardView(self.npc_context, 'aliados', NPCAddAllyModal)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🥷 Inimigos", style=discord.ButtonStyle.secondary, custom_id="npc:adv:enemies")
    async def add_enemies(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        loc = resolve_loc_safe(interaction, default_locale="pt", npc_context=self.npc_context)
        title = _tr("npc.adv.title.enemies", loc, "Inimigos")
        embed = self.create_list_embed('inimigos', title, '🥷', loc)
        view = NPCRoleplayDashboardView(self.npc_context, 'inimigos', NPCAddEnemyModal)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="😱 Medos/Fobias", style=discord.ButtonStyle.danger, custom_id="npc:adv:fears")
    async def add_fear(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        loc = resolve_loc_safe(interaction, default_locale="pt", npc_context=self.npc_context)
        title = _tr("npc.adv.title.fears", loc, "Medos e Fobias")
        embed = self.create_list_embed('medos_fobias', title, '😱', loc)
        view = NPCRoleplayDashboardView(self.npc_context, 'medos_fobias', NPCAddFearModal)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🔒 Segredos", style=discord.ButtonStyle.blurple, custom_id="npc:adv:secrets")
    async def add_secret(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        loc = resolve_loc_safe(interaction, default_locale="pt", npc_context=self.npc_context)
        title = _tr("npc.adv.title.secrets", loc, "Segredos")
        embed = self.create_list_embed('segredos', title, '🔒', loc)
        view = NPCRoleplayDashboardView(self.npc_context, 'segredos', NPCAddSecretModal)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🤝 Definir Relacionamento", style=discord.ButtonStyle.success, custom_id="npc:adv:set_rel")
    async def set_relacionamento(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        loc = resolve_loc_safe(interaction, default_locale="pt", npc_context=self.npc_context)
        msg = _tr("npc.adv.rel.choose", loc, "Selecione o relacionamento do NPC com os jogadores:")
        await interaction.response.edit_message(
            content=msg,
            view=RelacionamentoSelectView(self.npc_context),
            embed=None
        )

    @discord.ui.button(label="➕ Extras", style=discord.ButtonStyle.primary, custom_id="npc:adv:extras")
    async def add_extras(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.npc_context.interaction = interaction
        await interaction.response.send_modal(NPCExtrasModal(self.npc_context))

    @discord.ui.button(label="🔙 Voltar", style=discord.ButtonStyle.secondary, custom_id="npc:adv:back")
    async def voltar(self, interaction: discord.Interaction, button: discord.ui.Button):
        from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
        self.npc_context.interaction = interaction
        view = NPCMainMenuView(self.npc_context)

        loc = resolve_loc_safe(interaction, default_locale="pt", npc_context=self.npc_context)
        content = _tr("npc.basic.editing", loc, "📜 Editando NPC: **{name}**", name=self.npc_context.npc_name)

        await interaction.response.edit_message(content=content, view=view)

    def create_list_embed(self, category: str, category_name: str, icon: str, locale: str) -> discord.Embed:
        npc_data = self.npc_context.load()
        items = npc_data.get("roleplay", {}).get(category, [])

        title_tpl = _tr(
            "npc.adv.list.title",
            locale,
            "{icon} {category} de {name}",
            icon=icon, category=category_name, name=self.npc_context.npc_name
        )
        embed = discord.Embed(title=title_tpl, color=discord.Color.blue())

        if not items:
            none_tpl = _tr("npc.adv.list.none", locale, "Nenhum(a) {cat} registrado(a).", cat=category_name.lower())
            embed.description = none_tpl
        else:
            lines = []
            for item in items:
                titulo = (
                    item.get("nome")
                    or item.get("medo")
                    or item.get("segredo")
                    or next(iter(item.values()), "—")
                )
                lines.append(f"• **{titulo}**")
            embed.description = "\n".join(lines)
        return embed


class RelacionamentoSelectView(discord.ui.View):
    def __init__(self, npc_context: NPCContext):
        super().__init__(timeout=360)
        self.npc_context = npc_context
        self.add_item(RelacionamentoSelect(npc_context))


class RelacionamentoSelect(discord.ui.Select):
    def __init__(self, npc_context: NPCContext):
        self.npc_context = npc_context

        base_locale = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        lbl_ally    = _tr("npc.adv.rel.ally",    base_locale, "Aliado")
        lbl_neutral = _tr("npc.adv.rel.neutral", base_locale, "Neutro")
        lbl_hostile = _tr("npc.adv.rel.hostile", base_locale, "Hostil")
        desc_ally    = _tr("npc.adv.rel.ally.desc",    base_locale, "O NPC é amigável com os jogadores.")
        desc_neutral = _tr("npc.adv.rel.neutral.desc", base_locale, "O NPC é indiferente ou reage com base nas ações.")
        desc_hostile = _tr("npc.adv.rel.hostile.desc", base_locale, "O NPC é ativamente contra os jogadores.")

        options = [
            discord.SelectOption(label=lbl_ally,    value="Aliado", description=desc_ally),
            discord.SelectOption(label=lbl_neutral, value="Neutro", description=desc_neutral),
            discord.SelectOption(label=lbl_hostile, value="Hostil", description=desc_hostile),
        ]

        npc_data = self.npc_context.load()
        current_rel = npc_data.get("relacionamento")
        if current_rel:
            for option in options:
                if option.value == current_rel:
                    option.default = True
                    break

        placeholder = _tr("npc.adv.rel.placeholder", base_locale, "Selecione o relacionamento...")
        super().__init__(placeholder=placeholder, options=options, custom_id="npc:adv:rel:select")

    async def callback(self, interaction: discord.Interaction):
        npc_data = self.npc_context.load()
        npc_data["relacionamento"] = self.values[0]
        self.npc_context.save(npc_data)
        self.npc_context.interaction = interaction
        loc = resolve_loc_safe(interaction, default_locale="pt", npc_context=self.npc_context)

        view = NPCConfigAvancadasView(self.npc_context)
        header = _tr("npc.adv.header", loc, "⚙️ Configurações Avançadas:")
        await interaction.response.edit_message(
            content=f"{header}\n\n" + view.format_config(),
            view=view
        )
