"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
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
};
type AnswerValue = string | string[] | Record<string, string>;
type Attempt = { id: string; subject: string; subjectName: string; date: string; score: number; total: number; percentage: number };
type Screen = "home" | "exam" | "results";
type FontSize = "small" | "medium" | "large";
type Theme = "light" | "dusk";

const subjects: Subject[] = [
  { code: "DER101", label: "DER 101", name: "Introducción al Derecho", total: 28, icon: BookOpen },
  { code: "DER102", label: "DER 102", name: "Lógica y Dialéctica Jurídica", total: 20, icon: GitBranch },
  { code: "DER104", label: "DER 104", name: "Teoría General del Estado y Sociología Jurídica", total: 30, icon: Landmark },
  { code: "DER105", label: "DER 105", name: "Expresión Oral y Redacción Jurídica", total: 93, icon: FilePenLine },
  { code: "DER106", label: "DER 106", name: "Historia y Filosofía del Derecho", total: 33, icon: History },
  { code: "C10", label: "C10", name: "Investigación", total: 140, icon: SearchCheck },
];

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
  const [secondsLeft, setSecondsLeft] = useState(3600);
  const [tipsEnabled, setTipsEnabled] = useState(true);
  const [feedbackEnabled, setFeedbackEnabled] = useState(true);
  const [fontSize, setFontSize] = useState<FontSize>("medium");
  const [theme, setTheme] = useState<Theme>("light");
  const [attempts, setAttempts] = useState<Attempt[]>([]);
  const [draggedItem, setDraggedItem] = useState<string | null>(null);

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
  }, []);

  useEffect(() => {
    if (screen !== "exam") return;
    const timer = window.setInterval(() => {
      setSecondsLeft((value) => {
        if (value <= 1) {
          window.clearInterval(timer);
          return 0;
        }
        return value - 1;
      });
    }, 1000);
    return () => window.clearInterval(timer);
  }, [screen]);

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

  const availableCounts = subject
    ? [...new Set([10, 20, 30, subject.total].filter((count) => count <= subject.total))]
    : [];

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
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    const selected = dragQuestion
      ? [dragQuestion, ...shuffled.filter((question) => question.id !== dragQuestion.id)].slice(0, Math.min(count, pool.length))
      : shuffled.slice(0, Math.min(count, pool.length));
    setExamQuestions(selected);
    setQuestionIndex(0);
    setAnswers({});
    setSubmitted({});
    setSecondsLeft(3600);
    setTipsEnabled(true);
    setFeedbackEnabled(true);
    setFontSize("medium");
    setTheme("light");
    setScreen("exam");
  };

  const leaveAttempt = () => {
    setSubject(null);
    setExamQuestions([]);
    setQuestionIndex(0);
    setAnswers({});
    setSubmitted({});
    setScreen("home");
  };

  const hasCompleteAnswer = (question: BankQuestion, answer: AnswerValue | undefined) => {
    if (question.question_type === "ordering") return Array.isArray(answer) && answer.length === question.answer.ordered_items.length;
    if (question.question_type === "matching") return !!answer && typeof answer === "object" && !Array.isArray(answer) && Object.keys(answer).length === question.answer.pairs.length;
    if (question.question_type === "multiple_choice") return Array.isArray(answer) && answer.length > 0;
    return typeof answer === "string" && answer.length > 0;
  };

  const orderingItems = (question: BankQuestion) => {
    const answer = answers[questionIndex];
    return Array.isArray(answer) ? answer : [...question.answer.ordered_items].reverse();
  };

  const moveOrderingItem = (from: number, to: number) => {
    if (isSubmitted) return;
    const items = [...orderingItems(current)];
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
    };
    const updated = [attempt, ...attempts].slice(0, 20);
    setAttempts(updated);
    window.localStorage.setItem("aula-juridica-attempts", JSON.stringify(updated));
    setScreen("results");
  }, [attempts, examQuestions.length, score, subject]);

  useEffect(() => {
    if (screen === "exam" && secondsLeft === 0 && examQuestions.length) {
      const timeout = window.setTimeout(finishAttempt, 0);
      return () => window.clearTimeout(timeout);
    }
  }, [examQuestions.length, finishAttempt, screen, secondsLeft]);

  if (screen === "exam" && current && subject) {
    const correct = isCorrectAnswer(current, selectedAnswer);
    return (
      <main className={`exam-app theme-${theme} font-${fontSize}`}>
        <header className="exam-topbar">
          <button className="exam-title" onClick={leaveAttempt}><strong>Simulador de examen final</strong><small>Carrera de Derecho</small></button>
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
            <div className="clock"><small>Tiempo restante</small><strong>{formatTime(secondsLeft)}</strong></div>
          </div>
        </header>

        <div className="attempt-progress"><span style={{ width: `${((questionIndex + 1) / examQuestions.length) * 100}%` }} /></div>

        <section className="exam-body">
          <aside className="navigator">
            <div className="navigator-heading"><strong>Preguntas</strong><span>{Object.keys(answers).length}/{examQuestions.length}</span></div>
            <div className="question-grid">
              {examQuestions.map((_, index) => (
                <button
                  key={index}
                  className={`${index === questionIndex ? "current" : ""} ${answers[index] ? "answered" : ""}`}
                  onClick={() => setQuestionIndex(index)}
                >{index + 1}</button>
              ))}
            </div>
            <div className="session-options">
              <label><input type="checkbox" checked={tipsEnabled} onChange={(event) => setTipsEnabled(event.target.checked)} /> Consejos</label>
              <label><input type="checkbox" checked={feedbackEnabled} onChange={(event) => setFeedbackEnabled(event.target.checked)} /> Retroalimentación</label>
            </div>
            <button className="exit-link" onClick={leaveAttempt}>Salir del intento</button>
          </aside>

          <article className="question-panel">
            <div className="question-labels"><span>{current.topic}</span><span>Pregunta {questionIndex + 1} de {examQuestions.length}</span></div>
            <h1>{current.prompt}</h1>
            {tipsEnabled && !isSubmitted && <div className="hint"><b>Consejo</b><p>{current.tip}</p></div>}
            {["single_choice", "true_false", "fill_blank", "multiple_choice"].includes(current.question_type) && (
              <div className="answer-list">
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
                      className={`${chosen ? "chosen" : ""} ${right ? "right" : ""} ${wrong ? "wrong" : ""}`}
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
                      <span>{option.id}</span><p>{option.text}</p>{right && <em>Correcta</em>}{wrong && <em>Tu respuesta</em>}
                    </button>
                  );
                })}
              </div>
            )}

            {current.question_type === "ordering" && (
              <div className="drag-question">
                <p className="drag-instruction">Arrastra los elementos hasta colocarlos en el orden correcto.</p>
                <div className="ordering-list">
                  {orderingItems(current).map((item, index) => (
                    <div
                      key={item}
                      draggable={!isSubmitted}
                      onDragStart={(event) => event.dataTransfer.setData("text/plain", String(index))}
                      onDragOver={(event) => event.preventDefault()}
                      onDrop={(event) => { event.preventDefault(); moveOrderingItem(Number(event.dataTransfer.getData("text/plain")), index); }}
                      className="draggable-row"
                    >
                      <span className="drag-handle">⠿</span><b>{index + 1}</b><p>{item}</p>
                      <span className="move-controls"><button onClick={() => moveOrderingItem(index, Math.max(0, index - 1))}>↑</button><button onClick={() => moveOrderingItem(index, Math.min(orderingItems(current).length - 1, index + 1))}>↓</button></span>
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
                    return (
                      <div key={pair.left} className="match-row">
                        <p>{pair.left}</p>
                        <button
                          className={mapping[pair.left] ? "filled" : ""}
                          onDragOver={(event) => event.preventDefault()}
                          onDrop={(event) => { event.preventDefault(); assignMatch(pair.left, event.dataTransfer.getData("text/plain")); }}
                          onClick={() => draggedItem && assignMatch(pair.left, draggedItem)}
                        >{mapping[pair.left] || "Soltar aquí"}</button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {feedbackEnabled && isSubmitted && (
              <div className={`feedback ${correct ? "feedback-right" : "feedback-wrong"}`}>
                <strong>{correct ? "Respuesta correcta" : "Revisa este concepto"}</strong>
                <p>{correct ? current.feedback_correct : current.feedback_incorrect}</p>
              </div>
            )}

            <footer className="exam-actions">
              <button className="secondary" disabled={questionIndex === 0} onClick={() => setQuestionIndex((index) => index - 1)}>Anterior</button>
              {feedbackEnabled && !isSubmitted ? (
                <button className="primary" disabled={!hasCompleteAnswer(current, selectedAnswer)} onClick={() => setSubmitted((value) => ({ ...value, [questionIndex]: true }))}>Comprobar</button>
              ) : questionIndex < examQuestions.length - 1 ? (
                <button className="primary" onClick={() => setQuestionIndex((index) => index + 1)}>Siguiente</button>
              ) : (
                <button className="primary" onClick={finishAttempt}>Finalizar intento</button>
              )}
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
          <p>El resultado quedó guardado en tu historial. Tus respuestas individuales no se almacenaron.</p>
          <div><button className="secondary" onClick={() => { setSubject(null); setScreen("home"); }}>Volver a materias</button><button className="primary" onClick={() => setScreen("home")}>Nuevo intento</button></div>
        </section>
      </main>
    );
  }

  return (
    <main className="catalog-page">
      <span className="ambient-glow glow-cyan" aria-hidden="true" />
      <span className="ambient-glow glow-magenta" aria-hidden="true" />
      <header className="minimal-header centered-header">
        <div className="main-title"><h1>Simulador de examen final</h1><p>Carrera de Derecho</p></div>
      </header>

      <section className="catalog-intro">
        <p>Selecciona una asignatura para comenzar. Cada intento dura una hora.</p>
      </section>

      <section className="subject-catalog">
        {subjects.map((item, index) => {
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
            <p>{subject.name} · 60 minutos</p>
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
