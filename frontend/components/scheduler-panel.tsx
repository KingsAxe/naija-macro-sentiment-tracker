"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import type { SchedulerStatus } from "@/lib/api";

type SchedulerPanelProps = {
  scheduler: SchedulerStatus;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

function formatTimestamp(value: string | null): string {
  if (!value) {
    return "Not yet";
  }

  return new Intl.DateTimeFormat("en-NG", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function SchedulerPanel({ scheduler }: SchedulerPanelProps) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function toggleScheduler() {
    setPending(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/ingest/scheduler`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ enabled: !scheduler.enabled }),
      });

      if (!response.ok) {
        throw new Error("Scheduler toggle failed");
      }

      router.refresh();
    } catch {
      setError("Could not update scheduler state.");
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-6 shadow-panel">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Scheduler</p>
          <h2 className="mt-2 text-2xl font-semibold">Daily Refresh Control</h2>
          <p className="mt-2 max-w-xl text-sm text-neutral-400">
            Runs once daily, keeps Azure as the single analysis engine, and can include
            Vanguard/Punch refreshes.
          </p>
        </div>
        <button
          className={`rounded-xl px-4 py-2 text-sm font-medium transition ${
            scheduler.enabled
              ? "border border-white/10 bg-white text-black hover:bg-neutral-200"
              : "border border-white/10 bg-white/5 text-neutral-100 hover:bg-white/10"
          }`}
          type="button"
          onClick={toggleScheduler}
          disabled={pending}
        >
          {pending ? "Updating..." : scheduler.enabled ? "Disable Scheduler" : "Enable Scheduler"}
        </button>
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Status</p>
          <p className="mt-3 text-lg font-semibold text-neutral-100">
            {scheduler.running ? "Running now" : scheduler.enabled ? "Enabled" : "Disabled"}
          </p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Next Run</p>
          <p className="mt-3 text-sm text-neutral-300">{formatTimestamp(scheduler.next_run_at)}</p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Daily Hour</p>
          <p className="mt-3 text-lg font-semibold text-neutral-100">{scheduler.daily_hour}:00</p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">News Scope</p>
          <p className="mt-3 text-sm text-neutral-300">
            {scheduler.include_news ? `Enabled, limit ${scheduler.news_limit}` : "Manual X only"}
          </p>
        </article>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Last Run</p>
          <p className="mt-3 text-sm text-neutral-300">
            Started: {formatTimestamp(scheduler.last_started_at)}
          </p>
          <p className="mt-2 text-sm text-neutral-300">
            Completed: {formatTimestamp(scheduler.last_completed_at)}
          </p>
        </article>
        <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-neutral-500">Execution Mode</p>
          <p className="mt-3 text-sm text-neutral-300">
            {scheduler.skip_news_pages ? "RSS-only news content" : "Fetches full article pages"}
          </p>
          <p className="mt-2 text-sm text-neutral-300">
            Last status: {scheduler.last_status ?? "No scheduled run yet"}
          </p>
        </article>
      </div>

      {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
    </section>
  );
}
