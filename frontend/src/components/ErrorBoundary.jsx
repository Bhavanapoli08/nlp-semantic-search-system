import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <div className="max-w-lg rounded-2xl border border-red-100 bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-wide text-red-600">
            Frontend error
          </p>
          <h1 className="mt-2 text-xl font-semibold text-slate-950">
            The app could not render this page.
          </h1>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Clear this site&apos;s browser storage and refresh. If it happens again, open the
            console and check the error shown here.
          </p>
          <pre className="mt-4 max-h-48 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-white">
            {this.state.error?.message || String(this.state.error)}
          </pre>
          <button
            className="btn-primary mt-5"
            onClick={() => {
              localStorage.clear();
              window.location.href = "/signup";
            }}
          >
            Clear storage and reload
          </button>
        </div>
      </div>
    );
  }
}
