import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="bg-mesh flex min-h-[70vh] items-center justify-center p-6 text-center">
      <div>
        <p className="text-6xl font-extrabold text-brand-600">404</p>
        <p className="mt-2 text-lg font-semibold text-slate-800">Page not found</p>
        <Link to="/" className="btn-primary mt-6 inline-flex">
          Back to search
        </Link>
      </div>
    </div>
  );
}
