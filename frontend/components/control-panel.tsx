export function ControlPanel() {
  return (
    <aside className="rounded-[1.75rem] border border-cyan-200/10 bg-panel p-5 shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Control Panel</p>
      <h2 className="mt-3 text-2xl font-semibold">Ingestion Runtime</h2>
      <div className="mt-5 grid gap-3 text-sm text-slate-300">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>Backend API</span>
            <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-emerald-300">
              Scaffolded
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>CSV ETL</span>
            <span className="rounded-full bg-amber-400/15 px-3 py-1 text-amber-300">
              Pending
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>Azure AI</span>
            <span className="rounded-full bg-rose-400/15 px-3 py-1 text-rose-300">
              Not Wired
            </span>
          </div>
        </div>
      </div>
      <button className="mt-6 w-full rounded-full bg-signal px-4 py-3 font-medium text-slate-950 transition hover:brightness-110">
        Trigger Ingestion
      </button>
    </aside>
  );
}
