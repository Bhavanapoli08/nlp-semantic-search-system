import { useEffect, useState } from "react";
import { Edit3, FileText, Loader2, Plus, Search, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import { papersApi } from "../api/client";

const emptyForm = { title: "", authors: "", abstract: "", summary: "", tags: "" };

export default function Papers() {
  const [items, setItems] = useState(null);
  const [query, setQuery] = useState("");
  const [form, setForm] = useState(emptyForm);
  const [file, setFile] = useState(null);
  const [editing, setEditing] = useState(null);
  const [busy, setBusy] = useState(false);

  const load = (q = query) => {
    setItems(null);
    papersApi
      .list(q.trim() ? { q } : {})
      .then(setItems)
      .catch((err) => toast.error(err?.response?.data?.detail || "Failed to load papers"));
  };

  useEffect(() => {
    load("");
  }, []);

  const resetForm = () => {
    setForm(emptyForm);
    setFile(null);
    setEditing(null);
  };

  const startEdit = (paper) => {
    setEditing(paper);
    setFile(null);
    setForm({
      title: paper.title || "",
      authors: paper.authors || "",
      abstract: paper.abstract || "",
      summary: paper.summary || "",
      tags: (paper.tags || []).join(", "),
    });
  };

  const submit = async (event) => {
    event.preventDefault();
    if (!form.title.trim() && !file) {
      toast.error("Add a title or upload a PDF");
      return;
    }
    setBusy(true);
    try {
      if (editing) {
        await papersApi.update(editing.id, {
          title: form.title,
          authors: form.authors,
          abstract: form.abstract,
          summary: form.summary,
          tags: form.tags.split(",").map((tag) => tag.trim()).filter(Boolean),
        });
        toast.success("Paper updated");
      } else {
        await papersApi.create({ ...form, file });
        toast.success("Paper created");
      }
      resetForm();
      load();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Save failed");
    } finally {
      setBusy(false);
    }
  };

  const remove = async (paper) => {
    if (!window.confirm(`Delete "${paper.title}"? This cannot be undone.`)) return;
    try {
      await papersApi.delete(paper.id);
      setItems((current) => current.filter((item) => item.id !== paper.id));
      toast.success("Paper deleted");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
            <FileText size={14} /> Paper library
          </div>
          <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950">
            Uploaded papers
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Create, edit, filter, and delete your MongoDB-backed paper records.
          </p>
        </div>
        <form
          onSubmit={(event) => {
            event.preventDefault();
            load(query);
          }}
          className="relative w-full md:max-w-sm"
        >
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            className="input pl-9"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Filter by title, author, summary"
          />
        </form>
      </div>

      <form onSubmit={submit} className="card p-5">
        <div className="grid gap-3 md:grid-cols-2">
          <input
            className="input"
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            placeholder="Title"
          />
          <input
            className="input"
            value={form.authors}
            onChange={(event) => setForm({ ...form, authors: event.target.value })}
            placeholder="Authors"
          />
          <input
            className="input md:col-span-2"
            value={form.tags}
            onChange={(event) => setForm({ ...form, tags: event.target.value })}
            placeholder="Tags, comma separated"
          />
          <textarea
            className="input min-h-24 md:col-span-2"
            value={form.abstract}
            onChange={(event) => setForm({ ...form, abstract: event.target.value })}
            placeholder="Abstract"
          />
          <textarea
            className="input min-h-24 md:col-span-2"
            value={form.summary}
            onChange={(event) => setForm({ ...form, summary: event.target.value })}
            placeholder="Summary"
          />
        </div>
        {!editing && (
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            className="mt-3 block w-full text-sm text-slate-500 file:mr-4 file:rounded-lg file:border-0 file:bg-brand-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-brand-700"
          />
        )}
        <div className="mt-4 flex justify-end gap-2">
          {editing && (
            <button type="button" onClick={resetForm} className="btn-outline">
              Cancel
            </button>
          )}
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? <Loader2 className="animate-spin" size={18} /> : <Plus size={18} />}
            {editing ? "Update paper" : "Create paper"}
          </button>
        </div>
      </form>

      <div className="mt-6 grid gap-4">
        {items === null ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-brand-500" size={28} />
          </div>
        ) : items.length === 0 ? (
          <div className="card p-8 text-center text-sm text-slate-500">No papers found.</div>
        ) : (
          items.map((paper) => (
            <div key={paper.id} className="card p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-slate-950">{paper.title}</h2>
                  {paper.authors && <p className="mt-1 text-sm text-slate-500">{paper.authors}</p>}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => startEdit(paper)} className="btn-outline" title="Edit">
                    <Edit3 size={16} />
                  </button>
                  <button onClick={() => remove(paper)} className="btn-outline text-red-600" title="Delete">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              {paper.summary && <p className="mt-3 text-sm leading-6 text-slate-600">{paper.summary}</p>}
              {paper.tags?.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {paper.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-600">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
