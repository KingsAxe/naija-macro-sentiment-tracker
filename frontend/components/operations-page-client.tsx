"use client";

import { useEffect, useMemo, useState } from "react";

import { DashboardControls } from "@/components/dashboard-controls";
import { IngestionQualityBoard } from "@/components/ingestion-quality-board";
import { LiveFeed } from "@/components/live-feed";
import { ManualIngestionPanel } from "@/components/manual-ingestion-panel";
import { SourcePerformancePanel } from "@/components/source-performance-panel";
import {
  type FeedItem,
  type IngestionRunSummary,
  getFeed,
  getIngestionRuns,
} from "@/lib/api";

function isPresent(value: string | null): value is string {
  return Boolean(value);
}

export function OperationsPageClient() {
  const [feed, setFeed] = useState<FeedItem[]>([]);
  const [runs, setRuns] = useState<IngestionRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTopic, setActiveTopic] = useState("");
  const [activeSentiment, setActiveSentiment] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setActiveTopic(params.get("topic") ?? "");
    setActiveSentiment(params.get("sentiment") ?? "");
  }, []);

  async function load() {
    setLoading(true);
    setError(null);

    try {
      const [nextFeed, nextRuns] = await Promise.all([getFeed(), getIngestionRuns()]);
      setFeed(nextFeed);
      setRuns(nextRuns);
    } catch {
      setError("Backend call failure");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const topics = useMemo(
    () => Array.from(new Set(feed.map((item) => item.topic_label).filter(isPresent))).sort(),
    [feed],
  );
  const sentiments = useMemo(
    () => Array.from(new Set(feed.map((item) => item.overall_sentiment).filter(isPresent))).sort(),
    [feed],
  );
  const filteredFeed = useMemo(
    () =>
      feed.filter((item) => {
        const topicMatches = !activeTopic || item.topic_label === activeTopic;
        const sentimentMatches = !activeSentiment || item.overall_sentiment === activeSentiment;
        return topicMatches && sentimentMatches;
      }),
    [activeSentiment, activeTopic, feed],
  );

  function syncFilterUrl(nextTopic: string, nextSentiment: string) {
    const params = new URLSearchParams();
    if (nextTopic) {
      params.set("topic", nextTopic);
    }
    if (nextSentiment) {
      params.set("sentiment", nextSentiment);
    }
    const nextUrl = params.toString()
      ? `${window.location.pathname}?${params.toString()}`
      : window.location.pathname;
    window.history.replaceState({}, "", nextUrl);
  }

  function updateTopic(value: string) {
    setActiveTopic(value);
    syncFilterUrl(value, activeSentiment);
  }

  function updateSentiment(value: string) {
    setActiveSentiment(value);
    syncFilterUrl(activeTopic, value);
  }

  function clearFilters() {
    setActiveTopic("");
    setActiveSentiment("");
    window.history.replaceState({}, "", window.location.pathname);
  }

  return (
    <main className="min-h-screen px-6 py-8 md:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <section className="rounded-[2rem] border border-white/10 bg-gradient-to-br from-primary via-panel to-black px-6 py-8 shadow-panel">
          <p className="text-sm uppercase tracking-[0.3em] text-accent">Operations</p>
          <h1 className="mt-3 max-w-3xl text-4xl font-semibold tracking-tight md:text-5xl">
            Source runs, live feed inspection, and ingestion quality in one place.
          </h1>
          <p className="mt-4 max-w-2xl text-base text-neutral-300 md:text-lg">
            This page is for operational review: what was fetched, what was rejected, and what
            content is currently flowing into the sentiment pipeline.
          </p>
          {loading ? <p className="mt-4 text-sm text-neutral-400">Loading live operations data...</p> : null}
          {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
        </section>

        <SourcePerformancePanel runs={runs} />
        <ManualIngestionPanel onComplete={load} />
        <DashboardControls
          topics={topics}
          sentiments={sentiments}
          activeTopic={activeTopic}
          activeSentiment={activeSentiment}
          onTopicChange={updateTopic}
          onSentimentChange={updateSentiment}
          onClear={clearFilters}
          onRefresh={() => void load()}
        />
        <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <IngestionQualityBoard runs={runs} />
          <LiveFeed items={filteredFeed} totalItems={feed.length} />
        </section>
      </div>
    </main>
  );
}
