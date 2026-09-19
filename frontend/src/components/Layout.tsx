import { Menu, Recycle, X } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { DemoBanner } from "./DemoBanner";
import { ToastContainer } from "./ToastContainer";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/analyzer", label: "Waste Analyzer" },
  { to: "/image", label: "Image Analyzer" },
  { to: "/chat", label: "AI Chat" },
  { to: "/documents", label: "Document / RAG" },
  { to: "/history", label: "History" },
  { to: "/about", label: "About Project" },
];

export function Layout() {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-slate-50">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-2 focus:bg-white"
      >
        Skip to content
      </a>
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 transform bg-eco-900 text-white transition md:static md:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between px-4 py-5 border-b border-eco-800">
          <div className="flex items-center gap-2 font-semibold">
            <Recycle className="h-6 w-6 text-eco-200" aria-hidden />
            EcoSort AI
          </div>
          <button
            type="button"
            className="md:hidden rounded p-1 hover:bg-eco-800"
            onClick={() => setOpen(false)}
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
        <nav className="flex flex-col gap-1 p-3" aria-label="Main">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `rounded-lg px-3 py-2 text-sm transition ${
                  isActive ? "bg-eco-700 font-medium" : "hover:bg-eco-800/80"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <p className="mt-auto p-4 text-xs text-eco-200/80">SDG 12 · Responsible Consumption</p>
      </aside>
      {open && (
        <button
          type="button"
          className="fixed inset-0 z-30 bg-black/40 md:hidden"
          aria-label="Close overlay"
          onClick={() => setOpen(false)}
        />
      )}
      <div className="flex min-h-screen flex-1 flex-col md:ml-0">
        <header className="flex items-center gap-3 border-b bg-white px-4 py-3 md:hidden">
          <button
            type="button"
            className="rounded-lg border p-2"
            onClick={() => setOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
          <span className="font-semibold text-eco-800">EcoSort AI</span>
        </header>
        <DemoBanner />
        <main id="main" className="flex-1 p-4 md:p-8 max-w-6xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
      <ToastContainer />
    </div>
  );
}
