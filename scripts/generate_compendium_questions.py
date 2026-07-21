#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera una primera tanda determinista de preguntas desde los compendios Markdown.

Las preguntas se construyen únicamente con afirmaciones, conceptos, listas y secuencias
presentes en las fuentes. La salida se guarda por asignatura en
`Procesado/<asignatura>/preguntas_compendios.md` y puede convertirse con
`scripts/convert_banks.py`.
"""

from __future__ import annotations

import random
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "Procesado"
RNG = random.Random(20260720)


SUBJECTS = {
    "DER101": {
        "name": "Introducción al Derecho",
        "folder": "DER 101 - Introducción al Derecho",
        "sources": ["texto_extraido_derecho_unemi.md", "introduccion_al_derecho_texto_completo.md"],
        "start": 30,
        "quota": {"selection": 80, "ordering": 6, "matching": 10},
    },
    "DER102": {
        "name": "Lógica y Dialéctica Jurídica",
        "folder": "DER 102 - Lógica y Dialéctica Jurídica",
        "sources": ["logica_y_dialectica_juridica_UNEMI_COMPLETO.md"],
        "start": 21,
        "quota": {"selection": 70, "ordering": 5, "matching": 10},
    },
    "DER104": {
        "name": "Teoría General del Estado y Sociología Jurídica",
        "folder": "DER 104 - Teoría General del Estado y Sociología Jurídica",
        "sources": ["Teoria_general_del_estado_texto_completo.md"],
        "start": 31,
        "quota": {"selection": 75, "ordering": 8, "matching": 12},
    },
    "DER105": {
        "name": "Expresión Oral y Redacción Jurídica",
        "folder": "DER 105 - Expresión Oral y Redacción Jurídica",
        "sources": ["contenido_texto_juridico.md"],
        "start": 96,
        "quota": {"selection": 35, "ordering": 4, "matching": 8},
    },
    "DER106": {
        "name": "Historia y Filosofía del Derecho",
        "folder": "DER 106 - Historia y Filosofía del Derecho",
        "sources": ["# Historia y Filosofía del Derecho.md"],
        "start": 34,
        "quota": {"selection": 95, "ordering": 10, "matching": 15},
    },
    "C10": {
        "name": "Investigación",
        "folder": "C10 - Investigación",
        "sources": ["# Metodología de la Investigación.md"],
        "start": 141,
        "quota": {"selection": 55, "ordering": 8, "matching": 12},
    },
}


# Secuencias verificables descritas en los compendios. `semantic=False` indica
# que se evalúa expresamente el orden expositivo de la fuente, no una relación
# cronológica o causal inexistente.
CURATED_SEQUENCES = {
    "DER101": [
        ("Proceso de formación de leyes en Ecuador", ["Iniciativa legislativa", "Calificación por el CAL", "Primer debate", "Segundo debate", "Sanción u objeción del Ejecutivo", "Publicación en el Registro Oficial"], True),
        ("Fases del proceso de creación de normas", ["Elaboración", "Consulta", "Aprobación", "Publicación"], True),
        ("Jerarquía normativa ecuatoriana", ["Constitución", "Tratados y convenios internacionales", "Leyes orgánicas", "Leyes ordinarias", "Normas regionales y ordenanzas distritales", "Decretos y reglamentos"], True),
        ("Elementos de la norma jurídica", ["Sujeto jurídico", "Objeto jurídico", "Relación jurídica", "Consecuencia jurídica", "Valores o fines jurídicos"], False),
        ("Elementos del sistema jurídico", ["Normas", "Instituciones", "Procedimientos", "Actores"], False),
        ("Clasificación general de las fuentes del Derecho", ["Fuentes formales", "Fuentes materiales o reales", "Fuentes históricas"], False),
    ],
    "DER102": [
        ("Estructura del silogismo jurídico", ["Premisa mayor: norma jurídica", "Premisa menor: hechos probados", "Conclusión: consecuencia jurídica"], True),
        ("Juicio de proporcionalidad", ["Idoneidad", "Necesidad", "Proporcionalidad en sentido estricto"], True),
        ("Contenido mínimo de la motivación", ["Identificación del problema jurídico", "Determinación de los hechos relevantes", "Selección de las normas aplicables", "Justificación de la interpretación", "Vinculación entre hechos, normas y principios"], True),
        ("Análisis de un argumento jurídico", ["Identificar la conclusión", "Reconocer las premisas", "Comprobar la relación lógica", "Examinar la justificación material"], True),
        ("Movimiento dialéctico", ["Tesis", "Antítesis", "Síntesis"], True),
    ],
    "DER104": [
        ("Formación histórica del Estado", ["Feudalismo", "Estado absolutista", "Nacimiento del Estado moderno"], True),
        ("Estado en América Latina", ["Proceso de formación y evolución", "Crisis y reformas del Estado", "La Colonia", "Lucha por la independencia"], False),
        ("Organización administrativa y territorial", ["Neoconstitucionalismo", "Centralización y descentralización", "Competencias y órganos", "Desconcentración"], False),
        ("Relación entre Estado y Constitución", ["El Estado y la Constitución", "Importancia de la Constitución", "Neoconstitucionalismo", "Estado de Derecho"], False),
        ("Globalización y Estado", ["Efectos de la globalización", "Crisis y desarticulación del Estado", "Poder público", "Poder privado"], False),
        ("Sociología jurídica", ["Concepto, objeto y finalidades", "Métodos sociológicos", "Positivismo jurídico", "Clásicos de la sociología"], False),
        ("Cambio social y política pública", ["Control social y normas sociales", "Grupos de presión y fuerzas sociales", "Relaciones entre política y sociedad", "Problemas sociales"], False),
        ("Ciclo de una política pública", ["Identificación del problema", "Formulación de alternativas", "Decisión", "Implementación", "Evaluación"], True),
    ],
    "DER105": [
        ("Estructura lógica de la frase jurídica", ["Quién", "Verbo", "Qué", "A quién"], True),
        ("Cálculo del índice de nebulosidad", ["Dividir el total de palabras entre el número de frases", "Sumar el porcentaje de palabras largas", "Multiplicar el resultado por 0,4"], True),
        ("Normas y procedimientos de redacción jurídica", ["Precisión léxica", "Control de falsas sinonimias", "Uso de paréntesis y corchetes", "Uso de la raya"], False),
        ("Gramática en documentos jurídicos", ["Coma vocativa", "Coma elíptica", "Punto y coma", "Género del sustantivo"], False),
    ],
    "DER106": [
        ("Acuerdos ibéricos sobre los territorios ultramarinos", ["Bula Unam Sanctam (1302)", "Tratado de Alcáçovas-Toledo (1479)", "Bula Inter Caetera (1493)", "Tratado de Tordesillas (1494)", "Tratado de Zaragoza (1526)"], True),
        ("Viajes colombinos y acuerdos posteriores", ["Llegada de Colón a América (1492)", "Bula Inter Caetera (1493)", "Tratado de Tordesillas (1494)", "Ratificación papal (1506)", "Tratado de Zaragoza (1526)"], True),
        ("Ciclos económicos del Brasil colonial", ["Ciclo del Azúcar", "Ciclo del Oro"], True),
        ("Generaciones de derechos humanos", ["Primera generación", "Segunda generación", "Tercera generación", "Cuarta generación"], True),
        ("Proceso de formación de normas jurídicas", ["Etapa prelegislativa", "Etapa legislativa", "Etapa postlegislativa"], True),
        ("Historia de la codificación y el constitucionalismo", ["Derecho en la modernidad", "Código y codificación", "Constitución y constitucionalismo", "Evolución constitucional", "Escuela Histórica del Derecho"], False),
        ("Principales escuelas jurídicas", ["Iusnaturalismo", "Iusracionalismo", "Contractualismo", "Positivismo"], False),
        ("Corrientes de la filosofía del Derecho", ["Iusnaturalismo moderno", "Sociología jurídica", "Corrientes contemporáneas"], False),
        ("Estructura de la ley romana", ["Praescriptio", "Rogatio", "Sanctio"], False),
        ("Proceso legislativo", ["Identificación de la necesidad normativa", "Preparación del proyecto", "Debate y aprobación", "Sanción", "Promulgación y publicación"], True),
    ],
    "C10": [
        ("Método histórico-lógico", ["Identificación del problema histórico", "Recolección de información", "Formulación de una hipótesis", "Organización y verificación de evidencias", "Análisis de evidencias", "Registro de conclusiones"], True),
        ("Método analítico-sintético", ["Observación", "Descripción", "Descomposición", "Enumeración", "Ordenación", "Clasificación y síntesis"], True),
        ("Selección de una muestra", ["Definir la población", "Establecer criterios de inclusión y exclusión", "Elegir el tipo de muestreo", "Calcular el tamaño de la muestra", "Seleccionar las unidades"], True),
        ("Construcción de instrumentos", ["Definir las variables", "Determinar dimensiones e indicadores", "Redactar los ítems", "Validar el instrumento", "Aplicar una prueba piloto"], True),
        ("Proceso de investigación cuantitativa", ["Plantear el problema", "Revisar la literatura", "Formular hipótesis", "Diseñar la investigación", "Recolectar y analizar datos", "Comunicar resultados"], True),
        ("Proceso de investigación cualitativa", ["Identificar el problema", "Ingresar al campo", "Recolectar datos", "Analizar e interpretar", "Elaborar el informe"], True),
        ("Elementos de la propuesta de investigación", ["Problema", "Objetivos", "Hipótesis", "Variables", "Marco teórico"], False),
        ("Estrategia de búsqueda científica", ["Definir palabras clave", "Combinar términos con operadores", "Seleccionar bases de datos", "Aplicar filtros", "Evaluar la pertinencia de los resultados"], True),
    ],
}


SKIP_HEADINGS = {
    "objetivo", "objetivos", "introduccion", "informacion de los subtemas",
    "contenido del documento", "material complementario", "bibliografia",
    "bibliografia general", "bibliografia de apoyo", "links de apoyo",
    "videos de apoyo", "preguntas de comprension de la unidad",
}
ORDER_WORDS = {
    "proceso", "fases", "fase", "pasos", "etapas", "secuencia", "orden",
    "evolucion", "formacion", "procedimiento", "construccion", "jerarquia",
    "cronologia", "desarrollo", "ciclo", "niveles",
}
TOPIC_STOPWORDS = {
    "concepto", "conceptos", "definicion", "definiciones", "caracteristicas",
    "clasificacion", "importancia", "general", "principales", "informacion",
    "subtema", "tema", "unidad", "parte", "introduccion", "contenido",
    "derecho", "juridico", "juridica", "juridicos", "juridicas", "segun",
    "metodo", "metodos", "muestreo", "proceso", "procesos", "factores",
    "para", "como", "entre", "desde", "sobre", "aplicada", "aplicado",
}


@dataclass(frozen=True)
class Fact:
    topic: str
    statement: str
    source: str


@dataclass(frozen=True)
class Sequence:
    topic: str
    items: tuple[str, ...]
    source: str
    semantic: bool


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_markdown(text: str) -> str:
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = text.replace("*", "").replace("$", "")
    text = re.sub(r"(?:^|\s)[-•]\s+", " ", text)
    return squash(text)


def clean_heading(raw: str) -> str:
    text = squash(raw.strip(" #*.:–—"))
    text = re.sub(r"^(?:subtema|tema|unidad)\s*[\d.IVXLC-]*\s*:\s*", "", text, flags=re.I)
    text = re.sub(r"^\d+(?:\.\d+)*\s*", "", text)
    text = re.sub(r"^[a-z]\)\s*", "", text, flags=re.I)
    return text.strip(" .:–—")


def useful_heading(raw: str) -> bool:
    key = norm(clean_heading(raw))
    if not key or key in SKIP_HEADINGS:
        return False
    if key.startswith("pagina ") or key == "pagina":
        return False
    if any(key.startswith(prefix) for prefix in (
        "preguntas de comprension", "material complementario", "bibliografia",
        "videos de apoyo", "links de apoyo", "objetivo",
    )):
        return False
    heading = clean_heading(raw)
    if norm(heading).endswith((" de", " del", " de la", " de los", " y", " el", " la")):
        return False
    return 4 <= len(heading) <= 110


def split_sentences(text: str) -> list[str]:
    text = squash(text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÜÑ¿¡])", text)
    return [part.strip() for part in parts if part.strip()]


def useful_sentence(sentence: str) -> bool:
    words = sentence.split()
    key = norm(sentence)
    if not (8 <= len(words) <= 42 and 55 <= len(sentence) <= 260):
        return False
    if any(token in key for token in (
        "http ", "www ", "recuperado de", "bibliografia", "video de apoyo",
        "universidad estatal de milagro", "copyright", "isbn", "total de horas",
        "se conserva la redaccion", "tema de la semana", "texto extraido",
        "no se reproduce aqui", "limitaciones de formato",
    )):
        return False
    if "?" in sentence or "¿" in sentence:
        return False
    if sentence.endswith(":") or sentence.count("(") > 3:
        return False
    if re.search(r"(?:\s|^)(?:[a-z]|\d+)\.$", sentence, flags=re.I):
        return False
    if key.startswith((
        "unidad ", "tema de la semana", "por lo tanto para facilitar el analisis",
        "en esta parte se analizara", "durante el desarrollo de los temas",
    )):
        return False
    if sentence.startswith(("Este documento", "En este documento", "A continuación se")):
        return False
    return True


def topic_relevant(topic: str, sentence: str) -> bool:
    topic_words = [
        word for word in norm(topic).split()
        if len(word) >= 5 and word not in TOPIC_STOPWORDS
    ]
    if not topic_words:
        return True
    sentence_words = norm(sentence).split()
    for topic_word in topic_words:
        stem = topic_word[:6]
        if any(word == topic_word or (len(stem) >= 6 and word.startswith(stem)) for word in sentence_words):
            return True
    return False


def read_source(filename: str) -> str:
    text = (PROCESSED / filename).read_text(encoding="utf-8")
    if filename == "introduccion_al_derecho_texto_completo.md":
        # Este archivo es mixto: solo las páginas 1–504 corresponden a DER101.
        page_505 = re.search(r"(?m)^## Página 505\s*$", text)
        if page_505:
            text = text[:page_505.start()]
    return text


def extract_facts(filename: str) -> list[Fact]:
    text = read_source(filename)
    current: str | None = None
    buffers: dict[str, list[str]] = defaultdict(list)
    source_order: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,5})\s+(.*)$", line)
        if match:
            raw_heading = match.group(2).strip()
            if useful_heading(raw_heading):
                current = clean_heading(raw_heading)
                if current not in buffers:
                    source_order.append(current)
            elif not norm(raw_heading).startswith("pagina "):
                current = None
            continue
        plain_heading = re.match(
            r"^\s*((?:Subtema|Tema|Unidad)\s*[\d.IVXLC-]*(?:\s*[:.-]\s*|\s+).{4,110})\s*$",
            line,
            flags=re.I,
        )
        if plain_heading and useful_heading(plain_heading.group(1)):
            current = clean_heading(plain_heading.group(1))
            if current not in buffers:
                source_order.append(current)
            continue
        if current and line.strip() and not line.lstrip().startswith(("|", "---")):
            buffers[current].append(line.strip())

    facts: list[Fact] = []
    seen: set[str] = set()
    for topic in source_order:
        body = " ".join(buffers[topic])
        per_topic = 0
        for sentence in split_sentences(body):
            sentence = strip_markdown(re.sub(r"\s*\[[^\]]{1,30}\]\s*", " ", sentence))
            key = norm(sentence)
            if not useful_sentence(sentence) or not topic_relevant(topic, sentence) or key in seen:
                continue
            seen.add(key)
            facts.append(Fact(topic=topic, statement=sentence, source=filename))
            per_topic += 1
            if per_topic >= 6:
                break
    return facts


def numbered_sequences(filename: str) -> list[Sequence]:
    text = read_source(filename)
    lines = text.splitlines()
    current_topic = "Contenido de la asignatura"
    sequences: list[Sequence] = []
    i = 0
    while i < len(lines):
        heading = re.match(r"^#{1,5}\s+(.*)$", lines[i])
        if heading and useful_heading(heading.group(1)):
            current_topic = clean_heading(heading.group(1))
        first = re.match(r"^\s*1[.)]\s+(.+)$", lines[i])
        if not first:
            i += 1
            continue
        items = [strip_markdown(first.group(1)).strip(" ;")]
        expected = 2
        j = i + 1
        while j < len(lines) and len(items) < 7:
            nxt = re.match(rf"^\s*{expected}[.)]\s+(.+)$", lines[j])
            if nxt:
                items.append(strip_markdown(nxt.group(1)).strip(" ;"))
                expected += 1
                j += 1
                continue
            if not lines[j].strip() or lines[j].lstrip().startswith("#"):
                break
            if len(items[-1]) < 180 and len(lines[j].strip()) < 150:
                items[-1] = squash(items[-1] + " " + lines[j].strip()).strip(" ;")
                j += 1
                continue
            break
        if (3 <= len(items) <= 6 and all(3 <= len(item) <= 220 for item in items)
                and not any("?" in item or "¿" in item for item in items)):
            context = norm(current_topic + " " + " ".join(lines[max(0, i - 4):i]))
            semantic = any(word in context for word in ORDER_WORDS)
            sequences.append(Sequence(current_topic, tuple(items), filename, semantic))
        i = max(i + 1, j)

    # También se admiten grupos de subtítulos numerados cuando el título padre
    # declara explícitamente un proceso, fases, evolución o jerarquía.
    heading_rows: list[tuple[int, str]] = []
    for line in lines:
        match = re.match(r"^(#{2,5})\s+(.*)$", line)
        if match and useful_heading(match.group(2)):
            heading_rows.append((len(match.group(1)), clean_heading(match.group(2))))
    for idx, (level, parent) in enumerate(heading_rows):
        if not any(word in norm(parent) for word in ORDER_WORDS):
            continue
        children = []
        for child_level, child in heading_rows[idx + 1:]:
            if child_level <= level:
                break
            if child_level == level + 1:
                children.append(child)
        if 3 <= len(children) <= 6:
            sequences.append(Sequence(parent, tuple(children), filename, True))

    unique: list[Sequence] = []
    seen = set()
    for seq in sorted(sequences, key=lambda item: (not item.semantic, item.topic)):
        key = tuple(norm(item) for item in seq.items)
        if key not in seen and len(set(key)) == len(key):
            seen.add(key)
            unique.append(seq)
    return unique


def balanced_facts(facts: list[Fact], count: int) -> list[Fact]:
    buckets: dict[str, list[Fact]] = defaultdict(list)
    for fact in facts:
        buckets[fact.topic].append(fact)
    topics = list(buckets)
    selected: list[Fact] = []
    depth = 0
    while len(selected) < count and topics:
        progressed = False
        for topic in topics:
            if depth < len(buckets[topic]):
                selected.append(buckets[topic][depth])
                progressed = True
                if len(selected) == count:
                    break
        if not progressed:
            break
        depth += 1
    if len(selected) < count:
        raise RuntimeError(f"Solo hay {len(selected)} hechos útiles para una cuota de {count}")
    return selected


def concept_pool(facts: list[Fact]) -> list[str]:
    concepts = []
    for fact in facts:
        topic = clean_heading(fact.topic)
        if topic not in concepts and 3 <= len(topic) <= 100:
            concepts.append(topic)
    return concepts


def distractor_concepts(correct: str, pool: list[str], index: int) -> list[str]:
    candidates = [item for item in pool if norm(item) != norm(correct)]
    candidates.sort(key=lambda item: (abs(len(item) - len(correct)), item))
    if len(candidates) < 3:
        raise RuntimeError("No hay conceptos suficientes para crear distractores")
    start = (index * 7) % len(candidates)
    rotated = candidates[start:] + candidates[:start]
    chosen = []
    for item in rotated:
        if norm(item) not in {norm(value) for value in chosen}:
            chosen.append(item)
        if len(chosen) == 3:
            return chosen
    raise RuntimeError("No se pudieron formar tres distractores")


def lettered(values: list[str], correct_values: set[str], index: int):
    values = list(values)
    shift = index % len(values)
    values = values[shift:] + values[:shift]
    letters = "ABCDE"
    options = [(letters[i], value) for i, value in enumerate(values)]
    correct_letters = [letter for letter, value in options if value in correct_values]
    return options, correct_letters


def md_question(
    qid: str,
    title: str,
    code: str,
    topic: str,
    difficulty: str,
    source: str,
    prompt: str,
    alternatives: list[str],
    answer: str,
    feedback_correct: str,
    feedback_incorrect: str,
    tip: str,
    explanation: str,
    memory_key: str,
    common_confusion: str = "",
    wrong_reasons: list[str] | None = None,
) -> str:
    lines = [
        f"## {qid} — {title}",
        f"- Asignatura: {code}",
        f"- Tema: {topic}",
        f"- Dificultad: {difficulty}",
        "- Estado: revisada",
        f"- Fuente: {source}",
        "- Procedencia: generated_from_compendium",
        "",
        "### Enunciado",
        prompt,
        "",
        "### Alternativas",
        *alternatives,
        "",
        "### Respuesta correcta",
        answer,
        "",
        "### Retroalimentación sencilla",
        feedback_correct,
        "",
        "### Si responde incorrectamente",
        feedback_incorrect,
        "",
        "### Consejo opcional",
        tip,
        "",
        "### Explicación",
        explanation,
        "",
        "### Clave para recordar",
        memory_key,
    ]
    if common_confusion:
        lines += ["", "### Confusión común", common_confusion]
    if wrong_reasons:
        lines += ["", "### Por qué las otras opciones no corresponden", *wrong_reasons]
    lines += ["", "---", ""]
    return "\n".join(lines)


def selection_questions(code: str, facts: list[Fact], quota: int, first_id: int):
    chosen = balanced_facts(facts, quota + max(8, quota // 6))
    pool = concept_pool(facts)
    blocks = []
    used = 0
    cursor = 0
    multiselect_target = max(1, round(quota * 0.12))
    multiselect_done = 0
    by_topic: dict[str, list[Fact]] = defaultdict(list)
    for fact in facts:
        by_topic[fact.topic].append(fact)

    while used < quota:
        fact = chosen[cursor]
        cursor += 1
        qnum = first_id + used
        qid = f"{code}-P{qnum:03d}"
        difficulty = ("básica", "media", "media", "avanzada")[used % 4]
        source = f"{fact.source}, apartado «{fact.topic}»"
        make_multi = (
            multiselect_done < multiselect_target
            and used % 8 == 7
            and len(by_topic[fact.topic]) >= 2
        )

        if make_multi:
            same = [item for item in by_topic[fact.topic] if item.statement != fact.statement][0]
            other_facts = [item for item in facts if item.topic != fact.topic]
            d1 = other_facts[(used * 5) % len(other_facts)]
            d2 = other_facts[(used * 11 + 3) % len(other_facts)]
            while d2.topic == d1.topic or d2.statement == d1.statement:
                d2 = other_facts[(other_facts.index(d2) + 1) % len(other_facts)]
            values = [fact.statement, same.statement, d1.statement, d2.statement]
            options, correct_letters = lettered(values, {fact.statement, same.statement}, used)
            answer = f"{correct_letters[0]} y {correct_letters[1]}. {fact.topic}"
            blocks.append(md_question(
                qid, f"Dos afirmaciones sobre {fact.topic}", code, fact.topic, difficulty,
                source,
                f"Seleccione las dos afirmaciones que corresponden a «{fact.topic}» según el compendio.",
                [f"- {letter}. {value}" for letter, value in options],
                answer,
                f"Las dos afirmaciones correctas desarrollan directamente «{fact.topic}».",
                f"Revisa qué dos enunciados explican el mismo apartado: «{fact.topic}».",
                "Busca dos afirmaciones que compartan el mismo concepto central, no solo palabras jurídicas generales.",
                f"El compendio vincula con «{fact.topic}» estas dos ideas: {fact.statement} {same.statement}",
                f"{fact.topic}: identifica las dos ideas que lo explican de forma conjunta.",
                "Una afirmación puede ser verdadera en otra parte del curso y aun así no responder al apartado preguntado.",
            ))
            multiselect_done += 1
        else:
            correct = clean_heading(fact.topic)
            distractors = distractor_concepts(correct, pool, used)
            values = [correct, *distractors]
            options, correct_letters = lettered(values, {correct}, used)
            correct_letter = correct_letters[0]
            wrong = [
                f"- {letter}. «{value}» corresponde a otro concepto o apartado y no identifica toda la afirmación citada."
                for letter, value in options if letter != correct_letter
            ]
            blocks.append(md_question(
                qid, f"Concepto: {correct}", code, fact.topic, difficulty, source,
                f"¿A qué concepto o apartado corresponde la siguiente afirmación del compendio? «{fact.statement}»",
                [f"- {letter}. {value}" for letter, value in options],
                f"{correct_letter}. {correct}",
                f"La afirmación se desarrolla en el apartado «{correct}».",
                f"La respuesta correcta es «{correct}», porque ese apartado contiene la afirmación presentada.",
                "Identifica el concepto que explica la idea completa, no una palabra aislada.",
                f"En palabras sencillas, «{correct}» se relaciona aquí con esta idea: {fact.statement}",
                f"{correct}: {fact.statement[:150].rstrip()}.",
                "No confundas conceptos cercanos de la misma unidad: compara la definición completa.",
                wrong,
            ))
        used += 1
    return blocks, first_id + quota


def matching_questions(code: str, facts: list[Fact], quota: int, first_id: int):
    representatives = []
    seen_topics = set()
    for fact in facts:
        if fact.topic not in seen_topics:
            representatives.append(fact)
            seen_topics.add(fact.topic)
    if len(representatives) < 8:
        raise RuntimeError(f"{code}: no hay conceptos suficientes para emparejamiento")
    blocks = []
    for index in range(quota):
        start = (index * 3) % len(representatives)
        group = [representatives[(start + offset * 5) % len(representatives)] for offset in range(4)]
        while len({fact.topic for fact in group}) < 4:
            start = (start + 1) % len(representatives)
            group = [representatives[(start + offset * 7) % len(representatives)] for offset in range(4)]
        qid = f"{code}-P{first_id + index:03d}"
        pairs = [(clean_heading(fact.topic), fact.statement.replace(";", ",")) for fact in group]
        alternatives = ["- Conceptos: " + " | ".join(left for left, _ in pairs),
                        "- Descripciones: " + " | ".join(right for _, right in reversed(pairs))]
        answer = "; ".join(f"{left} → {right}" for left, right in pairs)
        source = "; ".join(sorted({fact.source for fact in group}))
        blocks.append(md_question(
            qid, f"Relaciones conceptuales {index + 1}", code,
            "Relación de conceptos del compendio", "media", source,
            "Relacione cada concepto con la afirmación que le corresponde según el compendio.",
            alternatives, answer,
            "Cada concepto quedó unido con la afirmación desarrollada en su propio apartado.",
            "Vuelve a identificar la idea central de cada descripción antes de formar las parejas.",
            "Empieza por la pareja más evidente y descarta esa descripción antes de continuar.",
            "El emparejamiento evalúa si puedes distinguir conceptos próximos por su definición completa.",
            "Concepto y definición deben conservar el mismo núcleo de significado.",
            "No emparejes solo por una palabra compartida; comprueba el sentido completo de cada descripción.",
        ))
    return blocks, first_id + quota


def ordering_questions(code: str, sequences: list[Sequence], quota: int, first_id: int):
    if not sequences:
        raise RuntimeError(f"{code}: no se detectaron secuencias")
    expanded = list(sequences)
    # Para listas largas se crean ventanas diferentes de 3 a 5 elementos sin alterar el orden fuente.
    for seq in list(sequences):
        if len(seq.items) >= 5:
            expanded.append(Sequence(seq.topic, seq.items[:4], seq.source, seq.semantic))
            expanded.append(Sequence(seq.topic, seq.items[-4:], seq.source, seq.semantic))
    unique = []
    seen = set()
    for seq in expanded:
        key = tuple(norm(item) for item in seq.items)
        if key not in seen:
            unique.append(seq)
            seen.add(key)
    if len(unique) < quota:
        raise RuntimeError(f"{code}: solo hay {len(unique)} secuencias distintas para una cuota de {quota}")
    blocks = []
    for index, seq in enumerate(unique[:quota]):
        qid = f"{code}-P{first_id + index:03d}"
        prompt = (
            f"Ordene las etapas o elementos de «{seq.topic}» según la secuencia indicada en el compendio."
            if seq.semantic else
            f"Ordene los elementos de «{seq.topic}» según la secuencia expositiva del compendio."
        )
        shuffled = list(seq.items)
        RNG.shuffle(shuffled)
        if shuffled == list(seq.items):
            shuffled.reverse()
        answer = "; ".join(f"{position}. {item}" for position, item in enumerate(seq.items, 1))
        blocks.append(md_question(
            qid, f"Secuencia: {seq.topic}", code, seq.topic, "media", seq.source,
            prompt,
            ["- Elementos para ordenar: " + " | ".join(shuffled)],
            answer,
            "La secuencia coincide con el orden establecido en el compendio.",
            "Compara qué elemento inicia el proceso y cuál depende del anterior.",
            "Busca primero el punto de partida; después revisa qué paso prepara al siguiente.",
            "El orden correcto conserva la relación progresiva presentada por la fuente.",
            "Inicio, desarrollo y cierre: cada elemento debe ocupar el lugar que prepara al siguiente.",
            "No confundas una lista de elementos con una secuencia: aquí se sigue expresamente el orden de la fuente.",
        ))
    return blocks, first_id + quota


def generate_subject(code: str, config: dict) -> tuple[int, dict[str, int]]:
    facts = []
    sequences = []
    for source in config["sources"]:
        facts.extend(extract_facts(source))
        sequences.extend(numbered_sequences(source))
    for topic, items, semantic in CURATED_SEQUENCES[code]:
        sequences.insert(0, Sequence(topic, tuple(items), config["sources"][0], semantic))
    deduped_facts = []
    seen = set()
    for fact in facts:
        key = norm(fact.statement)
        if key not in seen:
            seen.add(key)
            deduped_facts.append(fact)
    facts = deduped_facts

    next_id = config["start"]
    blocks = []
    selection, next_id = selection_questions(
        code, facts, config["quota"]["selection"], next_id
    )
    blocks.extend(selection)
    ordering, next_id = ordering_questions(
        code, sequences, config["quota"]["ordering"], next_id
    )
    blocks.extend(ordering)
    matching, next_id = matching_questions(
        code, facts, config["quota"]["matching"], next_id
    )
    blocks.extend(matching)

    output = PROCESSED / config["folder"] / "preguntas_compendios.md"
    header = (
        f"# Preguntas generadas desde compendios — {code}: {config['name']}\n\n"
        "Primera tanda generada desde los compendios incorporados el 20 de julio de 2026. "
        "Las preguntas originales del aula virtual permanecen en `banco_preguntas.md`.\n\n---\n\n"
    )
    output.write_text(header + "\n".join(blocks), encoding="utf-8", newline="\n")
    counts = {name: config["quota"][name] for name in ("selection", "ordering", "matching")}
    return len(blocks), counts


def main() -> int:
    total = 0
    for code, config in SUBJECTS.items():
        count, counts = generate_subject(code, config)
        total += count
        print(
            f"{code}: {count} preguntas "
            f"(selección {counts['selection']}, ordenamiento {counts['ordering']}, "
            f"emparejamiento {counts['matching']})"
        )
    print(f"TOTAL GENERADO: {total}")
    if total != 518:
        raise RuntimeError(f"Se esperaban 518 preguntas y se generaron {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
