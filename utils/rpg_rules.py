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
SUPPORTED_SYSTEMS = {
    "dnd": "Dungeons & Dragons / T20",
    "ordem_paranormal": "Ordem Paranormal",
    "cyberpunk": "Cyberpunk",
    "skyfall": "SkiFall RPG",
    "vampiro": "Vampiro: A Máscara",
    "cthulhu": "Call of Cthulhu"
}

def calculate_modifier(score: int) -> int:
    return (score - 10) // 2

MODIFIER_RULES = {
    "dnd": calculate_modifier,
    "skyfall": calculate_modifier,
    "ordem_paranormal": lambda score: score,
    "cyberpunk": lambda score: score,
    "vampiro": lambda score: score,
    "cthulhu": lambda score: 0,
}

def get_modifier(system_name: str, attribute_score: int) -> int:
    system_key = system_name.lower().strip().replace(" ", "_") if system_name else "dnd"
    calculation_function = MODIFIER_RULES.get(system_key, MODIFIER_RULES["dnd"])
    try:
        score = int(attribute_score)
        return calculation_function(score)
    except (ValueError, TypeError):
        return 0
SYSTEM_CHECKS = {
    "dnd": ["Força", "Destreza", "Constituição", "Inteligência", "Sabedoria", "Carisma"],
    "skyfall": ["Força", "Destreza", "Vigor", "Intelecto", "Percepção", "Vontade"],
    "ordem_paranormal": ["Força", "Agilidade", "Vigor", "Presença", "Intelecto"],
    "cyberpunk": ["Inteligência", "Reflexos", "Técnica", "Empatia", "Frio", "Corpo", "Atratividade", "Sorte"],
    "vampiro": ["Força", "Destreza", "Vigor", "Carisma", "Manipulação", "Autocontrole", "Inteligência", "Raciocínio", "Perseverança"],
    "cthulhu": ["Força", "Destreza", "Constituição", "Inteligência", "Poder", "Educação", "Tamanho", "Aparência"]
}

def get_system_checks(system_name: str) -> list[str]:
    system_key = system_name.lower().strip().replace(" ", "_") if system_name else "dnd"
    return SYSTEM_CHECKS.get(system_key, SYSTEM_CHECKS["dnd"])
SYSTEM_SKILLS = {
    "dnd": {
        "Força": ["Atletismo"],
        "Destreza": ["Acrobacia", "Furtividade", "Prestidigitação"],
        "Inteligência": ["Arcanismo", "História", "Investigação", "Natureza", "Religião"],
        "Sabedoria": ["Intuição", "Lidar com Animais", "Medicina", "Percepção", "Sobrevivência"],
        "Carisma": ["Atuação", "Enganação", "Intimidação", "Persuasão"]
    },
    "ordem_paranormal": {
        "Agilidade": [
            "Acrobacia", "Crime", "Furtividade", "Iniciativa", "Pilotagem", "Pontaria", "Reflexos"],
        "Força": ["Atletismo", "Luta"],
        "Intelecto": [
            "Atualidades", "Ciências", "Investigação", "Medicina", "Ocultismo",
            "Percepção", "Profissão", "Sobrevivência", "Tática", "Tecnologia"],
        "Presença": [
            "Adestramento", "Artes", "Diplomacia", "Enganação", "Intimidação",
            "Intuição", "Liderança", "Religião", "Vontade"],
        "Vigor": ["Fortitude"]
    },
    "cthulhu": {
        "Força": ["Intimidação", "Luta", "Natação", "Saltar"],
        "Destreza": [
            "Arcos", "Arremessar", "Artes/Ofícios", "Chaveiro", "Consertos Elétricos",
            "Consertos Mecânicos", "Furtividade", "Operar Maquinário", "Pilotar"],
        "Educação": ["Antropologia", "Arqueologia", "Ciências", "Contabilidade",
                     "Direito", "História", "Língua Nativa", "Língua Outra", "Medicina",
                     "Mitos de Cthulhu", "Mundo Natural", "Ocultismo", "Primeiros Socorros", "Psicanálise"],
        "Poder": ["Encontrar", "Escutar", "Psicologia"],
        "Aparência": ["Charme", "Disfarce", "Lábia", "Persuasão"],
        "Inteligência": ["Avaliação", "Rastrear"]
    },
     "vampiro": {
        "Força": ["Atletismo", "Briga", "Armas Brancas"],
        "Destreza": ["Ofícios", "Condução", "Larcínia", "Furtividade"],
        "Autocontrole": ["Armas de Fogo", "Etiqueta", "Intuição"],
        "Raciocínio": ["Sobrevivência", "Consciência"],
        "Carisma": ["Trato com Animais", "Liderança", "Performance", "Persuasão"],
        "Manipulação": ["Intimidação", "Manha", "Lábia", "Política"],
        "Inteligência": ["Erudição", "Finanças", "Investigação", "Medicina", "Ocultismo", "Ciência", "Tecnologia"]
    },
    "cyberpunk": {
        "Vontade": ["Concentração", "Resistência"],
        "Inteligência": ["Acadêmicos", "Burocracia", "Criptografia", "Línguas", "Percepção"],
        "Reflexos": ["Condução (Terrestre)", "Pistolas", "Fuzis", "Armas Pesadas"],
        "Destreza": ["Atletismo", "Briga", "Evasão", "Armas Brancas (Corpo a Corpo)", "Furtividade"],
        "Frio": ["Atuação", "Suborno", "Interrogatório", "Persuasão", "Comércio"],
        "Empatia": ["Conversação", "Percepção Humana"],
        "Técnica": ["Cybertecnia", "Primeiros Socorros", "Eletrônica/Segurança", "Fabricação de Armas"]
    },
    "skyfall": {
        "Força": ["Luta"],
        "Destreza": ["Pontaria", "Reflexos", "Furtividade", "Ladinagem"],
        "Vigor": ["Fortitude"],
        "Percepção": ["Iniciativa", "Intuição", "Investigar", "Percepção", "Sobrevivência"],
        "Vontade": ["Vontade", "Intimidação", "Misticismo"],
        "Intelecto": ["Conhecimento", "Cura", "Diplomacia", "Enganação", "Magia", "Nobreza", "Ofícios"]
    }
}

def get_system_skills(system_name: str) -> dict:
    system_key = system_name.lower().strip().replace(" ", "_") if system_name else "dnd"
    return SYSTEM_SKILLS.get(system_key, SYSTEM_SKILLS["dnd"])