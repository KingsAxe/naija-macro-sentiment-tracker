import type { IngestionRunSummary } from "@/lib/api";

type SourcePerformancePanelProps = {
  runs: IngestionRunSummary[];
};

type SourceTotals = {
  source: string;
  fetched: number;
  inserted: number;
  duplicates: number;
  rejected: number;
  completedRuns: number;
};

function normalizeSource(run: IngestionRunSummary): string {
  return run.source_name ?? run.source_type;
}

function percent(value: number, total: number): string {
  if (total <= 0) {
    return "0%";
  }
  return `${Math.round((value / total) * 100)}%`;
}

export function SourcePerformancePanel({ runs }: SourcePerformancePanelProps) {
  const totalsBySource = runs.reduce<Map<string, SourceTotals>>((acc, run) => {
    const key = normalizeSource(run);
    const current = acc.get(key) ?? {
      source: key,
      fetched: 0,
      inserted: 0,
      duplicates: 0,
      rejected: 0,
      completedRuns: 0,
    };

    current.fetched += run.fetched_count;
    current.inserted += run.inserted_count;
    current.duplicates += run.duplicate_count;
    current.rejected += run.rejected_count;
    if (run.status === "completed") {
      current.completedRuns += 1;
    }

    acc.set(key, current);
    return acc;
  }, new Map());

  const rows = Array.from(totalsBySource.values()).sort((left, right) => right.inserted - left.inserted);
  const maxFetched = Math.max(...rows.map((row) => row.fetched), 1);

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-6 shadow-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Source Performance</p>
          <h2 className="mt-2 text-2xl font-semibold">Acceptance By Source</h2>
        </div>
        <p className="text-sm text-neutral-500">{rows.length} active sources</p>
      </div>

      <div className="mt-6 grid gap-3">
        {rows.length === 0 ? (
          <article className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-neutral-400">
            No source performance data is available yet.
          </article>
        ) : null}
        {rows.map((row) => (
          <article key={row.source} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.18em] text-neutral-500">{row.source}</p>
                <h3 className="mt-2 text-lg font-semibold text-neutral-100">
                  {row.inserted} inserted from {row.fetched} fetched
                </h3>
                <p className="mt-1 text-sm text-neutral-400">
                  {row.completedRuns} completed run{row.completedRuns === 1 ? "" : "s"}
                </p>
              </div>
              <div className="grid gap-2 text-sm text-neutral-300 md:grid-cols-3">
                <span>Accepted: {percent(row.inserted, row.fetched)}</span>
                <span>Duplicates: {percent(row.duplicates, row.fetched)}</span>
                <span>Rejected: {percent(row.rejected, row.fetched)}</span>
              </div>
            </div>

            <div className="mt-4 overflow-hidden rounded-full bg-black/30">
              <div className="flex h-4 w-full">
                <div
                  className="bg-emerald-300"
                  style={{ width: `${(row.inserted / maxFetched) * 100}%` }}
                  title={`Inserted ${row.inserted}`}
                />
                <div
                  className="bg-amber-300"
                  style={{ width: `${(row.duplicates / maxFetched) * 100}%` }}
                  title={`Duplicates ${row.duplicates}`}
                />
                <div
                  className="bg-rose-300"
                  style={{ width: `${(row.rejected / maxFetched) * 100}%` }}
                  title={`Rejected ${row.rejected}`}
                />
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-2 text-xs text-neutral-400">
              <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1">
                Inserted {row.inserted}
              </span>
              <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1">
                Duplicates {row.duplicates}
              </span>
              <span className="rounded-full border border-white/10 bg-black/20 px-3 py-1">
                Rejected {row.rejected}
              </span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
