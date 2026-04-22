const sampleFeed = [
  "Live feed will show ingested headlines and analyzed records once the ETL pipeline is connected.",
  "Scraped news items from Vanguard and Punch will appear here after source ingestion is implemented.",
];

export function LiveFeed() {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel p-6 shadow-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Live Feed</p>
          <h2 className="mt-2 text-2xl font-semibold">Recent Records</h2>
        </div>
        <span className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-400">
          0 documents
        </span>
      </div>
      <div className="mt-6 grid gap-3">
        {sampleFeed.map((item) => (
          <article key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p className="text-sm leading-6 text-slate-300">{item}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
