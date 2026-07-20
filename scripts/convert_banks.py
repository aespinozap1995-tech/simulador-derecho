#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_banks.py — Convierte los bancos Markdown revisados a JSON estructurado.

Uso:
    python scripts/convert_banks.py

- Lee los seis bancos desde rutas relativas al proyecto (carpeta padre de `scripts/`).
- Genera datos/questions.json y datos/subjects/<CODIGO>.json (UTF-8, indentado, determinista).
- No modifica los Markdown de origen. No usa servicios externos. Solo biblioteca estándar.
- Reejecutable: sobrescribe las salidas completas, nunca duplica preguntas.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "datos"
SUBJECTS_DIR = DATA_DIR / "subjects"

# Orden determinista de asignaturas y sus rutas de origen.
BANKS = [
    ("DER101", "Introducción al Derecho",
     "Procesado/DER 101 - Introducción al Derecho/banco_preguntas.md"),
    ("DER102", "Lógica y Dialéctica Jurídica",
     "Procesado/DER 102 - Lógica y Dialéctica Jurídica/banco_preguntas.md"),
    ("DER104", "Teoría General del Estado y Sociología Jurídica",
     "Procesado/DER 104 - Teoría General del Estado y Sociología Jurídica/banco_preguntas.md"),
    ("DER105", "Expresión Oral y Redacción Jurídica",
     "Procesado/DER 105 - Expresión Oral y Redacción Jurídica/banco_preguntas.md"),
    ("DER106", "Historia y Filosofía del Derecho",
     "Procesado/DER 106 - Historia y Filosofía del Derecho/banco_preguntas.md"),
    ("C10", "Investigación",
     "Procesado/C10 - Investigación/banco_preguntas.md"),
]

DIFFICULTY_MAP = {"básica": "basic", "media": "medium", "avanzada": "advanced"}
STATUS_MAP = {"revisada": "reviewed", "pendiente_de_revision": "pending_review"}

OPTION_RE = re.compile(r"^- ([A-E])\.\s+(.*)$")
HEADER_RE = re.compile(r"^([A-Z0-9]+-P\d{3})\s+—\s+(.*)$")
META_RE = re.compile(r"^- (Asignatura|Tema|Dificultad|Estado|Fuente):\s*(.*)$")
SINGLE_LETTER_RE = re.compile(r"^([A-E])\.\s")
MULTI_LETTER_RE = re.compile(r"^([A-E](?:,\s*[A-E])*\s+y\s+[A-E])\.\s")
BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
NUMBERED_PAIR_RE = re.compile(r"^\(\d\)$")
ORDERED_ITEM_RE = re.compile(r"(?:^|;\s*)\d+\.\s*(.*?)(?=;\s*\d+\.|$)")

# Notas del conversor (advertencias no fatales) acumuladas para el reporte.
WARNINGS = []


def norm_key(s):
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip()


def split_blocks(text):
    """Divide el Markdown en bloques de pregunta a partir de '## '."""
    blocks = []
    current = None
    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                blocks.append(current)
            current = [line[3:]]
        elif current is not None:
            current.append(line)
    if current is not None:
        blocks.append(current)
    return blocks


def parse_sections(lines):
    """Separa metadatos (líneas '- Clave: valor') y secciones '### '."""
    meta = {}
    sections = {}
    name = None
    buf = []
    for line in lines:
        if line.startswith("### "):
            if name is not None:
                sections[name] = "\n".join(buf).strip()
            name = line[4:].strip()
            buf = []
        elif name is None:
            m = META_RE.match(line)
            if m:
                meta[m.group(1)] = m.group(2).strip()
        else:
            if line.strip() == "---":
                continue
            buf.append(line)
    if name is not None:
        sections[name] = "\n".join(buf).strip()
    return meta, sections


def parse_options(alt_text):
    """Devuelve (opciones_con_letra, nota_de_opciones_sin_letra)."""
    options = []
    note_lines = []
    for line in alt_text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        m = OPTION_RE.match(line)
        if m:
            options.append({"id": m.group(1), "text": m.group(2).strip()})
        else:
            cleaned = line[2:].strip() if line.startswith("- ") else line.strip()
            if cleaned:
                note_lines.append(cleaned)
    return options, " | ".join(note_lines)


def parse_option_notes(text):
    """Convierte líneas '- A. explicación' en un objeto por alternativa."""
    notes = {}
    for line in text.splitlines():
        match = OPTION_RE.match(line.rstrip())
        if match:
            notes[match.group(1)] = match.group(2).strip()
    return notes


def extract_numbered_statements(prompt):
    """Extrae '(1) texto (2) texto…' del enunciado para resolver pares numerados."""
    found = re.findall(r"\((\d)\)\s*(.*?)(?=\s*\(\d\)|$)", prompt, re.S)
    return {f"({n})": re.sub(r"\s+", " ", t).strip(" .;") for n, t in found if t.strip()}


def parse_pairs(raw, prompt):
    """Convierte 'X → Y; Z → W' (o separado por '. ') en pares left/right."""
    segs = raw.split("→")
    if len(segs) < 2:
        return []
    pairs = []
    left = segs[0].strip()
    n = len(segs)
    for i, seg in enumerate(segs[1:], 1):
        if i < n - 1:
            idx = seg.rfind(";")
            if idx == -1:
                idx = seg.rfind(". ")
            if idx == -1:
                return []  # no separable con seguridad
            right = seg[:idx].strip(" .;")
            next_left = seg[idx + 1:].strip(" .;")
        else:
            right = seg.strip(" .;")
            next_left = None
        pairs.append({"left": left.strip(" .;"), "right": right})
        left = next_left
    # Resolver referencias numeradas "(1)" con los enunciados del prompt.
    numbered = extract_numbered_statements(prompt)
    if numbered:
        for p in pairs:
            if NUMBERED_PAIR_RE.match(p["left"]) and p["left"] in numbered:
                p["left"] = numbered[p["left"]]
    # Retirar corchetes envolventes (marcadores de solución del banco).
    for p in pairs:
        for k in ("left", "right"):
            v = p[k].strip()
            if v.startswith("[") and v.endswith("]"):
                v = v[1:-1].strip()
            p[k] = v
    return pairs


def classify_and_answer(qid, prompt, options, raw):
    """Determina question_type y la respuesta normalizada de forma conservadora."""
    answer = {
        "raw": raw,
        "option_ids": [],
        "accepted_text": [],
        "pairs": [],
        "ordered_items": [],
    }
    option_letters = [o["id"] for o in options]
    option_texts = {norm_key(o["text"]) for o in options}

    # Pendientes de revisión: estructura de opción única, sin normalizar respuesta.
    if raw.startswith("Pendiente de revisión"):
        return ("single_choice" if options else "unknown"), answer

    # Verdadero/Falso.
    if options and option_texts <= {"verdadero", "falso"}:
        m = SINGLE_LETTER_RE.match(raw)
        if m and m.group(1) in option_letters:
            answer["option_ids"] = [m.group(1)]
        return "true_false", answer

    # Ordenamiento: la solución enumera explícitamente los elementos en su orden.
    if norm_key(prompt).startswith("ordene ") or norm_key(prompt).startswith("ordena "):
        ordered_items = [item.strip(" .;") for item in ORDERED_ITEM_RE.findall(raw)]
        if len(ordered_items) >= 2:
            answer["ordered_items"] = ordered_items
        else:
            WARNINGS.append(
                f"{qid}: ordenamiento no separable con seguridad; "
                "ordered_items vacío (raw conservado)"
            )
        return "ordering", answer

    # Relacionar (matching): la solución usa flechas '→'.
    if "→" in raw:
        pairs = parse_pairs(raw, prompt)
        if pairs:
            answer["pairs"] = pairs
        else:
            WARNINGS.append(f"{qid}: matching no separable con seguridad; pairs vacío (raw conservado)")
        return "matching", answer

    # Selección múltiple: "A y D." / "B, C y D."
    m = MULTI_LETTER_RE.match(raw)
    if m:
        letters = re.findall(r"[A-E]", m.group(1))
        if all(l in option_letters for l in letters):
            answer["option_ids"] = sorted(set(letters))
        else:
            WARNINGS.append(f"{qid}: letras {letters} no coinciden con opciones; option_ids vacío")
        return "multiple_choice", answer

    # Completar espacios: la solución marca las palabras con corchetes [ ... ].
    if BRACKET_RE.search(raw):
        answer["accepted_text"] = [t.strip() for t in BRACKET_RE.findall(raw)]
        sm = SINGLE_LETTER_RE.match(raw)
        if sm and sm.group(1) in option_letters:
            answer["option_ids"] = [sm.group(1)]
        return "fill_blank", answer

    # Opción única clásica.
    sm = SINGLE_LETTER_RE.match(raw)
    if sm:
        if sm.group(1) in option_letters:
            answer["option_ids"] = [sm.group(1)]
        else:
            WARNINGS.append(f"{qid}: letra {sm.group(1)} sin opción correspondiente; option_ids vacío")
        return "single_choice", answer

    # Completar sin corchetes ni letra (caso límite): conservar raw.
    if not options and ("____" in prompt or norm_key(prompt).startswith("complete")):
        WARNINGS.append(f"{qid}: fill_blank sin marcadores [] en la solución; accepted_text vacío")
        return "fill_blank", answer

    WARNINGS.append(f"{qid}: tipo no determinable con seguridad -> unknown")
    return "unknown", answer


def convert_bank(code, name, rel_path):
    path = PROJECT_ROOT / rel_path
    text = path.read_text(encoding="utf-8")
    questions = []
    for lines in split_blocks(text):
        header = lines[0].strip()
        hm = HEADER_RE.match(header)
        if not hm:
            # Encabezados que no son preguntas (p. ej. IDs -M###) se omiten y registran.
            WARNINGS.append(f"{code}: encabezado omitido (no es pregunta -P###): {header!r}")
            continue
        qid, title = hm.group(1), hm.group(2).strip()
        meta, sections = parse_sections(lines[1:])
        prompt = re.sub(r"\s+\n", "\n", sections.get("Enunciado", "").strip())
        options, options_note = parse_options(sections.get("Alternativas", ""))
        raw = re.sub(r"\s+", " ", sections.get("Respuesta correcta", "").strip())
        qtype, answer = classify_and_answer(qid, prompt, options, raw)
        difficulty = DIFFICULTY_MAP.get(meta.get("Dificultad", "").strip(), "")
        status = STATUS_MAP.get(meta.get("Estado", "").strip(), "")
        if not difficulty:
            WARNINGS.append(f"{qid}: dificultad no reconocida: {meta.get('Dificultad')!r}")
        if not status:
            WARNINGS.append(f"{qid}: estado no reconocido: {meta.get('Estado')!r}")
        q = {
            "id": qid,
            "subject_code": code,
            "subject_name": name,
            "title": title,
            "question_type": qtype,
            "topic": meta.get("Tema", "").strip(),
            "difficulty": difficulty,
            "status": status,
            "active": status == "reviewed",
            "provenance": "original_simulator",
            "source": meta.get("Fuente", "").strip(),
            "prompt": prompt,
            "options": options,
            "answer": answer,
            "feedback_correct": sections.get("Retroalimentación sencilla", "").strip(),
            "feedback_incorrect": sections.get("Si responde incorrectamente", "").strip(),
            "tip": sections.get("Consejo opcional", "").strip(),
        }
        optional_fields = {
            "explanation": sections.get("Explicación", "").strip(),
            "memory_key": sections.get("Clave para recordar", "").strip(),
            "common_confusion": sections.get("Confusión común", "").strip(),
            "why_options_are_wrong": parse_option_notes(
                sections.get("Por qué las otras opciones no corresponden", "")
            ),
        }
        q.update({key: value for key, value in optional_fields.items() if value})
        if options_note:
            q["options_note"] = options_note
        questions.append(q)
    # Orden determinista por número de pregunta.
    questions.sort(key=lambda q: int(q["id"].rsplit("P", 1)[1]))
    return questions


def dump_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")


def main():
    all_questions = []
    per_subject = {}
    for code, name, rel in BANKS:
        qs = convert_bank(code, name, rel)
        per_subject[code] = {
            "subject_code": code,
            "subject_name": name,
            "source_file": rel,
            "total": len(qs),
            "questions": qs,
        }
        all_questions.extend(qs)
        print(f"{code}: {len(qs)} preguntas convertidas desde {rel}")

    for code, payload in per_subject.items():
        dump_json(SUBJECTS_DIR / f"{code}.json", payload)

    consolidated = {
        "schema": "question.schema.json",
        "subjects": [
            {"subject_code": c, "subject_name": n, "total": per_subject[c]["total"]}
            for c, n, _ in BANKS
        ],
        "total": len(all_questions),
        "questions": all_questions,
    }
    dump_json(DATA_DIR / "questions.json", consolidated)
    print(f"TOTAL: {len(all_questions)} preguntas -> {DATA_DIR / 'questions.json'}")

    if WARNINGS:
        print("\nAdvertencias del conversor:")
        for w in WARNINGS:
            print(" -", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
# fin del conversor
