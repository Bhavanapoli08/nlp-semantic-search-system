import { motion } from "framer-motion";
import { Quote } from "lucide-react";

export default function SectionCard({ section }) {
  if (!section) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card relative overflow-hidden p-5"
    >
      <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-brand-500 to-violet-600" />
      <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
        <Quote size={16} className="text-brand-500" />
        Best matching section
      </div>
      <h4 className="mt-2 text-base font-semibold text-slate-900">
        {section.title}{" "}
        <span className="text-sm font-normal text-slate-500">— {section.section_name}</span>
      </h4>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">{section.text}</p>
      {typeof section.score === "number" && (
        <div className="mt-3 inline-flex rounded-md bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">
          Score: {section.score.toFixed(2)}
        </div>
      )}
    </motion.div>
  );
}
