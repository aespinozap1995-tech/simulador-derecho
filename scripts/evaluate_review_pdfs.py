#!/usr/bin/env python3
"""Evalúa preguntas de PDF de revisión contra el banco estructurado."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

from pypdf import PdfReader


@dataclass
class Candidate:
    file: str
    number: int
    prompt: str
    options: list[str]
    correct: str
    complete: bool
    duplicate_id: str = ""
    similarity: float = 0.0


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def clean_fragment(text: str) -> str:
    lines = []
    for line in text.replace("\uf058", "").replace("", "").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("https://"):
            continue
        if re.match(r"^\d+/\d+/\d+,", stripped):
            continue
        if re.match(r"^\d+/\d+$", stripped):
            continue
        if "Revisión del intento | Grado B UNEMI" in stripped:
            continue
        lines.append(stripped)
    return " ".join(lines).strip()


def parse_pdf(path: Path, relative: str) -> list[Candidate]:
    reader = PdfReader(path)
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    pieces = re.split(r"\nPregunta\s+(\d+)\s*\n", text)
    candidates: list[Candidate] = []
    for index in range(1, len(pieces), 2):
        number = int(pieces[index])
        block = pieces[index + 1]
        if "Marcar pregunta" not in block:
            continue
        block = block.split("Marcar pregunta", 1)[1]
        answer_match = re.search(r"La respuesta correcta es:\s*(.*?)(?:\n\d+/\d+/\d+,|\nhttps://|\nFinalizar|$)", block, re.S | re.I)
        correct = clean_fragment(answer_match.group(1)) if answer_match else ""
        question_part = block[: answer_match.start()] if answer_match else block
        option_matches = list(re.finditer(r"(?m)^([a-z])\.\s+", question_part))
        if not option_matches:
            continue
        prompt = clean_fragment(question_part[: option_matches[0].start()])
        options: list[str] = []
        marked_correct = ""
        for option_index, match in enumerate(option_matches):
            end = option_matches[option_index + 1].start() if option_index + 1 < len(option_matches) else len(question_part)
            raw_option = question_part[match.end() : end]
            option_text = clean_fragment(raw_option)
            options.append(option_text)
            if "\uf058" in raw_option or "" in raw_option:
                marked_correct = option_text
        if not correct:
            correct = marked_correct
        correct_normalized = normalize(correct)
        option_normalized = [normalize(option) for option in options]
        answer_present = bool(correct_normalized) and any(
            correct_normalized == option or correct_normalized in option or option in correct_normalized
            for option in option_normalized
        )
        candidates.append(
            Candidate(
                file=relative,
                number=number,
                prompt=prompt,
                options=options,
                correct=correct,
                complete=bool(prompt and len(options) >= 2 and answer_present),
            )
        )
    return candidates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("bank", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.resolve()
    existing = json.loads(args.bank.read_text(encoding="utf-8"))["questions"]
    existing_prompts = [(question["id"], normalize(question["prompt"])) for question in existing]
    candidates: list[Candidate] = []
    for path in sorted(source.glob("*.pdf")):
        relative = str(path.relative_to(source))
        for candidate in parse_pdf(path, relative):
            normalized = normalize(candidate.prompt)
            best_id = ""
            best_score = 0.0
            for question_id, prompt in existing_prompts:
                score = 1.0 if normalized == prompt else SequenceMatcher(None, normalized, prompt).ratio()
                if score > best_score:
                    best_id, best_score = question_id, score
            # Los PDF suelen añadir instrucciones como "Seleccione una" y
            # contienen errores OCR; 0,85 conserva esas variantes como posibles
            # duplicados para revisión humana.
            if best_score >= 0.85:
                candidate.duplicate_id = best_id
                candidate.similarity = best_score
            candidates.append(candidate)

    by_file: dict[str, list[Candidate]] = {}
    for candidate in candidates:
        by_file.setdefault(candidate.file, []).append(candidate)

    complete = [candidate for candidate in candidates if candidate.complete]
    new = [candidate for candidate in complete if not candidate.duplicate_id]
    duplicates = [candidate for candidate in complete if candidate.duplicate_id]
    incomplete = [candidate for candidate in candidates if not candidate.complete]
    lines = [
        "# Evaluación preliminar de PDF de revisión",
        "",
        f"- Preguntas detectadas: **{len(candidates)}**",
        f"- Completas y verificables por texto/marca: **{len(complete)}**",
        f"- Coincidencias probables con el banco: **{len(duplicates)}**",
        f"- Candidatas nuevas: **{len(new)}**",
        f"- Incompletas o no interpretables automáticamente: **{len(incomplete)}**",
        "",
        "## Resumen por archivo",
        "",
        "| Archivo | Detectadas | Completas | Duplicadas | Nuevas |",
        "|---|---:|---:|---:|---:|",
    ]
    for filename, items in by_file.items():
        file_complete = [item for item in items if item.complete]
        file_duplicates = [item for item in file_complete if item.duplicate_id]
        lines.append(
            f"| `{filename}` | {len(items)} | {len(file_complete)} | {len(file_duplicates)} | {len(file_complete) - len(file_duplicates)} |"
        )
    lines.extend(["", "## Candidatas nuevas completas", ""])
    for candidate in new:
        lines.extend(
            [
                f"### {candidate.file} — Pregunta {candidate.number}",
                "",
                candidate.prompt,
                "",
                *[f"- {chr(65 + index)}. {option}" for index, option in enumerate(candidate.options)],
                "",
                f"**Respuesta confirmada:** {candidate.correct}",
                "",
            ]
        )
    lines.extend(["## Coincidencias probables", ""])
    for candidate in duplicates:
        lines.append(
            f"- `{candidate.file}`, pregunta {candidate.number} → {candidate.duplicate_id} ({candidate.similarity:.1%}): {candidate.prompt}"
        )
    lines.extend(["", "## Pendientes de revisión visual", ""])
    for candidate in incomplete:
        lines.append(f"- `{candidate.file}`, pregunta {candidate.number}: {candidate.prompt or '(sin enunciado recuperable)' }")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"detectadas={len(candidates)} completas={len(complete)} duplicadas={len(duplicates)} nuevas={len(new)} pendientes={len(incomplete)}")


if __name__ == "__main__":
    main()
