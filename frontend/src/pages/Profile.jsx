import { useState } from "react";
import { Loader2, Save, Trash2, UserRound } from "lucide-react";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { user, updateProfile, deleteAccount } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: user?.name || "",
    email: user?.email || "",
    password: "",
  });
  const [busy, setBusy] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setBusy(true);
    try {
      const payload = {
        name: form.name,
        email: form.email,
        ...(form.password ? { password: form.password } : {}),
      };
      await updateProfile(payload);
      setForm((current) => ({ ...current, password: "" }));
      toast.success("Profile updated");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Update failed");
    } finally {
      setBusy(false);
    }
  };

  const remove = async () => {
    if (!window.confirm("Delete your account and all owned papers? This cannot be undone.")) return;
    try {
      await deleteAccount();
      toast.success("Account deleted");
      navigate("/signup");
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Delete failed");
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <div className="mb-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
          <UserRound size={14} /> User profile
        </div>
        <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950">Profile settings</h1>
      </div>

      <form onSubmit={submit} className="card p-6">
        <label className="mb-2 block text-sm font-medium text-slate-700">Name</label>
        <input
          className="input"
          value={form.name}
          onChange={(event) => setForm({ ...form, name: event.target.value })}
        />
        <label className="mb-2 mt-4 block text-sm font-medium text-slate-700">Email</label>
        <input
          className="input"
          type="email"
          value={form.email}
          onChange={(event) => setForm({ ...form, email: event.target.value })}
        />
        <label className="mb-2 mt-4 block text-sm font-medium text-slate-700">New password</label>
        <input
          className="input"
          type="password"
          value={form.password}
          onChange={(event) => setForm({ ...form, password: event.target.value })}
          placeholder="Leave blank to keep current password"
        />
        <div className="mt-5 flex justify-end">
          <button type="submit" disabled={busy} className="btn-primary">
            {busy ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
            Save changes
          </button>
        </div>
      </form>

      <div className="mt-6 rounded-2xl border border-red-100 bg-red-50 p-6">
        <h2 className="text-base font-semibold text-red-900">Delete account</h2>
        <p className="mt-1 text-sm text-red-700">
          This removes your user profile, uploaded papers, and saved papers from MongoDB.
        </p>
        <button onClick={remove} className="btn mt-4 bg-red-600 text-white hover:bg-red-700">
          <Trash2 size={18} /> Delete account
        </button>
      </div>
    </div>
  );
}
