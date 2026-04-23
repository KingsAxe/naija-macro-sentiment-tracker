import type { SentimentSummary } from "@/lib/api";

type ControlPanelProps = {
  summary: SentimentSummary;
};

export function ControlPanel({ summary }: ControlPanelProps) {
  const hasAnalysis = summary.total_documents > 0;

  return (
    <aside className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-5 shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Control Panel</p>
      <h2 className="mt-3 text-2xl font-semibold">Ingestion Runtime</h2>
      <div className="mt-5 grid gap-3 text-sm text-neutral-300">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>Backend API</span>
            <span className="rounded-full bg-signal/15 px-3 py-1 text-emerald-200">
              Live
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>File ETL</span>
            <span className="rounded-full bg-signal/15 px-3 py-1 text-emerald-200">
              Loaded
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-center justify-between">
            <span>Azure AI</span>
            <span
              className={`rounded-full px-3 py-1 ${
                hasAnalysis ? "bg-signal/15 text-emerald-200" : "bg-amber-400/15 text-amber-300"
              }`}
            >
              {hasAnalysis ? "Analyzed" : "Awaiting Data"}
            </span>
          </div>
        </div>
      </div>
      <p className="mt-6 rounded-2xl border border-white/10 bg-white px-4 py-3 text-center font-medium text-black">
        {summary.total_documents} analyzed records
      </p>
    </aside>
  );
}
