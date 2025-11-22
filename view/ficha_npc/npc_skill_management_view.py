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

import re
import discord
from utils import npc_utils, rpg_rules
from models.npc_modals.info_combate.npc_skill_edit_modal import NPCSkillEditModal
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


def resolve_loc_safe(
    interaction: discord.Interaction,
    default_locale: str = "pt",
    npc_context: npc_utils.NPCContext | None = None
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


class NPCSkillManagementView(discord.ui.View):
    def __init__(self, npc_context: npc_utils.NPCContext):
        super().__init__(timeout=None)
        self.npc_context = npc_context
        # Locale base (não temos interaction aqui)
        self._loc = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )
        self.add_item(self.SkillActionSelect(npc_context=self.npc_context, locale=self._loc))
        self.add_item(self.BackButton(npc_context=self.npc_context, locale=self._loc))

    def create_embed(self) -> discord.Embed:
        npc_data = self.npc_context.load()
        pericias = npc_data.get("pericias", {})

        title = _tr("npc.skills.title", self._loc, "💡 Perícias de {name}", name=self.npc_context.npc_name)
        embed = discord.Embed(title=title, color=discord.Color.dark_green())

        if not pericias:
            embed.description = _tr(
                "npc.skills.empty.short",
                self._loc,
                "Este NPC não possui perícias. Use o menu para adicionar."
            )
        else:
            description = ""
            for nome, dados in pericias.items():
                if isinstance(dados, dict):
                    bonus = dados.get('bonus', 0)
                    sinal = "+" if bonus >= 0 else ""
                    description += f"• **{nome}** (`{dados.get('atributo_base', 'N/A')}` {sinal}{bonus})\n"
                else:
                    description += f"• **{nome}** (`{dados}`)\n"
            embed.description = description
        return embed

    class SkillActionSelect(discord.ui.Select):
        def __init__(self, npc_context: npc_utils.NPCContext, locale: str = "pt"):
            self.npc_context = npc_context
            self._loc = locale

            npc_data = self.npc_context.load()
            pericias = npc_data.get("pericias", {})

            opt_add = _tr("npc.skills.select.add", self._loc, "➕ Adicionar Nova Perícia")
            opt_remove = _tr("npc.skills.select.remove", self._loc, "➖ Remover Perícias")
            opt_edit_fmt = _tr("npc.skills.select.edit", self._loc, "✏️ Editar: {name}", name="{name}")
            placeholder = _tr("npc.skills.select.ph.short", self._loc, "Escolha uma ação...")

            options = [discord.SelectOption(label=opt_add, value="CREATE_NEW")]
            if pericias:
                options.append(discord.SelectOption(label=opt_remove, value="REMOVE_SKILLS", emoji="🗑️"))
                options.extend([
                    discord.SelectOption(label=opt_edit_fmt.format(name=nome), value=nome)
                    for nome in pericias.keys()
                ])

            super().__init__(placeholder=placeholder, options=options, custom_id="npc:skills:action")

        async def callback(self, interaction: discord.Interaction):
            self.npc_context.interaction = interaction

            loc = resolve_loc_safe(interaction, default_locale=self._loc, npc_context=self.npc_context)
            selection = self.values[0]

            if selection == "CREATE_NEW":
                await interaction.response.send_modal(
                    NPCSkillEditModal(self.npc_context, interaction=interaction)
                )
            elif selection == "REMOVE_SKILLS":
                view = NPCRemoveSkillView(npc_context=self.npc_context, locale=loc)
                content = _tr(
                    "npc.skills.remove.prompt",
                    loc,
                    "Selecione as perícias do NPC para remover:"
                )
                await interaction.response.edit_message(content=content, embed=None, view=view)
            else:
                await interaction.response.send_modal(
                    NPCSkillEditModal(self.npc_context, interaction=interaction, skill_name=selection)
                )

    class BackButton(discord.ui.Button):
        def __init__(self, npc_context: npc_utils.NPCContext, locale: str = "pt"):
            self.npc_context = npc_context
            self._loc = locale
            label = _tr("common.back", locale, "🔙 Voltar")
            super().__init__(label=label, style=discord.ButtonStyle.danger, row=1, custom_id="npc:skills:back")

        async def callback(self, interaction: discord.Interaction):
            from view.ficha_npc.npc_main_menu_view import NPCMainMenuView
            self.npc_context.interaction = interaction

            view = NPCMainMenuView(npc_context=self.npc_context)
            loc = resolve_loc_safe(interaction, default_locale=self._loc, npc_context=self.npc_context)
            content = _tr("npc.basic.editing", loc, "📜 Editando NPC: **{name}**", name=self.npc_context.npc_name)

            await interaction.response.edit_message(content=content, view=view, embed=None)


class NPCAttributeLinkView(discord.ui.View):
    def __init__(self, npc_context: npc_utils.NPCContext, skill_name: str, skill_bonus: int):
        super().__init__(timeout=180)
        self.npc_context = npc_context
        self.skill_name = skill_name
        self.skill_bonus = skill_bonus

        # Locale base
        self._loc = (
            getattr(npc_context, "user_pref", None)
            or getattr(npc_context, "guild_pref", None)
            or getattr(npc_context, "locale", None)
            or "pt"
        )

        npc_data = self.npc_context.load()
        sistema = npc_data.get("informacoes_basicas", {}).get("sistema_rpg", "dnd")
        atributos = rpg_rules.get_system_checks(sistema)
        self.add_item(self.AttributeSelect(atributos, locale=self._loc))

    class AttributeSelect(discord.ui.Select):
        def __init__(self, atributos: list, locale: str = "pt"):
            self._loc = locale
            options = [discord.SelectOption(label=attr) for attr in atributos]
            placeholder = _tr("npc.skills.attr.ph", self._loc, "Selecione o atributo base...")
            super().__init__(placeholder=placeholder, options=options, custom_id="npc:skills:attr_select")

        async def callback(self, interaction: discord.Interaction):
            selected_attribute = self.values[0]
            npc_data = self.view.npc_context.load()
            pericias = npc_data.setdefault("pericias", {})
            pericias[self.view.skill_name] = {"atributo_base": selected_attribute, "bonus": self.view.skill_bonus}
            self.view.npc_context.save(npc_data)

            # Mensagem de sucesso traduzida (assinatura correta)
            loc = resolve_loc_safe(interaction, default_locale=self._loc, npc_context=self.view.npc_context)
            success = _tr(
                "npc.skills.save.success",
                loc,
                "✅ Perícia **{skill}** salva para **{name}**!",
                skill=self.view.skill_name,
                name=self.view.npc_context.npc_name
            )

            view = NPCSkillManagementView(npc_context=self.view.npc_context)
            embed = view.create_embed()
            await interaction.response.edit_message(content=success, embed=embed, view=view)


class NPCRemoveSkillView(discord.ui.View):
    def __init__(self, npc_context: npc_utils.NPCContext, locale: str = "pt"):
        super().__init__(timeout=180)
        self.npc_context = npc_context
        self._loc = locale

        npc_data = self.npc_context.load()
        pericias = npc_data.get("pericias", {})
        if pericias:
            self.add_item(self.SkillRemoveSelect(list(pericias.keys()), locale=self._loc))
            self.add_item(self.ConfirmRemoveButton(locale=self._loc))
        self.add_item(self.CancelButton(npc_context, locale=self._loc))

    class SkillRemoveSelect(discord.ui.Select):
        def __init__(self, skills: list, locale: str = "pt"):
            self._loc = locale
            placeholder = _tr("npc.skills.remove.select.ph", self._loc, "Selecione as perícias para remover...")
            options = [discord.SelectOption(label=skill) for skill in skills]
            super().__init__(placeholder=placeholder, min_values=1, max_values=len(skills),
                             options=options, custom_id="npc:skills:remove_select")

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()

    class ConfirmRemoveButton(discord.ui.Button):
        def __init__(self, locale: str = "pt"):
            self._loc = locale
            label = _tr("npc.skills.remove.confirm", self._loc, "Confirmar Remoção")
            super().__init__(label=label, style=discord.ButtonStyle.danger, row=1,
                             custom_id="npc:skills:remove_confirm")

        async def callback(self, interaction: discord.Interaction):
            skills_to_remove = self.view.children[0].values
            npc_data = self.view.npc_context.load()
            for skill in skills_to_remove:
                npc_data["pericias"].pop(skill, None)
            self.view.npc_context.save(npc_data)

            view = NPCSkillManagementView(npc_context=self.view.npc_context)
            new_embed = view.create_embed()

            loc = resolve_loc_safe(interaction, default_locale=self._loc, npc_context=self.view.npc_context)
            msg = _tr(
                "npc.skills.remove.done",
                loc,
                "✅ Perícia(s) removida(s) de **{name}**!",
                name=self.view.npc_context.npc_name
            )

            await interaction.response.edit_message(content=msg, embed=new_embed, view=view)

    class CancelButton(discord.ui.Button):
        def __init__(self, npc_context: npc_utils.NPCContext, locale: str = "pt"):
            self.npc_context = npc_context
            self._loc = locale
            label = _tr("common.cancel", self._loc, "Cancelar")
            super().__init__(label=label, style=discord.ButtonStyle.secondary, row=1,
                             custom_id="npc:skills:remove_cancel")

        async def callback(self, interaction: discord.Interaction):
            view = NPCSkillManagementView(npc_context=self.npc_context)
            embed = view.create_embed()
            await interaction.response.edit_message(content=None, embed=embed, view=view)
