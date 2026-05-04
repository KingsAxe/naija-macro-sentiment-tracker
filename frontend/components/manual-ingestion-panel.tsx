"use client";

import { useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type TriggerResponse = {
  status: string;
  detail: string;
  source_name?: string | null;
  fetched_count: number;
  ingested_count: number;
  skipped_count: number;
  duplicate_count: number;
  rejected_count: number;
};

type ManualIngestionPanelProps = {
  onComplete?: () => Promise<void> | void;
};

export function ManualIngestionPanel({ onComplete }: ManualIngestionPanelProps) {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TriggerResponse | null>(null);

  async function triggerIngestion() {
    setPending(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/ingest/trigger`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Ingestion trigger failed");
      }

      const payload = (await response.json()) as TriggerResponse;
      setResult(payload);
      await onComplete?.();
    } catch {
      setError("Could not trigger ingestion.");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-6 shadow-panel">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Manual Trigger</p>
          <h2 className="mt-2 text-2xl font-semibold">Run File Ingestion</h2>
          <p className="mt-2 max-w-xl text-sm text-neutral-400">
            Starts the manual X file ingestion path from the UI and refreshes the operations data
            after completion.
          </p>
        </div>
        <button
          className="rounded-xl border border-white/10 bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-neutral-200 disabled:cursor-not-allowed disabled:opacity-60"
          type="button"
          onClick={triggerIngestion}
          disabled={pending}
        >
          {pending ? "Running..." : "Trigger Ingestion"}
        </button>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-4">
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Fetched</p>
          <p className="mt-3 text-2xl font-semibold text-neutral-100">
            {result?.fetched_count ?? 0}
          </p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Inserted</p>
          <p className="mt-3 text-2xl font-semibold text-emerald-300">
            {result?.ingested_count ?? 0}
          </p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Duplicates</p>
          <p className="mt-3 text-2xl font-semibold text-amber-300">
            {result?.duplicate_count ?? 0}
          </p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Rejected</p>
          <p className="mt-3 text-2xl font-semibold text-rose-300">
            {result?.rejected_count ?? 0}
          </p>
        </article>
      </div>

      {result ? (
        <p className="mt-4 text-sm text-neutral-300">
          {result.detail} Status: {result.status}.
        </p>
      ) : null}
      {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
    </section>
  );
}
