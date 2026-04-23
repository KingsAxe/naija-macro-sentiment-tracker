import type { SentimentSummary } from "@/lib/api";

type SentimentSignalPlotProps = {
  summary: SentimentSummary;
};

export function SentimentSignalPlot({ summary }: SentimentSignalPlotProps) {
  const total = Math.max(summary.total_documents, 1);
  const points = [
    {
      label: "Positive",
      value: summary.positive,
      description: "Constructive and optimistic language",
      color: "bg-emerald-300",
      tone: "text-emerald-300",
    },
    {
      label: "Neutral",
      value: summary.neutral,
      description: "Informational or mixed-without-lean",
      color: "bg-amber-300",
      tone: "text-amber-300",
    },
    {
      label: "Negative",
      value: summary.negative,
      description: "Concern, dissatisfaction, or risk-heavy language",
      color: "bg-rose-300",
      tone: "text-rose-300",
    },
  ];

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-6 shadow-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Signal Plot</p>
          <h2 className="mt-2 text-2xl font-semibold">Sentiment Distribution</h2>
        </div>
        <p className="text-sm text-neutral-500">Easy-read polarity breakdown</p>
      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {points.map((point) => {
          const percent = Math.round((point.value / total) * 100);
          return (
            <article
              key={point.label}
              className="rounded-2xl border border-white/10 bg-white/5 p-5"
            >
              <div className="flex items-end justify-between gap-4">
                <div>
                  <p className="text-sm text-neutral-500">{point.label}</p>
                  <p className={`mt-2 text-4xl font-semibold ${point.tone}`}>{percent}%</p>
                </div>
                <p className="text-sm text-neutral-300">{point.value} docs</p>
              </div>
              <div className="mt-5 h-40 rounded-[1.5rem] border border-white/10 bg-black/30 px-6 pb-4 pt-5">
                <div className="flex h-full items-end">
                  <div
                    className={`w-full rounded-t-[1rem] ${point.color}`}
                    style={{ height: `${Math.max(percent, point.value ? 8 : 0)}%` }}
                  />
                </div>
              </div>
              <p className="mt-4 text-sm leading-6 text-neutral-400">{point.description}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
