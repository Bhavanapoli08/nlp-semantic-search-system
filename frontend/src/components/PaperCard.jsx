import { motion } from "framer-motion";
import { Bookmark, BookmarkCheck, Users } from "lucide-react";

export default function PaperCard({ paper, saved, onToggleSave, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      className="card group relative overflow-hidden p-5 hover:shadow-md transition-shadow"
    >
      <div className="pointer-events-none absolute -right-12 -top-12 h-32 w-32 rounded-full bg-gradient-to-br from-brand-100 to-violet-100 opacity-50 blur-2xl transition group-hover:opacity-90" />

      <div className="relative">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="mb-2 flex items-center gap-2">
              <span className="rounded-md bg-brand-50 px-2 py-0.5 text-xs font-semibold text-brand-700">
                #{paper.rank}
              </span>
              {typeof paper.score === "number" && (
                <span className="rounded-md bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
                  {(paper.score * 100).toFixed(0)}% match
                </span>
              )}
            </div>
            <h3 className="text-lg font-semibold leading-snug text-slate-900">{paper.title}</h3>
            {paper.authors && paper.authors !== "N/A" && (
              <div className="mt-1.5 flex items-center gap-1.5 text-sm text-slate-500">
                <Users size={14} />
                <span className="line-clamp-1">{paper.authors}</span>
              </div>
            )}
          </div>

          {onToggleSave && (
            <button
              onClick={onToggleSave}
              title={saved ? "Remove from saved" : "Save paper"}
              className={`rounded-xl p-2 transition ${
                saved
                  ? "bg-amber-50 text-amber-600"
                  : "bg-slate-50 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
              }`}
            >
              {saved ? <BookmarkCheck size={18} /> : <Bookmark size={18} />}
            </button>
          )}
        </div>

        {paper.summary && (
          <p className="mt-3 text-sm leading-relaxed text-slate-600 line-clamp-4">{paper.summary}</p>
        )}
      </div>
    </motion.div>
  );
}
