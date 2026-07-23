"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  BookOpen,
  FilePenLine,
  GitBranch,
  History,
  Landmark,
  SearchCheck,
  type LucideIcon,
} from "lucide-react";

type Subject = { code: string; label: string; name: string; total: number; icon: LucideIcon };
type SubjectDefinition = Omit<Subject, "total">;
type BankQuestion = {
  id: string;
  subject_code: string;
  question_type: "single_choice" | "multiple_choice" | "true_false" | "fill_blank" | "matching" | "ordering" | "unknown";
  topic: string;
  prompt: string;
  active: boolean;
  options: { id: string; text: string }[];
  answer: {
    option_ids: string[];
    pairs: { left: string; right: string }[];
    ordered_items: string[];
  };
  feedback_correct: string;
  feedback_incorrect: string;
  tip: string;
  explanation?: string;
  memory_key?: string;
  common_confusion?: string;
  why_options_are_wrong?: Record<string, string>;
};
type AnswerValue = string | string[] | Record<string, string>;
type Attempt = { id: string; subject: string; subjectName: string; date: string; score: number; total: number; percentage: number; durationSeconds?: number };
type SavedAttempt = {
  version: 1;
  subjectCode: string;
  questionIds: string[];
  questionIndex: number;
  answers: Record<number, AnswerValue>;
  submitted: Record<number, boolean>;
  secondsElapsed: number;
  isPaused: boolean;
  tipsEnabled: boolean;
  feedbackEnabled: boolean;
  fontSize: FontSize;
  theme: Theme;
  savedAt: string;
};
type Screen = "home" | "exam" | "results";
type FontSize = "small" | "medium" | "large";
type Theme = "light" | "dusk";

const subjectDefinitions: SubjectDefinition[] = [
  { code: "DER101", label: "DER 101", name: "Introducción al Derecho", icon: BookOpen },
  { code: "DER102", label: "DER 102", name: "Lógica y Dialéctica Jurídica", icon: GitBranch },
  { code: "DER104", label: "DER 104", name: "Teoría General del Estado y Sociología Jurídica", icon: Landmark },
  { code: "DER105", label: "DER 105", name: "Expresión Oral y Redacción Jurídica", icon: FilePenLine },
  { code: "DER106", label: "DER 106", name: "Historia y Filosofía del Derecho", icon: History },
  { code: "C10", label: "C10", name: "Investigación", icon: SearchCheck },
];

const questionTypeLabels: Record<BankQuestion["question_type"], string> = {
  single_choice: "Selecciona una respuesta",
  multiple_choice: "Selecciona todas las correctas",
  true_false: "Verdadero o falso",
  fill_blank: "Completa el enunciado",
  matching: "Empareja los conceptos",
  ordering: "Ordena los elementos",
  unknown: "Pregunta",
};

function shuffleItems<T>(items: T[]) {
  const shuffled = [...items];
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const target = Math.floor(Math.random() * (index + 1));
    [shuffled[index], shuffled[target]] = [shuffled[target], shuffled[index]];
  }
  return shuffled;
}

function createOrderingStart(items: string[]) {
  const correct = JSON.stringify(items);
  const reversed = JSON.stringify([...items].reverse());
  let candidate = shuffleItems(items);
  for (let attempt = 0; attempt < 8 && (JSON.stringify(candidate) === correct || (items.length > 2 && JSON.stringify(candidate) === reversed)); attempt += 1) {
    candidate = shuffleItems(items);
  }
  if (JSON.stringify(candidate) === correct && items.length > 1) {
    [candidate[0], candidate[1]] = [candidate[1], candidate[0]];
  }
  return candidate;
}

function formatTime(seconds: number) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
  const remaining = (seconds % 60).toString().padStart(2, "0");
  return `${minutes}:${remaining}`;
}

export default function Home() {
  const [screen, setScreen] = useState<Screen>("home");
  const [allQuestions, setAllQuestions] = useState<BankQuestion[]>([]);
  const [subject, setSubject] = useState<Subject | null>(null);
  const [examQuestions, setExamQuestions] = useState<BankQuestion[]>([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, AnswerValue>>({});
  const [submitted, setSubmitted] = useState<Record<number, boolean>>({});
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [savedAttempt, setSavedAttempt] = useState<SavedAttempt | null>(null);
  const [tipsEnabled, setTipsEnabled] = useState(true);
  const [feedbackEnabled, setFeedbackEnabled] = useState(true);
  const [fontSize, setFontSize] = useState<FontSize>("medium");
  const [theme, setTheme] = useState<Theme>("light");
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [draggedItem, setDraggedItem] = useState<string | null>(null);
  const feedbackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/questions.json")
      .then((response) => response.json())
      .then((data) => setAllQuestions(data.questions || []))
      .catch(() => setAllQuestions([]));
    const saved = window.localStorage.getItem("aula-juridica-attempts");
    if (saved) {
      Promise.resolve().then(() => {
        try {
          setAttempts(JSON.parse(saved));
        } catch {
          window.localStorage.removeItem("aula-juridica-attempts");
        }
      });
    }
    const savedActiveAttempt = window.localStorage.getItem("aula-juridica-active-attempt");
    if (savedActiveAttempt) {
      try {
        setSavedAttempt(JSON.parse(savedActiveAttempt));
      } catch {
        window.localStorage.removeItem("aula-juridica-active-attempt");
      }
    }
  }, []);

  useEffect(() => {
    if (screen !== "exam" || isPaused) return;
    const timer = window.setInterval(() => {
      setSecondsElapsed((value) => value + 1);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [isPaused, screen]);

  const current = examQuestions[questionIndex];
  const selectedAnswer = answers[questionIndex];
  const isSubmitted = submitted[questionIndex];
  const isCorrectAnswer = (question: BankQuestion, answer: AnswerValue | undefined) => {
    if (question.question_type === "ordering") {
      return Array.isArray(answer) && JSON.stringify(answer) === JSON.stringify(question.answer.ordered_items);
    }
    if (question.question_type === "matching") {
      if (!answer || typeof answer !== "object" || Array.isArray(answer)) return false;
      return question.answer.pairs.every((pair) => answer[pair.left] === pair.right);
    }
    if (question.question_type === "multiple_choice") {
      return Array.isArray(answer) &&
        JSON.stringify([...answer].sort()) === JSON.stringify([...question.answer.option_ids].sort());
    }
    return typeof answer === "string" && answer === question.answer.option_ids[0];
  };
  const score = useMemo(
    () => examQuestions.reduce((sum, item, index) => sum + (isCorrectAnswer(item, answers[index]) ? 1 : 0), 0),
    [answers, examQuestions],
  );

  const subjectCatalog = useMemo(
    () => subjectDefinitions.map((item) => ({
      ...item,
      total: allQuestions.filter((question) => question.active && question.subject_code === item.code).length,
    })),
    [allQuestions],
  );

  const availableCounts = subject
    ? [...new Set([10, 20, 30, subject.total].filter((count) => count <= subject.total))]
    : [];

  const createActiveAttemptSnapshot = useCallback((paused = isPaused): SavedAttempt | null => {
    if (!subject || !examQuestions.length) return null;
    return {
      version: 1,
      subjectCode: subject.code,
      questionIds: examQuestions.map((question) => question.id),
      questionIndex,
      answers,
      submitted,
      secondsElapsed,
      isPaused: paused,
      tipsEnabled,
      feedbackEnabled,
      fontSize,
      theme,
      savedAt: new Date().toISOString(),
    };
  }, [answers, examQuestions, feedbackEnabled, fontSize, isPaused, questionIndex, secondsElapsed, subject, submitted, theme, tipsEnabled]);

  useEffect(() => {
    if (screen !== "exam") return;
    const snapshot = createActiveAttemptSnapshot();
    if (snapshot) {
      window.localStorage.setItem("aula-juridica-active-attempt", JSON.stringify(snapshot));
    }
  }, [createActiveAttemptSnapshot, screen]);

  const startAttempt = (count: number) => {
    if (!subject) return;
    const pool = allQuestions.filter(
      (question) =>
        question.subject_code === subject.code &&
        question.active &&
        ((["single_choice", "true_false", "fill_blank"].includes(question.question_type) && question.options.length >= 2 && question.answer.option_ids.length === 1) ||
          (question.question_type === "multiple_choice" && question.options.length >= 2 && question.answer.option_ids.length >= 1) ||
          (question.question_type === "ordering" && question.answer.ordered_items.length >= 2) ||
          (question.question_type === "matching" && question.answer.pairs.length >= 2)),
    );
    const dragQuestion = pool.find((question) => ["ordering", "matching"].includes(question.question_type));
    const shuffled = shuffleItems(pool);
    const selected = dragQuestion
      ? [dragQuestion, ...shuffled.filter((question) => question.id !== dragQuestion.id)].slice(0, Math.min(count, pool.length))
      : shuffled.slice(0, Math.min(count, pool.length));
    const initialAnswers = selected.reduce<Record<number, AnswerValue>>((value, question, index) => {
      if (question.question_type === "ordering") value[index] = createOrderingStart(question.answer.ordered_items);
      return value;
    }, {});
    setExamQuestions(selected);
    setQuestionIndex(0);
    setAnswers(initialAnswers);
    setSubmitted({});
    setSecondsElapsed(0);
    setIsPaused(false);
    setSavedAttempt(null);
    window.localStorage.removeItem("aula-juridica-active-attempt");
    setTipsEnabled(true);
    setFeedbackEnabled(true);
    setFontSize("medium");
    setTheme("light");
    setScreen("exam");
  };

  const saveAndExitAttempt = () => {
    const snapshot = createActiveAttemptSnapshot(true);
    if (snapshot) {
      window.localStorage.setItem("aula-juridica-active-attempt", JSON.stringify(snapshot));
      setSavedAttempt(snapshot);
    }
    setSubject(null);
    setScreen("home");
  };

  const resumeSavedAttempt = () => {
    if (!savedAttempt) return;
    const savedSubject = subjectCatalog.find((item) => item.code === savedAttempt.subjectCode);
    const questionsById = new Map(allQuestions.map((question) => [question.id, question]));
    const restoredQuestions = savedAttempt.questionIds
      .map((id) => questionsById.get(id))
      .filter((question): question is BankQuestion => Boolean(question));
    if (!savedSubject || restoredQuestions.length !== savedAttempt.questionIds.length) {
      window.localStorage.removeItem("aula-juridica-active-attempt");
      setSavedAttempt(null);
      return;
    }
    setSubject(savedSubject);
    setExamQuestions(restoredQuestions);
    setQuestionIndex(Math.min(savedAttempt.questionIndex, restoredQuestions.length - 1));
    setAnswers(savedAttempt.answers || {});
    setSubmitted(savedAttempt.submitted || {});
    setSecondsElapsed(savedAttempt.secondsElapsed || 0);
    setTipsEnabled(savedAttempt.tipsEnabled);
    setFeedbackEnabled(savedAttempt.feedbackEnabled);
    setFontSize(savedAttempt.fontSize || "medium");
    setTheme(savedAttempt.theme || "light");
    setIsPaused(false);
    setScreen("exam");
  };

  const closeAttempt = () => {
    if (!window.confirm("¿Cerrar este intento? Se perderán el progreso y las respuestas guardadas.")) return;
    window.localStorage.removeItem("aula-juridica-active-attempt");
    setSavedAttempt(null);
    setSubject(null);
    setExamQuestions([]);
    setQuestionIndex(0);
    setAnswers({});
    setSubmitted({});
    setSecondsElapsed(0);
    setIsPaused(false);
    setScreen("home");
  };

  const hasCompleteAnswer = (question: BankQuestion, answer: AnswerValue | undefined) => {
    if (question.question_type === "ordering") return Array.isArray(answer) && answer.length === question.answer.ordered_items.length;
    if (question.question_type === "matching") return !!answer && typeof answer === "object" && !Array.isArray(answer) && Object.keys(answer).length === question.answer.pairs.length;
    if (question.question_type === "multiple_choice") return Array.isArray(answer) && answer.length > 0;
    return typeof answer === "string" && answer.length > 0;
  };

  const orderingItems = () => {
    const answer = answers[questionIndex];
    return Array.isArray(answer) ? answer : [];
  };

  const moveOrderingItem = (from: number, to: number) => {
    if (isSubmitted) return;
    const items = [...orderingItems()];
    const [moved] = items.splice(from, 1);
    items.splice(to, 0, moved);
    setAnswers((value) => ({ ...value, [questionIndex]: items }));
  };

  const assignMatch = (left: string, right: string) => {
    if (isSubmitted) return;
    const currentAnswer = answers[questionIndex];
    const mapping = currentAnswer && typeof currentAnswer === "object" && !Array.isArray(currentAnswer) ? currentAnswer : {};
    setAnswers((value) => ({ ...value, [questionIndex]: { ...mapping, [left]: right } }));
    setDraggedItem(null);
  };

  const clearMatch = (left: string) => {
    if (isSubmitted) return;
    const currentAnswer = answers[questionIndex];
    if (!currentAnswer || typeof currentAnswer !== "object" || Array.isArray(currentAnswer)) return;
    const mapping = { ...currentAnswer };
    delete mapping[left];
    setAnswers((value) => ({ ...value, [questionIndex]: mapping }));
  };

  const optionLabel = (question: BankQuestion, optionId: string) => {
    const option = question.options.find((item) => item.id === optionId);
    return option ? `${option.id}. ${option.text}` : optionId;
  };

  const describeAnswer = (question: BankQuestion, answer: AnswerValue | undefined) => {
    if (!answer) return "Sin respuesta";
    if (typeof answer === "string") return optionLabel(question, answer);
    if (Array.isArray(answer)) {
      if (question.question_type === "ordering") return answer.join(" → ");
      return answer.map((item) => optionLabel(question, item)).join(" · ");
    }
    return Object.entries(answer).map(([left, right]) => `${left} → ${right}`).join(" · ");
  };

  const describeCorrectAnswer = (question: BankQuestion) => {
    if (question.question_type === "ordering") return question.answer.ordered_items.join(" → ");
    if (question.question_type === "matching") return question.answer.pairs.map((pair) => `${pair.left} → ${pair.right}`).join(" · ");
    return question.answer.option_ids.map((id) => optionLabel(question, id)).join(" · ");
  };

  const finishAttempt = useCallback(() => {
    if (!subject || !examQuestions.length) return;
    const percentage = Math.round((score / examQuestions.length) * 100);
    const attempt: Attempt = {
      id: crypto.randomUUID(),
      subject: subject.label,
      subjectName: subject.name,
      date: new Intl.DateTimeFormat("es-EC", { dateStyle: "medium", timeStyle: "short" }).format(new Date()),
      score,
      total: examQuestions.length,
      percentage,
      durationSeconds: secondsElapsed,
    };
    const updated = [attempt, ...attempts].slice(0, 20);
    setAttempts(updated);
    window.localStorage.setItem("aula-juridica-attempts", JSON.stringify(updated));
    window.localStorage.removeItem("aula-juridica-active-attempt");
    setSavedAttempt(null);
    setIsPaused(true);
    setScreen("results");
  }, [attempts, examQuestions.length, score, secondsElapsed, subject]);

  useEffect(() => {
    if (screen === "exam" && isSubmitted && feedbackEnabled) {
      window.requestAnimationFrame(() => feedbackRef.current?.focus());
    }
  }, [feedbackEnabled, isSubmitted, questionIndex, screen]);

  useEffect(() => {
    if (screen !== "exam" || !current) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (["INPUT", "SELECT", "TEXTAREA"].includes(target.tagName)) return;
      const choiceTypes = ["single_choice", "true_false", "fill_blank", "multiple_choice"];
      const option = current.options.find((item) => item.id.toLowerCase() === event.key.toLowerCase());
      if (!isSubmitted && choiceTypes.includes(current.question_type) && option) {
        event.preventDefault();
        if (current.question_type === "multiple_choice") {
          const selected = Array.isArray(selectedAnswer) ? [...selectedAnswer] : [];
          const next = selected.includes(option.id) ? selected.filter((id) => id !== option.id) : [...selected, option.id];
          setAnswers((value) => ({ ...value, [questionIndex]: next }));
        } else {
          setAnswers((value) => ({ ...value, [questionIndex]: option.id }));
        }
      }
      if (event.key === "Enter" && feedbackEnabled && !isSubmitted && hasCompleteAnswer(current, selectedAnswer)) {
        event.preventDefault();
        setSubmitted((value) => ({ ...value, [questionIndex]: true }));
      }
      if (event.key === "ArrowRight" && isSubmitted && questionIndex < examQuestions.length - 1) {
        event.preventDefault();
        setQuestionIndex((index) => index + 1);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [current, examQuestions.length, feedbackEnabled, isSubmitted, questionIndex, screen, selectedAnswer]);

  if (screen === "exam" && current && subject) {
    const correct = isCorrectAnswer(current, selectedAnswer);
    return (
      <main className={`exam-app theme-${theme} font-${fontSize}`}>
        <header className="exam-topbar">
          <button className="exam-title" onClick={saveAndExitAttempt}><strong>Simulador de examen final</strong><small>Carrera de Derecho</small></button>
          <div className="exam-identity"><small>{subject.label}</small><strong>{subject.name}</strong></div>
          <div className="exam-tools">
            <div className="tool-group" aria-label="Tamaño de letra">
              <button className={fontSize === "small" ? "active" : ""} onClick={() => setFontSize("small")}>A</button>
              <button className={fontSize === "medium" ? "active medium-a" : "medium-a"} onClick={() => setFontSize("medium")}>A</button>
              <button className={fontSize === "large" ? "active large-a" : "large-a"} onClick={() => setFontSize("large")}>A</button>
            </div>
            <button className="theme-button" onClick={() => setTheme(theme === "light" ? "dusk" : "light")}>
              {theme === "light" ? "Tema azul" : "Tema claro"}
            </button>
            <div className={`clock ${isPaused ? "paused" : ""}`}><small>{isPaused ? "Cronómetro pausado" : "Tiempo empleado"}</small><strong>{formatTime(secondsElapsed)}</strong></div>
          </div>
        </header>

        <div className="attempt-progress"><span style={{ width: `${((questionIndex + 1) / examQuestions.length) * 100}%` }} /></div>

        <section className="exam-body">
          <aside className="navigator">
            <div className="navigator-heading"><strong>Preguntas</strong><span>{Object.keys(answers).length}/{examQuestions.length}</span></div>
            <div className="attempt-controls" aria-label="Acciones del intento">
              <button className="attempt-control pause-control" aria-label={isPaused ? "Continuar intento" : "Pausar intento"} onClick={() => setIsPaused((value) => !value)}>
                {isPaused ? "Continuar" : "Pausar"}
              </button>
              <button className="attempt-control save-control" aria-label="Guardar y salir" onClick={saveAndExitAttempt}>Guardar</button>
              <button className="attempt-control finish-control" aria-label="Terminar y ver resultado" onClick={finishAttempt}>Terminar</button>
              <button className="attempt-control close-control" aria-label="Cerrar intento" onClick={closeAttempt}>Cerrar</button>
            </div>
            <div className="session-options">
              <label><input type="checkbox" disabled={isPaused} checked={tipsEnabled} onChange={(event) => setTipsEnabled(event.target.checked)} /> Consejos</label>
              <label><input type="checkbox" disabled={isPaused} checked={feedbackEnabled} onChange={(event) => setFeedbackEnabled(event.target.checked)} /> Retroalimentación</label>
            </div>
            <div className="question-grid">
              {examQuestions.map((_, index) => (
                <button
                  key={index}
                  className={`${index === questionIndex ? "current" : ""} ${answers[index] ? "answered" : ""}`}
                  disabled={isPaused}
                  onClick={() => setQuestionIndex(index)}
                >{index + 1}</button>
              ))}
            </div>
          </aside>

          <article className={`question-panel ${isPaused ? "attempt-paused" : ""}`}>
            {isPaused && (
              <div className="pause-overlay" role="status">
                <strong>Intento en pausa</strong>
                <p>El cronómetro y la actividad están detenidos. Tu progreso está guardado.</p>
                <button className="primary" onClick={() => setIsPaused(false)}>Continuar intento</button>
              </div>
            )}
            <div className="question-labels"><span>{current.topic}</span><span>Pregunta {questionIndex + 1} de {examQuestions.length}</span></div>
            <span className="question-type">{questionTypeLabels[current.question_type]}</span>
            <h1 className={current.prompt.length > 400 ? "long-prompt" : ""}>{current.prompt}</h1>
            {tipsEnabled && current.tip && <details className="hint"><summary>Consejo disponible</summary><p>{current.tip}</p></details>}
            {["single_choice", "true_false", "fill_blank", "multiple_choice"].includes(current.question_type) && (
              <div
                className={`answer-list ${isSubmitted ? "submitted" : ""}`}
                role={current.question_type === "multiple_choice" ? "group" : "radiogroup"}
                aria-label={questionTypeLabels[current.question_type]}
              >
                {current.options.map((option) => {
                  const multiple = current.question_type === "multiple_choice";
                  const chosen = multiple
                    ? Array.isArray(selectedAnswer) && selectedAnswer.includes(option.id)
                    : selectedAnswer === option.id;
                  const right = isSubmitted && current.answer.option_ids.includes(option.id);
                  const wrong = isSubmitted && chosen && !right;
                  return (
                    <button
                      key={option.id}
                      type="button"
                      role={multiple ? "checkbox" : "radio"}
                      aria-checked={chosen}
                      disabled={isSubmitted}
                      className={`${multiple ? "multiple" : "single"} ${chosen ? "chosen" : ""} ${right ? "right" : ""} ${wrong ? "wrong" : ""}`}
                      onClick={() => {
                        if (isSubmitted) return;
                        if (!multiple) {
                          setAnswers((value) => ({ ...value, [questionIndex]: option.id }));
                          return;
                        }
                        const selected = Array.isArray(selectedAnswer) ? [...selectedAnswer] : [];
                        const next = selected.includes(option.id)
                          ? selected.filter((id) => id !== option.id)
                          : [...selected, option.id];
                        setAnswers((value) => ({ ...value, [questionIndex]: next }));
                      }}
                    >
                      <span className="option-marker">{right ? "✓" : wrong ? "×" : option.id}</span><p>{option.text}</p>{right && <em>Correcta</em>}{wrong && <em>Tu respuesta</em>}
                    </button>
                  );
                })}
              </div>
            )}

            {current.question_type === "ordering" && (
              <div className="drag-question">
                <p className="drag-instruction">Arrastra los elementos hasta colocarlos en el orden correcto.</p>
                <div className="ordering-list">
                  {orderingItems().map((item, index) => (
                    <div
                      key={item}
                      draggable={!isSubmitted}
                      onDragStart={(event) => event.dataTransfer.setData("text/plain", String(index))}
                      onDragOver={(event) => event.preventDefault()}
                      onDrop={(event) => { event.preventDefault(); moveOrderingItem(Number(event.dataTransfer.getData("text/plain")), index); }}
                      className="draggable-row"
                    >
                      <span className="drag-handle">⠿</span><b>{index + 1}</b><p>{item}</p>
                      <span className="move-controls"><button onClick={() => moveOrderingItem(index, Math.max(0, index - 1))}>↑</button><button onClick={() => moveOrderingItem(index, Math.min(orderingItems().length - 1, index + 1))}>↓</button></span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {current.question_type === "matching" && (
              <div className="drag-question matching-question">
                <p className="drag-instruction">Arrastra cada concepto de la derecha hacia su correspondencia. En teléfono, toca el concepto y luego su destino.</p>
                <div className="match-bank">
                  {current.answer.pairs.map((pair) => pair.right).sort().map((right) => (
                    <button
                      key={right}
                      draggable={!isSubmitted}
                      className={draggedItem === right ? "picked" : ""}
                      onDragStart={(event) => { event.dataTransfer.setData("text/plain", right); setDraggedItem(right); }}
                      onClick={() => !isSubmitted && setDraggedItem(right)}
                    >{right}</button>
                  ))}
                </div>
                <div className="match-targets">
                  {current.answer.pairs.map((pair) => {
                    const mapping = selectedAnswer && typeof selectedAnswer === "object" && !Array.isArray(selectedAnswer) ? selectedAnswer : {};
                    const pairCorrect = isSubmitted && mapping[pair.left] === pair.right;
                    const pairWrong = isSubmitted && !!mapping[pair.left] && mapping[pair.left] !== pair.right;
                    return (
                      <div key={pair.left} className={`match-row ${pairCorrect ? "pair-right" : ""} ${pairWrong ? "pair-wrong" : ""}`}>
                        <p>{pair.left}</p>
                        <div className="match-answer">
                          <button
                            className={mapping[pair.left] ? "filled" : ""}
                            disabled={isSubmitted}
                            onDragOver={(event) => event.preventDefault()}
                            onDrop={(event) => { event.preventDefault(); assignMatch(pair.left, event.dataTransfer.getData("text/plain")); }}
                            onClick={() => draggedItem && assignMatch(pair.left, draggedItem)}
                          >{mapping[pair.left] || "Soltar aquí"}</button>
                          {!isSubmitted && mapping[pair.left] && <button className="clear-match" onClick={() => clearMatch(pair.left)} aria-label={`Quitar relación de ${pair.left}`}>×</button>}
                          {pairCorrect && <span className="pair-status">✓ Correcta</span>}
                          {pairWrong && <span className="pair-status">× Revisar</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {feedbackEnabled && isSubmitted && (
              <div
                ref={feedbackRef}
                tabIndex={-1}
                role="status"
                aria-live="polite"
                className={`feedback ${correct ? "feedback-right" : "feedback-wrong"}`}
              >
                <div className="feedback-heading"><span aria-hidden="true">{correct ? "✓" : "×"}</span><strong>{correct ? "¡Correcto!" : "Esta vez no es correcto."}</strong></div>
                {!correct && <p className="feedback-answer"><b>Tu respuesta:</b> {describeAnswer(current, selectedAnswer)}</p>}
                <p className="feedback-answer correct-answer"><b>Respuesta correcta:</b> {describeCorrectAnswer(current)}</p>
                <div className="feedback-explanation">
                  <b>Por qué:</b>
                  <p>{current.explanation || current.feedback_correct}</p>
                </div>
                {!correct && (
                  <div className="feedback-explanation">
                    <b>Por qué no corresponde:</b>
                    <p>{typeof selectedAnswer === "string" && current.why_options_are_wrong?.[selectedAnswer] ? current.why_options_are_wrong[selectedAnswer] : current.feedback_incorrect}</p>
                  </div>
                )}
                {(current.memory_key || current.tip) && <p className="memory-key"><b>Para recordar:</b> {current.memory_key || current.tip}</p>}
                {current.common_confusion && <p className="common-confusion"><b>No confundir:</b> {current.common_confusion}</p>}
              </div>
            )}

            <footer className="exam-actions">
              <button className="secondary" disabled={questionIndex === 0} onClick={() => setQuestionIndex((index) => index - 1)}>Anterior</button>
              <div className="primary-action">
                {feedbackEnabled && !isSubmitted && !hasCompleteAnswer(current, selectedAnswer) && <small>{current.question_type === "matching" ? "Completa todas las relaciones" : "Selecciona una respuesta"}</small>}
                {feedbackEnabled && !isSubmitted ? (
                  <button className="primary" disabled={!hasCompleteAnswer(current, selectedAnswer)} onClick={() => setSubmitted((value) => ({ ...value, [questionIndex]: true }))}>Comprobar</button>
                ) : questionIndex < examQuestions.length - 1 ? (
                  <button className="primary" onClick={() => setQuestionIndex((index) => index + 1)}>Siguiente</button>
                ) : (
                  <button className="primary" onClick={finishAttempt}>Finalizar intento</button>
                )}
              </div>
            </footer>
          </article>
        </section>
      </main>
    );
  }

  if (screen === "results" && subject) {
    const percentage = Math.round((score / examQuestions.length) * 100);
    return (
      <main className="result-page">
        <header className="minimal-header"><button className="exam-title" onClick={() => { setSubject(null); setScreen("home"); }}><strong>Simulador de examen final</strong><small>Carrera de Derecho</small></button></header>
        <section className="result-panel">
          <small>Intento finalizado</small>
          <h1>{subject.name}</h1>
          <div className="result-number"><strong>{percentage}%</strong><span>{score} de {examQuestions.length} respuestas correctas</span></div>
          <p>Completaste el intento en <b>{formatTime(secondsElapsed)}</b>. El resultado quedó guardado en tu historial; tus respuestas individuales no se almacenaron.</p>
          <div><button className="secondary" onClick={() => { setSubject(null); setScreen("home"); }}>Volver a materias</button><button className="primary" onClick={() => setScreen("home")}>Nuevo intento</button></div>
        </section>
      </main>
    );
  }

  return (
    <main className={`catalog-page ${savedAttempt ? "with-saved-attempt" : ""}`}>
      <span className="ambient-glow glow-cyan" aria-hidden="true" />
      <span className="ambient-glow glow-magenta" aria-hidden="true" />
      <header className="minimal-header centered-header">
        <div className="main-title"><h1>Simulador de examen final</h1><p>Carrera de Derecho</p></div>
      </header>

      <section className="catalog-intro">
        <p>Selecciona una asignatura para comenzar. El cronómetro registrará cuánto tardas, sin cerrar el intento automáticamente.</p>
      </section>

      {savedAttempt && (
        <section className="resume-attempt" aria-label="Intento guardado">
          <span>
            <small>Intento guardado</small>
            <strong>{subjectCatalog.find((item) => item.code === savedAttempt.subjectCode)?.name || savedAttempt.subjectCode}</strong>
            <em>Pregunta {savedAttempt.questionIndex + 1} · {formatTime(savedAttempt.secondsElapsed)} empleados</em>
          </span>
          <div>
            <button className="primary" disabled={!allQuestions.length} onClick={resumeSavedAttempt}>Continuar donde quedé</button>
            <button className="secondary danger-outline" onClick={closeAttempt}>Cerrar intento</button>
          </div>
        </section>
      )}

      <section className="subject-catalog">
        {subjectCatalog.map((item, index) => {
          const Icon = item.icon;
          return (
            <button key={item.code} className={`minimal-subject-card accent-${index % 3}`} onClick={() => setSubject(item)}>
              <span className="card-icon"><Icon size={31} strokeWidth={1.8} aria-hidden="true" /></span>
              <span className="card-copy"><strong>{item.name}</strong><em>{item.total} preguntas disponibles</em></span>
              <span className="card-arrow">→</span>
            </button>
          );
        })}
      </section>

      {subject && screen === "home" && (
        <div className="modal-backdrop" role="presentation" onMouseDown={() => setSubject(null)}>
          <section className="count-dialog" role="dialog" aria-modal="true" aria-labelledby="count-title" onMouseDown={(event) => event.stopPropagation()}>
            <button className="dialog-close" onClick={() => setSubject(null)} aria-label="Cerrar">×</button>
            <span className="dialog-kicker">Configurar intento</span>
            <h2 id="count-title">¿Cuántas preguntas quieres responder?</h2>
            <p>{subject.name} · cronómetro sin límite</p>
            <div className="count-options">
              {availableCounts.map((count) => <button key={count} disabled={!allQuestions.length} onClick={() => startAttempt(count)}><strong>{count}</strong><span>preguntas</span></button>)}
            </div>
            {!allQuestions.length && <small className="loading-copy">Preparando el banco de preguntas…</small>}
          </section>
        </div>
      )}
    </main>
  );
}
