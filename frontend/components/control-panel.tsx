import type { SentimentSummary } from "@/lib/api";

type ControlPanelProps = {
  summary: SentimentSummary;
};

export function ControlPanel({ summary }: ControlPanelProps) {
  const hasAnalysis = summary.total_documents > 0;

  return (
    <aside className="rounded-[1.75rem] border border-blue-200/15 bg-panel/95 p-5 shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Control Panel</p>
      <h2 className="mt-3 text-2xl font-semibold">Ingestion Runtime</h2>
      <div className="mt-5 grid gap-3 text-sm text-slate-300">
        <div className="rounded-2xl border border-blue-100/10 bg-blue-950/30 p-4">
          <div className="flex items-center justify-between">
            <span>Backend API</span>
            <span className="rounded-full bg-signal/15 px-3 py-1 text-teal-200">
              Live
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-blue-100/10 bg-blue-950/30 p-4">
          <div className="flex items-center justify-between">
            <span>File ETL</span>
            <span className="rounded-full bg-signal/15 px-3 py-1 text-teal-200">
              Loaded
            </span>
          </div>
        </div>
        <div className="rounded-2xl border border-blue-100/10 bg-blue-950/30 p-4">
          <div className="flex items-center justify-between">
            <span>Azure AI</span>
            <span
              className={`rounded-full px-3 py-1 ${
                hasAnalysis ? "bg-signal/15 text-teal-200" : "bg-amber-400/15 text-amber-300"
              }`}
            >
              {hasAnalysis ? "Analyzed" : "Awaiting Data"}
            </span>
          </div>
        </div>
      </div>
      <p className="mt-6 rounded-2xl bg-gradient-to-r from-primaryBright to-signal px-4 py-3 text-center font-medium text-white">
        {summary.total_documents} analyzed records
      </p>
    </aside>
  );
}
