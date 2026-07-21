#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_questions.py — Valida datos/questions.json y datos/subjects/*.json.

Uso:
    python scripts/validate_questions.py

Solo biblioteca estándar. Sale con código 0 si todas las validaciones pasan.
"""

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "datos"
SUBJECTS_DIR = DATA_DIR / "subjects"

EXPECTED_TOTAL = 865
EXPECTED_BY_SUBJECT = {
    "DER101": 125,
    "DER102": 105,
    "DER104": 125,
    "DER105": 142,
    "DER106": 153,
    "C10": 215,
}
EXPECTED_PENDING = {"DER105-P033", "DER105-P087"}
EXPECTED_GENERATED = 518

ALLOWED_TYPES = {
    "single_choice", "multiple_choice", "true_false", "fill_blank",
    "matching", "ordering", "unknown",
}
ALLOWED_DIFFICULTY = {"basic", "medium", "advanced"}
ALLOWED_STATUS = {"reviewed", "pending_review"}
REQUIRED_FIELDS = [
    "id", "subject_code", "subject_name", "title", "question_type", "topic",
    "difficulty", "status", "active", "provenance", "source", "prompt",
    "options", "answer", "feedback_correct", "feedback_incorrect", "tip",
]
REQUIRED_NONEMPTY_STR = [
    "id", "subject_code", "subject_name", "title", "question_type", "topic",
    "difficulty", "status", "provenance", "source", "prompt",
    "feedback_correct", "feedback_incorrect", "tip",
]
ID_RE = re.compile(r"^([A-Z0-9]+)-P(\d{3})$")

errors = []
warnings = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def load_utf8(path):
    """Carga JSON verificando codificación UTF-8 estricta."""
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        errors.append(f"{path.name}: no es UTF-8 válido ({exc})")
        return None
    return json.loads(text)


def validate_question(q):
    qid = q.get("id", "<sin id>")
    for f in REQUIRED_FIELDS:
        check(f in q, f"{qid}: falta el campo obligatorio '{f}'")
    for f in REQUIRED_NONEMPTY_STR:
        v = q.get(f)
        check(isinstance(v, str) and v.strip(), f"{qid}: campo '{f}' vacío o no textual")

    m = ID_RE.match(q.get("id", ""))
    check(bool(m), f"{qid}: identificador con formato inválido")
    if m:
        check(m.group(1) == q.get("subject_code"),
              f"{qid}: subject_code '{q.get('subject_code')}' no coincide con el prefijo del id")

    check(q.get("question_type") in ALLOWED_TYPES, f"{qid}: question_type no permitido: {q.get('question_type')!r}")
    check(q.get("difficulty") in ALLOWED_DIFFICULTY, f"{qid}: dificultad no permitida: {q.get('difficulty')!r}")
    check(q.get("status") in ALLOWED_STATUS, f"{qid}: estado no permitido: {q.get('status')!r}")
    check(q.get("provenance") in {"original_simulator", "generated_from_compendium"},
          f"{qid}: provenance inesperado: {q.get('provenance')!r}")

    # Regla active/status.
    if q.get("status") == "pending_review":
        check(q.get("active") is False, f"{qid}: pending_review debe tener active=false")
    elif q.get("status") == "reviewed":
        check(q.get("active") is True, f"{qid}: reviewed debe tener active=true")

    # Opciones: estructura y letras sin duplicar.
    opts = q.get("options", [])
    check(isinstance(opts, list), f"{qid}: options debe ser lista")
    letters = []
    for o in opts:
        check(isinstance(o, dict) and set(o) == {"id", "text"}, f"{qid}: opción mal formada: {o!r}")
        check(re.match(r"^[A-E]$", str(o.get("id", ""))), f"{qid}: letra de opción inválida: {o.get('id')!r}")
        check(isinstance(o.get("text"), str) and o["text"].strip(), f"{qid}: opción {o.get('id')} sin texto")
        letters.append(o.get("id"))
    check(len(letters) == len(set(letters)), f"{qid}: letras de opción duplicadas: {letters}")
    option_texts = [re.sub(r"\s+", " ", o.get("text", "")).strip().casefold() for o in opts]
    if q.get("provenance") == "generated_from_compendium":
        check(len(option_texts) == len(set(option_texts)), f"{qid}: textos de opción duplicados")

    # Respuesta.
    ans = q.get("answer", {})
    check(isinstance(ans, dict) and set(ans) == {
              "raw", "option_ids", "accepted_text", "pairs", "ordered_items"
          },
          f"{qid}: answer con claves inesperadas: {sorted(ans) if isinstance(ans, dict) else ans!r}")
    check(isinstance(ans.get("raw"), str) and ans["raw"].strip(), f"{qid}: answer.raw vacío")
    oids = ans.get("option_ids", [])
    check(isinstance(oids, list) and len(oids) == len(set(oids)), f"{qid}: option_ids con duplicados")
    for l in oids:
        check(l in set(letters), f"{qid}: option_id '{l}' no existe entre las opciones")

    qt = q.get("question_type")
    if qt in ("single_choice", "true_false") and q.get("status") == "reviewed":
        check(len(oids) == 1, f"{qid}: {qt} revisada debe tener exactamente 1 option_id (tiene {len(oids)})")
    if qt == "multiple_choice" and q.get("status") == "reviewed":
        check(len(oids) >= 2, f"{qid}: multiple_choice revisada debe tener 2+ option_ids")
    if qt == "matching" and q.get("status") == "reviewed" and not ans.get("pairs"):
        warnings.append(f"{qid}: matching sin pairs normalizados (raw conservado)")
    if qt == "fill_blank" and q.get("status") == "reviewed" and not ans.get("accepted_text"):
        warnings.append(f"{qid}: fill_blank sin accepted_text (raw conservado)")
    if qt == "ordering" and q.get("status") == "reviewed":
        check(len(ans.get("ordered_items", [])) >= 2,
              f"{qid}: ordering revisada debe tener 2+ ordered_items")
    if qt == "unknown":
        warnings.append(f"{qid}: tipo unknown (revisar manualmente)")

    for p in ans.get("pairs", []):
        check(isinstance(p, dict) and set(p) == {"left", "right"} and p["left"].strip() and p["right"].strip(),
              f"{qid}: par mal formado: {p!r}")
    pairs = ans.get("pairs", [])
    if pairs:
        lefts = [re.sub(r"\s+", " ", p["left"]).strip().casefold() for p in pairs]
        rights = [re.sub(r"\s+", " ", p["right"]).strip().casefold() for p in pairs]
        check(len(lefts) == len(set(lefts)), f"{qid}: conceptos repetidos en matching")
        check(len(rights) == len(set(rights)), f"{qid}: descripciones repetidas en matching")
    for item in ans.get("ordered_items", []):
        check(isinstance(item, str) and item.strip(),
              f"{qid}: elemento de ordenamiento vacío o no textual: {item!r}")
    ordered = [re.sub(r"\s+", " ", item).strip().casefold() for item in ans.get("ordered_items", [])]
    check(len(ordered) == len(set(ordered)), f"{qid}: elementos repetidos en ordering")

    for field in ("explanation", "memory_key", "common_confusion"):
        if field in q:
            check(isinstance(q[field], str) and q[field].strip(),
                  f"{qid}: campo opcional '{field}' vacío o no textual")
    if "why_options_are_wrong" in q:
        reasons = q["why_options_are_wrong"]
        check(isinstance(reasons, dict), f"{qid}: why_options_are_wrong debe ser objeto")
        if isinstance(reasons, dict):
            for letter, reason in reasons.items():
                check(letter in letters, f"{qid}: distractor '{letter}' no existe entre las opciones")
                check(letter not in oids, f"{qid}: la opción correcta '{letter}' no debe tener explicación de distractor")
                check(isinstance(reason, str) and reason.strip(),
                      f"{qid}: explicación vacía para el distractor '{letter}'")

    if q.get("provenance") == "generated_from_compendium":
        for field in ("explanation", "memory_key", "common_confusion"):
            check(isinstance(q.get(field), str) and q[field].strip(),
                  f"{qid}: pregunta generada sin '{field}'")
        check("compendio" in q.get("source", "").casefold()
              or q.get("source", "").casefold().endswith(".md")
              or ".md," in q.get("source", "").casefold(),
              f"{qid}: pregunta generada sin fuente Markdown identificable")


def main():
    consolidated = load_utf8(DATA_DIR / "questions.json")
    if consolidated is None:
        report_and_exit()
    questions = consolidated.get("questions", [])

    # Total y conteos por asignatura.
    check(len(questions) == EXPECTED_TOTAL,
          f"Total: se esperaban {EXPECTED_TOTAL} preguntas y hay {len(questions)}")
    generated = [q for q in questions if q.get("provenance") == "generated_from_compendium"]
    check(len(generated) == EXPECTED_GENERATED,
          f"Generadas desde compendios: se esperaban {EXPECTED_GENERATED} y hay {len(generated)}")
    counts = {}
    for q in questions:
        counts[q.get("subject_code")] = counts.get(q.get("subject_code"), 0) + 1
    for code, expected in EXPECTED_BY_SUBJECT.items():
        check(counts.get(code, 0) == expected,
              f"{code}: se esperaban {expected} preguntas y hay {counts.get(code, 0)}")
    for code in counts:
        check(code in EXPECTED_BY_SUBJECT, f"Asignatura inesperada en el consolidado: {code}")

    # Identificadores únicos y registros no duplicados.
    ids = [q.get("id") for q in questions]
    dupes = {i for i in ids if ids.count(i) > 1}
    check(not dupes, f"Identificadores duplicados: {sorted(dupes)}")
    serialized = [json.dumps(q, ensure_ascii=False, sort_keys=True) for q in questions]
    check(len(serialized) == len(set(serialized)), "Existen registros completos duplicados")

    # Consecutividad por asignatura.
    by_subject = {}
    for q in questions:
        m = ID_RE.match(q.get("id", ""))
        if m:
            by_subject.setdefault(m.group(1), []).append(int(m.group(2)))
    for code, nums in sorted(by_subject.items()):
        nums_sorted = sorted(nums)
        expected_seq = list(range(1, len(nums_sorted) + 1))
        check(nums_sorted == expected_seq,
              f"{code}: numeración no consecutiva (faltan/saltan: "
              f"{sorted(set(expected_seq) ^ set(nums_sorted))})")

    # Validación por pregunta.
    for q in questions:
        validate_question(q)

    # Casos conocidos: pendientes.
    pending = {q["id"] for q in questions if q.get("status") == "pending_review"}
    check(pending == EXPECTED_PENDING,
          f"Pendientes esperadas {sorted(EXPECTED_PENDING)}, encontradas {sorted(pending)}")

    # Consistencia consolidado <-> archivos por asignatura.
    for code in EXPECTED_BY_SUBJECT:
        sub_path = SUBJECTS_DIR / f"{code}.json"
        if not sub_path.exists():
            errors.append(f"Falta el archivo por asignatura: {sub_path.name}")
            continue
        sub = load_utf8(sub_path)
        if sub is None:
            continue
        sub_qs = sub.get("questions", [])
        check(sub.get("total") == len(sub_qs),
              f"{code}.json: 'total' ({sub.get('total')}) no coincide con las preguntas ({len(sub_qs)})")
        cons_qs = [q for q in questions if q.get("subject_code") == code]
        check(sub_qs == cons_qs,
              f"{code}.json: las preguntas difieren del consolidado")

    report_and_exit()


def report_and_exit():
    print(f"Validaciones con error: {len(errors)}")
    for e in errors:
        print("  ERROR:", e)
    print(f"Advertencias (no fatales): {len(warnings)}")
    for w in warnings:
        print("  AVISO:", w)
    if errors:
        print("\nRESULTADO: FALLÓ")
        sys.exit(1)
    print("\nRESULTADO: OK — todas las validaciones pasaron")
    sys.exit(0)


if __name__ == "__main__":
    main()
