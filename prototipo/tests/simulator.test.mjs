import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const bank = JSON.parse(
  await readFile(new URL("../public/questions.json", import.meta.url), "utf8"),
);

test("the question bank contains the reviewed beta inventory", () => {
  assert.ok(Array.isArray(bank.questions));
  assert.equal(bank.questions.length, 347);
  assert.equal(bank.questions.filter((question) => question.active).length, 345);
  assert.deepEqual(
    [...new Set(bank.questions.map((question) => question.subject_code))].sort(),
    ["C10", "DER101", "DER102", "DER104", "DER105", "DER106"],
  );
});

test("every active question has enough data to run in the simulator", () => {
  for (const question of bank.questions.filter((item) => item.active)) {
    assert.ok(question.id, "question id is required");
    assert.ok(question.prompt, `${question.id} needs a prompt`);
    assert.ok(question.question_type, `${question.id} needs a type`);
    assert.ok(question.answer, `${question.id} needs an answer`);

    if (["single_choice", "true_false"].includes(question.question_type)) {
      assert.ok(question.options.length >= 2, `${question.id} needs answer options`);
      assert.equal(question.answer.option_ids.length, 1, `${question.id} needs one correct option`);
    }

    if (question.question_type === "matching") {
      assert.ok(question.answer.pairs.length >= 2, `${question.id} needs matching pairs`);
    }

    if (question.question_type === "ordering") {
      assert.ok(question.answer.ordered_items.length >= 2, `${question.id} needs ordered items`);
    }
  }
});

test("the main interface contains the beta entry points", async () => {
  const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
  assert.match(source, /Simulador de examen final/);
  assert.match(source, /Carrera de Derecho/);
  assert.match(source, /Tiempo restante/);
  assert.match(source, /Retroalimentación/);
  assert.match(source, /subjectCatalog/);
  assert.match(source, /Para recordar:/);
});

test("DER101 includes the subject-of-law question with structured feedback", () => {
  const question = bank.questions.find((item) => item.id === "DER101-P029");
  assert.ok(question);
  assert.equal(question.answer.option_ids[0], "A");
  assert.match(question.explanation, /derechos y asumir obligaciones/i);
  assert.match(question.memory_key, /puede ser sujeto del Derecho/i);
  assert.equal(question.why_options_are_wrong.B.length > 0, true);
});
