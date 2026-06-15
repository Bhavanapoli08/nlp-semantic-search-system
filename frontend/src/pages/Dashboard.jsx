import { useEffect, useState } from "react";
import { Activity, BarChart3, Bookmark, Brain, FileText, Loader2 } from "lucide-react";
import { dashboardApi } from "../api/client";

const cards = [
  ["papers_uploaded", "Papers uploaded", FileText],
  ["saved_papers", "Saved papers", Bookmark],
  ["sections_indexed", "Sections indexed", Brain],
  ["embeddings_stored", "Embeddings stored", BarChart3],
  ["search_latency_ms", "Search latency", Activity],
];

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    dashboardApi.metrics().then(setMetrics).catch(() => setMetrics({}));
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/10 dark:text-brand-200">
          <BarChart3 size={14} /> Research dashboard
        </div>
        <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950 dark:text-white">
          Research intelligence overview
        </h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Track uploaded papers, extracted sections, saved research, and semantic index scale.
        </p>
      </div>

      {!metrics ? (
        <div className="flex justify-center py-20">
          <Loader2 className="animate-spin text-brand-500" size={30} />
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {cards.map(([key, label, Icon]) => (
            <div key={key} className="card p-5 transition hover:-translate-y-1 hover:shadow-lg">
              <div className="flex items-center justify-between">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-200">
                  <Icon size={18} />
                </span>
              </div>
              <p className="mt-5 text-2xl font-bold text-slate-950 dark:text-white">
                {key === "search_latency_ms" ? `${metrics[key] || 0}ms` : metrics[key] || 0}
              </p>
              <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{label}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
