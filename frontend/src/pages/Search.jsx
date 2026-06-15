import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Search as SearchIcon, Sparkles } from "lucide-react";
import toast from "react-hot-toast";
import { savedApi, searchApi } from "../api/client";
import PaperCard from "../components/PaperCard";
import SectionCard from "../components/SectionCard";
import { SkeletonList } from "../components/Skeleton";

const EXAMPLES = [
  "deep learning energy consumption",
  "enzyme design with protein language models",
  "transformer interpretability",
  "gene finding in metagenomes",
];

export default function Search() {
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const [results, setResults] = useState(null);
  const [savedIds, setSavedIds] = useState(new Set());

  useEffect(() => {
    savedApi
      .list()
      .then((items) => setSavedIds(new Set(items.map((i) => i.paper_id))))
      .catch(() => {});
  }, []);

  const runSearch = async (query) => {
    const text = (query ?? q).trim();
    if (!text) return;
    setBusy(true);
    setResults(null);
    try {
      const data = await searchApi.search(text);
      setResults(data);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Search failed");
    } finally {
      setBusy(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    runSearch();
  };

  const toggleSave = async (paper) => {
    const id = paper.title;
    const isSaved = savedIds.has(id);
    try {
      if (isSaved) {
        await savedApi.unsave(id);
        setSavedIds((s) => {
          const next = new Set(s);
          next.delete(id);
          return next;
        });
        toast.success("Removed from saved");
      } else {
        await savedApi.save({
          paper_id: id,
          title: paper.title,
          authors: paper.authors,
          summary: paper.summary,
        });
        setSavedIds((s) => new Set(s).add(id));
        toast.success("Saved!");
      }
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Could not update saved");
    }
  };

  const hasResults = useMemo(
    () => results && (results.sections?.length || results.papers?.length),
    [results]
  );

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
          <Sparkles size={14} /> Semantic search powered by FAISS
        </div>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
          Find research that{" "}
          <span className="bg-gradient-to-r from-brand-600 to-violet-600 bg-clip-text text-transparent">
            matters
          </span>
        </h1>
        <p className="mt-3 text-slate-500">
          Ask in plain language. We'll match against indexed paper summaries and sections.
        </p>
      </motion.div>

      <form onSubmit={onSubmit} className="mt-8">
        <div className="relative">
          <SearchIcon
            size={18}
            className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="e.g. transformer interpretability in vision models"
            className="input h-14 pl-11 pr-32 text-base shadow-md"
          />
          <button
            type="submit"
            disabled={busy || !q.trim()}
            className="btn-primary absolute right-2 top-1/2 -translate-y-1/2 h-10"
          >
            {busy ? "Searching…" : "Search"}
          </button>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
          <span>Try:</span>
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => {
                setQ(ex);
                runSearch(ex);
              }}
              className="rounded-full border border-slate-200 bg-white px-3 py-1 hover:border-brand-300 hover:text-brand-700"
            >
              {ex}
            </button>
          ))}
        </div>
      </form>

      <div className="mt-10">
        {busy && <SkeletonList count={3} />}

        {!busy && results && !hasResults && (
          <div className="card p-10 text-center">
            <p className="text-lg font-semibold text-slate-800">No relevant results</p>
            <p className="mt-1 text-sm text-slate-500">
              Try rephrasing your query in more specific, scientific terms.
            </p>
          </div>
        )}

        {!busy && results?.sections?.length > 0 && (
          <div className="mb-6">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Matching section
            </h2>
            <SectionCard section={results.sections[0]} />
          </div>
        )}

        {!busy && results?.papers?.length > 0 && (
          <div>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
              Matching papers
            </h2>
            <div className="grid gap-4">
              {results.papers.map((p, i) => (
                <PaperCard
                  key={`${p.title}-${i}`}
                  paper={p}
                  index={i}
                  saved={savedIds.has(p.title)}
                  onToggleSave={() => toggleSave(p)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
