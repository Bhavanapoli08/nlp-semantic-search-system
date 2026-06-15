import { Link, NavLink, useNavigate } from "react-router-dom";
import {
  BarChart3,
  BookOpen,
  Bookmark,
  Files,
  LogOut,
  Moon,
  Search,
  Sun,
  UploadCloud,
  UserRound,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Header({ dark, onToggleTheme }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = () => {
    logout();
    navigate("/login");
  };

  const linkCls = ({ isActive }) =>
    `inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition ${
      isActive
        ? "bg-brand-50 text-brand-700 dark:bg-brand-500/10 dark:text-brand-200"
        : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
    }`;

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/60 bg-white/80 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-3">
        <Link to="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 text-white shadow-md">
            <BookOpen size={18} />
          </span>
          <span>Research Explorer</span>
        </Link>

        {user && (
          <nav className="flex items-center gap-1">
            <NavLink to="/" end className={linkCls}>
              <Search size={16} /> Search
            </NavLink>
            <NavLink to="/upload" className={linkCls}>
              <UploadCloud size={16} /> Upload
            </NavLink>
            <NavLink to="/papers" className={linkCls}>
              <Files size={16} /> Papers
            </NavLink>
            <NavLink to="/saved" className={linkCls}>
              <Bookmark size={16} /> Saved
            </NavLink>
            <NavLink to="/dashboard" className={linkCls}>
              <BarChart3 size={16} /> Dashboard
            </NavLink>
            <NavLink to="/profile" className={linkCls}>
              <UserRound size={16} /> Profile
            </NavLink>
          </nav>
        )}

        <div className="flex items-center gap-2">
          <button onClick={onToggleTheme} className="btn-ghost" title="Toggle theme">
            {dark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          {user ? (
            <>
              <div className="hidden items-center gap-2 sm:flex">
                <div className="grid h-8 w-8 place-items-center rounded-full bg-brand-100 text-sm font-semibold text-brand-700">
                  {(user.name || user.email || "U")[0].toUpperCase()}
                </div>
                <span className="text-sm text-slate-600 dark:text-slate-300">
                  {user.name || user.email}
                </span>
              </div>
              <button onClick={onLogout} className="btn-ghost" title="Sign out">
                <LogOut size={16} />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-ghost">Sign in</Link>
              <Link to="/signup" className="btn-primary">Get started</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
