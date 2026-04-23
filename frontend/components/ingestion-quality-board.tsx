import type { IngestionRunSummary } from "@/lib/api";

type IngestionQualityBoardProps = {
  runs: IngestionRunSummary[];
};

type ParsedQaSummary = {
  accepted_count?: number;
  duplicate_count?: number;
  fetched_count?: number;
  macro_candidate_count?: number;
  missing_topic_count?: number;
  rejected_count?: number;
  short_content_count?: number;
  topic_coverage?: Record<string, number>;
  validated_rows?: number;
};

function parseQaSummary(value: string | null): ParsedQaSummary | null {
  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as ParsedQaSummary;
  } catch {
    return null;
  }
}

function formatTimestamp(value: string | null): string {
  if (!value) {
    return "In progress";
  }

  return new Intl.DateTimeFormat("en-NG", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function IngestionQualityBoard({ runs }: IngestionQualityBoardProps) {
  const totalFetched = runs.reduce((sum, run) => sum + run.fetched_count, 0);
  const totalInserted = runs.reduce((sum, run) => sum + run.inserted_count, 0);
  const totalRejected = runs.reduce((sum, run) => sum + run.rejected_count, 0);
  const totalDuplicates = runs.reduce((sum, run) => sum + run.duplicate_count, 0);

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-6 shadow-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Ingestion QA</p>
          <h2 className="mt-2 text-2xl font-semibold">Recent Run Quality</h2>
        </div>
        <p className="text-sm text-neutral-500">{runs.length} recent runs</p>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-4">
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Fetched</p>
          <p className="mt-3 text-3xl font-semibold text-neutral-100">{totalFetched}</p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Inserted</p>
          <p className="mt-3 text-3xl font-semibold text-emerald-300">{totalInserted}</p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Duplicates</p>
          <p className="mt-3 text-3xl font-semibold text-amber-300">{totalDuplicates}</p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Rejected</p>
          <p className="mt-3 text-3xl font-semibold text-rose-300">{totalRejected}</p>
        </article>
      </div>

      <div className="mt-6 grid gap-3">
        {runs.length === 0 ? (
          <article className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-neutral-400">
            No ingestion runs recorded yet.
          </article>
        ) : null}
        {runs.map((run) => {
          const qaSummary = parseQaSummary(run.qa_summary);
          const topicCoverage = Object.entries(qaSummary?.topic_coverage ?? {});

          return (
            <article key={run.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.18em]">
                    <span className="text-neutral-500">{run.source_type}</span>
                    {run.source_name ? <span className="text-neutral-300">{run.source_name}</span> : null}
                    <span
                      className={`rounded-full px-2 py-1 normal-case tracking-normal ${
                        run.status === "completed"
                          ? "bg-emerald-400/15 text-emerald-300"
                          : run.status === "failed"
                            ? "bg-rose-400/15 text-rose-300"
                            : "bg-white/10 text-neutral-300"
                      }`}
                    >
                      {run.status}
                    </span>
                  </div>
                  <h3 className="mt-3 text-lg font-semibold text-neutral-100">
                    Run #{run.id}
                  </h3>
                  <p className="mt-1 text-sm text-neutral-400">
                    Started {formatTimestamp(run.started_at)}. Completed {formatTimestamp(run.completed_at)}.
                  </p>
                </div>
                <div className="grid gap-2 text-sm text-neutral-300 md:grid-cols-2">
                  <span>Fetched: {run.fetched_count}</span>
                  <span>Inserted: {run.inserted_count}</span>
                  <span>Duplicates: {run.duplicate_count}</span>
                  <span>Rejected: {run.rejected_count}</span>
                </div>
              </div>

              {topicCoverage.length > 0 ? (
                <div className="mt-4 flex flex-wrap gap-2">
                  {topicCoverage.map(([topic, count]) => (
                    <span
                      key={`${run.id}-${topic}`}
                      className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-sm text-neutral-300"
                    >
                      {topic}: {count}
                    </span>
                  ))}
                </div>
              ) : null}

              {qaSummary ? (
                <div className="mt-4 grid gap-2 text-sm text-neutral-400 md:grid-cols-3">
                  {qaSummary.macro_candidate_count !== undefined ? (
                    <span>Macro candidates: {qaSummary.macro_candidate_count}</span>
                  ) : null}
                  {qaSummary.missing_topic_count !== undefined ? (
                    <span>Missing topic labels: {qaSummary.missing_topic_count}</span>
                  ) : null}
                  {qaSummary.short_content_count !== undefined ? (
                    <span>Short content rejects: {qaSummary.short_content_count}</span>
                  ) : null}
                  {qaSummary.validated_rows !== undefined ? (
                    <span>Validated rows: {qaSummary.validated_rows}</span>
                  ) : null}
                </div>
              ) : null}

              {run.error_message ? (
                <p className="mt-4 text-sm text-rose-300">{run.error_message}</p>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}
