"use client";

import { useEffect, useState } from "react";

type DashboardControlsProps = {
  topics: string[];
  sentiments: string[];
  activeTopic: string;
  activeSentiment: string;
  onTopicChange: (value: string) => void;
  onSentimentChange: (value: string) => void;
  onClear: () => void;
  onRefresh?: () => void;
};

export function DashboardControls({
  topics,
  sentiments,
  activeTopic,
  activeSentiment,
  onTopicChange,
  onSentimentChange,
  onClear,
  onRefresh,
}: DashboardControlsProps) {

  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-5 shadow-panel">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Dashboard Controls</p>
          <h2 className="mt-2 text-xl font-semibold">Focus the feed</h2>
        </div>
        <div className="grid gap-3 md:grid-cols-[180px_180px_auto_auto]">
          <label className="grid gap-2 text-sm text-neutral-300">
            Topic
            <select
              className="rounded-xl border border-white/10 bg-black/40 px-3 py-2 text-neutral-100 outline-none ring-white/20 focus:ring-2"
              value={activeTopic}
              onChange={(event) => onTopicChange(event.target.value)}
            >
              <option value="">All topics</option>
              {topics.map((topic) => (
                <option key={topic} value={topic}>
                  {topic}
                </option>
              ))}
            </select>
          </label>
          <label className="grid gap-2 text-sm text-neutral-300">
            Sentiment
            <select
              className="rounded-xl border border-white/10 bg-black/40 px-3 py-2 text-neutral-100 outline-none ring-white/20 focus:ring-2"
              value={activeSentiment}
              onChange={(event) => onSentimentChange(event.target.value)}
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
            className="rounded-xl border border-white/10 px-4 py-2 text-sm font-medium text-neutral-200 transition hover:bg-white/10"
            type="button"
            onClick={onClear}
          >
            Clear
          </button>
          <button
            className="rounded-xl bg-white px-4 py-2 text-sm font-medium text-black transition hover:bg-neutral-200"
            type="button"
            onClick={() => onRefresh?.()}
          >
            Refresh
          </button>
        </div>
      </div>
    </section>
  );
}
