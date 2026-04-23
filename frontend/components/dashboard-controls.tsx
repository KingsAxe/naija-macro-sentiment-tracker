"use client";

import { useRouter, useSearchParams } from "next/navigation";

type DashboardControlsProps = {
  topics: string[];
  sentiments: string[];
};

export function DashboardControls({ topics, sentiments }: DashboardControlsProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const activeTopic = searchParams.get("topic") ?? "";
  const activeSentiment = searchParams.get("sentiment") ?? "";

  function updateFilter(key: "topic" | "sentiment", value: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    router.push(params.toString() ? `/?${params.toString()}` : "/");
  }

  function clearFilters() {
    router.push("/");
  }

  return (
    <section className="rounded-[1.75rem] border border-blue-200/15 bg-panel/95 p-5 shadow-panel">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Dashboard Controls</p>
          <h2 className="mt-2 text-xl font-semibold">Focus the feed</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-[180px_180px_auto_auto]">
          <label className="grid gap-2 text-sm text-slate-300">
            Topic
            <select
              className="rounded-xl border border-blue-100/10 bg-blue-950/60 px-3 py-2 text-slate-100 outline-none ring-blue-300/40 focus:ring-2"
              value={activeTopic}
              onChange={(event) => updateFilter("topic", event.target.value)}
            >
              <option value="">All topics</option>
              {topics.map((topic) => (
                <option key={topic} value={topic}>
                  {topic}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm text-slate-300">
            Sentiment
            <select
              className="rounded-xl border border-blue-100/10 bg-blue-950/60 px-3 py-2 text-slate-100 outline-none ring-blue-300/40 focus:ring-2"
              value={activeSentiment}
              onChange={(event) => updateFilter("sentiment", event.target.value)}
            >
              <option value="">All sentiment</option>
              {sentiments.map((sentiment) => (
                <option key={sentiment} value={sentiment}>
                  {sentiment}
                </option>
              ))}
            </select>
          </label>
          <button
            className="rounded-xl border border-blue-100/10 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10"
            type="button"
            onClick={clearFilters}
          >
            Clear
          </button>
          <button
            className="rounded-xl bg-gradient-to-r from-primaryBright to-signal px-4 py-2 text-sm font-medium text-white transition hover:brightness-110"
            type="button"
            onClick={() => router.refresh()}
          >
            Refresh
          </button>
        </div>
      </div>
    </section>
  );
}
