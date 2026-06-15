import { useEffect, useState } from "react";
import { Bookmark, Edit3, Loader2, Save, Trash2 } from "lucide-react";
import toast from "react-hot-toast";
import { savedApi } from "../api/client";
import { Link } from "react-router-dom";

export default function Saved() {
  const [items, setItems] = useState(null);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState({ notes: "", tags: "" });

  const reload = () => {
    savedApi
      .list()
      .then(setItems)
      .catch((err) => toast.error(err?.response?.data?.detail || "Failed to load saved papers"));
  };

  useEffect(() => {
    reload();
  }, []);

  const onUnsave = async (item) => {
    if (!window.confirm(`Remove "${item.title || item.paper_id}" from saved papers?`)) return;
    try {
      await savedApi.unsave(item.id || item.paper_id);
      setItems((arr) => arr.filter((i) => (i.id || i.paper_id) !== (item.id || item.paper_id)));
      toast.success("Removed");
    } catch (err) {
      toast.error("Failed to remove");
    }
  };

  const startEdit = (item) => {
    setEditing(item);
    setForm({ notes: item.notes || "", tags: (item.tags || []).join(", ") });
  };

  const saveEdit = async (event) => {
    event.preventDefault();
    try {
      const updated = await savedApi.update(editing.id || editing.paper_id, {
        notes: form.notes,
        tags: form.tags.split(",").map((tag) => tag.trim()).filter(Boolean),
      });
      setItems((arr) => arr.map((item) => (item.id === updated.id ? updated : item)));
      setEditing(null);
      toast.success("Saved paper updated");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Update failed");
    }
  };

  if (items === null) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="animate-spin text-brand-500" size={28} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <div className="mb-6 flex items-center gap-3">
        <span className="grid h-10 w-10 place-items-center rounded-xl bg-amber-50 text-amber-600">
          <Bookmark size={18} />
        </span>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Saved papers</h1>
          <p className="text-sm text-slate-500">{items.length} saved</p>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="card p-10 text-center">
          <p className="text-lg font-semibold">No saved papers yet</p>
          <p className="mt-1 text-sm text-slate-500">
            Run a search and tap the bookmark to save papers here.
          </p>
          <Link to="/" className="btn-primary mt-5 inline-flex">
            Go to search
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {items.map((p, i) => (
            <div key={p.id || p.paper_id} className="card p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <span className="rounded-md bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">
                    #{i + 1}
                  </span>
                  <h2 className="mt-2 text-lg font-semibold text-slate-950">
                    {p.title || p.paper_id}
                  </h2>
                  {p.authors && <p className="mt-1 text-sm text-slate-500">{p.authors}</p>}
                </div>
              </div>
              {p.summary && <p className="mt-3 text-sm leading-6 text-slate-600">{p.summary}</p>}
              {p.notes && <p className="mt-3 text-sm text-slate-600">{p.notes}</p>}
              <div className="mt-4 flex justify-end gap-2">
                <button onClick={() => startEdit(p)} className="btn-outline">
                  <Edit3 size={16} /> Edit
                </button>
                <button onClick={() => onUnsave(p)} className="btn-outline text-red-600">
                  <Trash2 size={16} /> Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editing && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 px-4">
          <form onSubmit={saveEdit} className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="text-lg font-semibold text-slate-950">Edit saved paper</h2>
            <label className="mb-2 mt-4 block text-sm font-medium text-slate-700">Notes</label>
            <textarea
              className="input min-h-28"
              value={form.notes}
              onChange={(event) => setForm({ ...form, notes: event.target.value })}
            />
            <label className="mb-2 mt-4 block text-sm font-medium text-slate-700">Tags</label>
            <input
              className="input"
              value={form.tags}
              onChange={(event) => setForm({ ...form, tags: event.target.value })}
              placeholder="Tags, comma separated"
            />
            <div className="mt-5 flex justify-end gap-2">
              <button type="button" onClick={() => setEditing(null)} className="btn-outline">
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                <Save size={18} /> Save
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
