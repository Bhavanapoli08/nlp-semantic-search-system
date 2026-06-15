import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import {
  Bot,
  Clock3,
  FileText,
  Highlighter,
  Loader2,
  MessageSquare,
  Send,
  Sparkles,
  UploadCloud,
  User,
} from "lucide-react";
import toast from "react-hot-toast";
import { uploadApi } from "../api/client";

const suggestions = [
  "What dataset is used?",
  "What methodology is used?",
  "What accuracy is achieved?",
  "What are the key contributions?",
  "What are the limitations?",
];

const nowTime = () =>
  new Intl.DateTimeFormat(undefined, { hour: "2-digit", minute: "2-digit" }).format(new Date());

function MarkdownText({ text }) {
  return (
    <div className="space-y-2 text-sm leading-6">
      {String(text || "")
        .split("\n")
        .filter(Boolean)
        .map((line, index) => {
          if (line.startsWith("- ") || line.startsWith("• ")) {
            return <li key={index}>{line.replace(/^[-•]\s*/, "")}</li>;
          }
          return <p key={index}>{line}</p>;
        })}
    </div>
  );
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 px-1 py-2">
      {[0, 1, 2].map((item) => (
        <span
          key={item}
          className="h-2 w-2 animate-pulse rounded-full bg-brand-400"
          style={{ animationDelay: `${item * 120}ms` }}
        />
      ))}
    </div>
  );
}

export default function Upload() {
  const inputRef = useRef(null);
  const chatEndRef = useRef(null);
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [activeSource, setActiveSource] = useState(null);

  const pdfUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  useEffect(() => {
    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl);
    };
  }, [pdfUrl]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.error("Choose a PDF first");
      return;
    }

    setBusy(true);
    setResult(null);
    setMessages([]);
    setActiveSource(null);
    try {
      const data = await uploadApi.upload(file);
      setResult(data);
      setMessages([
        {
          role: "ai",
          text:
            `I analysed **${data.title}** and found ${data.sections?.length || 0} readable sections.\n` +
            "Ask a question and I will answer with source evidence and confidence.",
          time: nowTime(),
          confidence: 96,
          sources: [],
        },
      ]);
      toast.success("PDF analysed");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  const ask = async (text = question) => {
    const clean = text.trim();
    if (!result?.paper_id || !clean) return;

    const userMessage = { role: "user", text: clean, time: nowTime() };
    setMessages((items) => [...items, userMessage]);
    setQuestion("");
    setAsking(true);
    try {
      const data = await uploadApi.ask({ paperId: result.paper_id, question: clean });
      const firstSource = data.sources?.[0] || null;
      setActiveSource(firstSource);
      setMessages((items) => [
        ...items,
        {
          role: "ai",
          text: data.answer,
          time: nowTime(),
          section: data.section,
          confidence: data.confidence,
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Question failed");
    } finally {
      setAsking(false);
    }
  };

  const stats = [
    ["Sections", result?.sections?.length || 0],
    ["Confidence", activeSource?.confidence ? `${activeSource.confidence}%` : "--"],
    ["Mode", "PDF Chat"],
  ];

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/10 dark:text-brand-200">
            <Sparkles size={14} /> AI paper workspace
          </div>
          <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 dark:text-white">
            Chat with your research paper
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">
            Upload a PDF, inspect it side by side, ask follow-up questions, and review cited source
            snippets with confidence scores.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3">
          {stats.map(([label, value]) => (
            <div key={label} className="glass rounded-2xl px-4 py-3 text-center shadow-sm">
              <p className="text-lg font-bold text-slate-950 dark:text-white">{value}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={onSubmit} className="card mb-6 p-4">
        <div className="flex flex-col gap-3 md:flex-row md:items-center">
          <button
            type="button"
            onClick={() => inputRef.current?.click()}
            className="flex flex-1 items-center gap-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-left transition hover:border-brand-300 hover:bg-brand-50/40 dark:border-slate-700 dark:bg-slate-950 dark:hover:bg-slate-800"
          >
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-white text-brand-600 shadow-sm dark:bg-slate-900 dark:text-brand-200">
              <FileText size={22} />
            </span>
            <span>
              <span className="block text-sm font-semibold text-slate-800 dark:text-slate-100">
                {file ? file.name : "Choose PDF"}
              </span>
              <span className="text-xs text-slate-500 dark:text-slate-400">
                PDF viewer, chat, source snippets, and answer confidence
              </span>
            </span>
          </button>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <button type="submit" disabled={busy || !file} className="btn-primary">
            {busy ? <Loader2 size={18} className="animate-spin" /> : <UploadCloud size={18} />}
            {busy ? "Analysing..." : "Analyse"}
          </button>
        </div>
      </form>

      <div className="grid min-h-[680px] gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="card overflow-hidden"
        >
          <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-brand-600 dark:text-brand-300">
                PDF Viewer
              </p>
              <h2 className="text-base font-semibold text-slate-950 dark:text-white">
                {result?.title || file?.name || "No paper loaded"}
              </h2>
            </div>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-200">
              <Highlighter size={14} /> Source aware
            </span>
          </div>

          <div className="h-[610px] bg-slate-100 dark:bg-slate-950">
            {pdfUrl ? (
              <object data={pdfUrl} type="application/pdf" className="h-full w-full">
                <iframe title="PDF preview" src={pdfUrl} className="h-full w-full" />
              </object>
            ) : (
              <div className="flex h-full items-center justify-center p-8 text-center">
                <div>
                  <FileText className="mx-auto text-slate-300" size={54} />
                  <p className="mt-3 text-sm font-medium text-slate-600 dark:text-slate-300">
                    Upload a PDF to preview it here.
                  </p>
                </div>
              </div>
            )}
          </div>

          {activeSource && (
            <div className="border-t border-brand-100 bg-brand-50/70 p-4 dark:border-brand-500/20 dark:bg-brand-500/10">
              <p className="text-xs font-semibold uppercase tracking-wide text-brand-700 dark:text-brand-200">
                Highlighted source: {activeSource.section}
              </p>
              <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-200">
                {activeSource.snippet}
              </p>
            </div>
          )}
        </motion.section>

        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="card flex min-h-[680px] flex-col overflow-hidden"
        >
          <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
            <p className="text-xs font-semibold uppercase tracking-wide text-brand-600 dark:text-brand-300">
              Conversational AI
            </p>
            <h2 className="text-base font-semibold text-slate-950 dark:text-white">
              Ask follow-up questions
            </h2>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto bg-slate-50 p-5 dark:bg-slate-950">
            {messages.length === 0 && (
              <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-slate-900">
                <MessageSquare className="text-brand-500" size={26} />
                <p className="mt-3 text-sm font-medium text-slate-800 dark:text-slate-100">
                  Analyse a paper to start a ChatGPT-style research conversation.
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "ai" && (
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/10 dark:text-brand-200">
                    <Bot size={18} />
                  </span>
                )}
                <div
                  className={`max-w-[84%] rounded-2xl px-4 py-3 shadow-sm ${
                    message.role === "user"
                      ? "bg-brand-600 text-white"
                      : "border border-slate-200 bg-white text-slate-700 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-100"
                  }`}
                >
                  <MarkdownText text={message.text} />
                  <div className="mt-3 flex flex-wrap items-center gap-2 text-xs opacity-80">
                    <Clock3 size={12} /> {message.time}
                    {message.confidence && <span>Confidence: {message.confidence}%</span>}
                    {message.section && <span>Source: {message.section}</span>}
                  </div>
                  {message.sources?.length > 0 && (
                    <div className="mt-3 space-y-2 border-t border-slate-100 pt-3 dark:border-slate-800">
                      {message.sources.map((source, sourceIndex) => (
                        <button
                          key={`${source.section}-${sourceIndex}`}
                          onClick={() => setActiveSource(source)}
                          className="block w-full rounded-xl bg-slate-50 p-3 text-left text-xs text-slate-600 transition hover:bg-brand-50 dark:bg-slate-950 dark:text-slate-300 dark:hover:bg-slate-800"
                        >
                          <span className="font-semibold text-slate-800 dark:text-slate-100">
                            {source.section}
                          </span>
                          <span className="ml-2 text-brand-600 dark:text-brand-300">
                            {source.confidence}% confidence
                          </span>
                          <span className="mt-1 block line-clamp-2">{source.snippet}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {message.role === "user" && (
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-200">
                    <User size={18} />
                  </span>
                )}
              </div>
            ))}

            {asking && (
              <div className="flex gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-brand-100 text-brand-700 dark:bg-brand-500/10 dark:text-brand-200">
                  <Bot size={18} />
                </span>
                <div className="rounded-2xl border border-slate-200 bg-white px-4 py-2 dark:border-slate-800 dark:bg-slate-900">
                  <TypingDots />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="border-t border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-3 flex flex-wrap gap-2">
              {suggestions.map((item) => (
                <button
                  key={item}
                  type="button"
                  disabled={!result || asking}
                  onClick={() => ask(item)}
                  className="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-600 transition hover:border-brand-300 hover:text-brand-700 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-300 dark:hover:border-brand-400"
                >
                  {item}
                </button>
              ))}
            </div>
            <form
              onSubmit={(event) => {
                event.preventDefault();
                ask();
              }}
              className="flex gap-2"
            >
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="input"
                disabled={!result || asking}
                placeholder="Ask about dataset, method, accuracy, limitations..."
              />
              <button type="submit" disabled={asking || !question.trim() || !result} className="btn-primary">
                {asking ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                Ask
              </button>
            </form>
          </div>
        </motion.section>
      </div>
    </div>
  );
}
