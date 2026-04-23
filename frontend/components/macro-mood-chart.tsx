import type { SentimentSummary } from "@/lib/api";

type MacroMoodChartProps = {
  summary: SentimentSummary;
};

export function MacroMoodChart({ summary }: MacroMoodChartProps) {
  const cards = [
    { label: "Positive", value: summary.positive, tone: "text-teal-300", bar: "bg-teal-300" },
    { label: "Neutral", value: summary.neutral, tone: "text-amber-300", bar: "bg-amber-300" },
    { label: "Negative", value: summary.negative, tone: "text-rose-300", bar: "bg-rose-300" },
  ];
  const total = Math.max(summary.total_documents, 1);

  return (
    <section className="rounded-[1.75rem] border border-blue-200/15 bg-panel/95 p-6 shadow-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Macro Mood</p>
          <h2 className="mt-2 text-2xl font-semibold">Sentiment Overview</h2>
        </div>
        <p className="text-sm text-slate-400">{summary.total_documents} analyzed documents</p>
      </div>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {cards.map((item) => (
          <div
            key={item.label}
            className="rounded-2xl border border-blue-100/10 bg-blue-950/30 p-5"
          >
            <p className="text-sm text-slate-400">{item.label}</p>
            <p className={`mt-3 text-4xl font-semibold ${item.tone}`}>{item.value}</p>
            <p className="mt-2 text-xs text-slate-500">
              {Math.round((item.value / total) * 100)}% of analyzed records
            </p>
          </div>
        ))}
      </div>
      <div className="mt-8 overflow-hidden rounded-[1.5rem] border border-blue-200/15 bg-slate-950/40">
        {cards.map((item) => (
          <div key={item.label} className="grid grid-cols-[100px_1fr_52px] items-center gap-3 px-5 py-3">
            <span className="text-sm text-slate-400">{item.label}</span>
            <div className="h-3 overflow-hidden rounded-full bg-white/10">
              <div
                className={`h-full rounded-full ${item.bar}`}
                style={{ width: `${Math.max((item.value / total) * 100, item.value ? 4 : 0)}%` }}
              />
            </div>
            <span className="text-right text-sm text-slate-300">{item.value}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
