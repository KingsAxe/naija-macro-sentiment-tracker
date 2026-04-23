import type { SentimentSummary } from "@/lib/api";

type ControlPanelProps = {
  summary: SentimentSummary;
};

export function ControlPanel({ summary }: ControlPanelProps) {
  const hasAnalysis = summary.total_documents > 0;

  return (
    <aside className="rounded-[1.75rem] border border-cyan-200/10 bg-panel p-5 shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Control Panel</p>
      <h2 className="mt-3 text-2xl font-semibold">Ingestion Runtime</h2>
      <div className="mt-5 grid gap-3 text-sm text-slate-300">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>Backend API</span>
            <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-emerald-300">
              Live
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>File ETL</span>
            <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-emerald-300">
              Loaded
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>Azure AI</span>
            <span
              className={`rounded-full px-3 py-1 ${
                hasAnalysis ? "bg-emerald-400/15 text-emerald-300" : "bg-amber-400/15 text-amber-300"
              }`}
            >
              {hasAnalysis ? "Analyzed" : "Awaiting Data"}
            </span>
          </div>
        </div>
      </div>
      <p className="mt-6 rounded-2xl bg-signal px-4 py-3 text-center font-medium text-slate-950">
        {summary.total_documents} analyzed records
      </p>
    </aside>
  );
}
