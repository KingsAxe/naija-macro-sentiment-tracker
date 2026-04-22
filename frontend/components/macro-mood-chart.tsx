const summary = [
  { label: "Positive", value: "0", tone: "text-emerald-300" },
  { label: "Neutral", value: "0", tone: "text-amber-300" },
  { label: "Negative", value: "0", tone: "text-rose-300" },
];

export function MacroMoodChart() {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel p-6 shadow-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Macro Mood</p>
          <h2 className="mt-2 text-2xl font-semibold">Sentiment Overview</h2>
        </div>
        <p className="text-sm text-slate-400">Awaiting live API data</p>
      </div>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {summary.map((item) => (
          <div
            key={item.label}
            className="rounded-2xl border border-white/10 bg-white/5 p-5"
          >
            <p className="text-sm text-slate-400">{item.label}</p>
            <p className={`mt-3 text-4xl font-semibold ${item.tone}`}>{item.value}</p>
          </div>
        ))}
      </div>
      <div className="mt-8 h-64 rounded-[1.5rem] border border-dashed border-cyan-200/15 bg-slate-950/30 p-6">
        <div className="flex h-full items-center justify-center text-center text-sm text-slate-500">
          Chart placeholder for document-level sentiment trend lines.
        </div>
      </div>
    </section>
  );
}
