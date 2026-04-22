const sampleTargets = [
  { name: "inflation", count: 0 },
  { name: "naira", count: 0 },
  { name: "fuel", count: 0 },
  { name: "growth", count: 0 },
];

export function TargetHeatmap() {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel p-6 shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Target Heatmap</p>
      <h2 className="mt-2 text-2xl font-semibold">Opinion Targets</h2>
      <div className="mt-6 grid gap-3">
        {sampleTargets.map((target) => (
          <div
            key={target.name}
            className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
          >
            <span className="capitalize text-slate-200">{target.name}</span>
            <span className="rounded-full bg-cyan-300/10 px-3 py-1 text-sm text-cyan-200">
              {target.count} mentions
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
