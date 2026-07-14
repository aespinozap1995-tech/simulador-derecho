import { readFile, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptsDirectory = dirname(fileURLToPath(import.meta.url));
const projectDirectory = dirname(scriptsDirectory);
const templatePath = join(projectDirectory, "prototipo", "standalone-template.html");
const questionsPath = join(projectDirectory, "prototipo", "public", "questions.json");
const outputPath = join(projectDirectory, "simulador-examen-final.html");

const [template, questionsText] = await Promise.all([
  readFile(templatePath, "utf8"),
  readFile(questionsPath, "utf8"),
]);

const safeQuestions = questionsText.replace(/<\//g, "<\\/");
const output = template.replace("__QUESTION_DATA__", safeQuestions);
const questions = JSON.parse(questionsText).questions;
const applicationScript = template
  .split("<script>")
  .at(-1)
  .split("</script>")[0];

if (output.includes("__QUESTION_DATA__")) {
  throw new Error("No se pudo insertar el banco de preguntas en el HTML.");
}
if (questions.length !== 346 || questions.filter((question) => question.active).length !== 344) {
  throw new Error("El inventario de preguntas no coincide con el banco validado.");
}
new Function(applicationScript);

await writeFile(outputPath, output, "utf8");
console.log(`${outputPath} — ${Buffer.byteLength(output)} bytes — 344 preguntas activas`);
