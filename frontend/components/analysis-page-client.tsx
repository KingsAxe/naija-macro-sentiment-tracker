"use client";

import { useEffect, useState } from "react";

import { ControlPanel } from "@/components/control-panel";
import { MacroMoodChart } from "@/components/macro-mood-chart";
import { SentimentSignalPlot } from "@/components/sentiment-signal-plot";
import { TargetHeatmap } from "@/components/target-heatmap";
import {
  type AssessmentSentiment,
  type SentimentSummary,
  type TargetSentiment,
  getAssessments,
  getSentimentSummary,
  getTargets,
} from "@/lib/api";

const EMPTY_SUMMARY: SentimentSummary = {
  total_documents: 0,
  positive: 0,
  neutral: 0,
  negative: 0,
};

export function AnalysisPageClient() {
  const [summary, setSummary] = useState<SentimentSummary>(EMPTY_SUMMARY);
  const [targets, setTargets] = useState<TargetSentiment[]>([]);
  const [assessments, setAssessments] = useState<AssessmentSentiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const [nextSummary, nextTargets, nextAssessments] = await Promise.all([
          getSentimentSummary(),
          getTargets(),
          getAssessments(),
        ]);

        if (!active) {
          return;
        }

        setSummary(nextSummary);
        setTargets(nextTargets);
        setAssessments(nextAssessments);
      } catch {
        if (!active) {
          return;
        }

        setError("Could not load dashboard data.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="min-h-screen px-6 py-8 md:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <section className="relative overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-primary via-panel to-black px-6 py-8 shadow-panel backdrop-blur">
          <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-white/5 blur-3xl" />
          <p className="mb-3 text-sm uppercase tracking-[0.3em] text-accent">Naija Macro Monitor</p>
          <div className="grid gap-6 lg:grid-cols-[1.6fr_0.9fr]">
            <div>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight md:text-6xl">
                Cloud-hosted macro sentiment intelligence for the Nigerian economy.
              </h1>
              <p className="mt-4 max-w-2xl text-base text-neutral-300 md:text-lg">
                Premium Azure-backed analysis, tracked ingestion operations, and live macro signal
                views across X and news sources.
              </p>
              {loading ? (
                <p className="mt-4 text-sm text-neutral-400">Loading live analysis data...</p>
              ) : null}
              {error ? <p className="mt-4 text-sm text-rose-300">{error}</p> : null}
            </div>
            <ControlPanel summary={summary} />
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <SentimentSignalPlot summary={summary} />
          <MacroMoodChart summary={summary} />
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <TargetHeatmap targets={targets} assessments={assessments} />
          <section className="rounded-[1.75rem] border border-white/10 bg-panel/95 p-6 shadow-panel">
            <p className="text-xs uppercase tracking-[0.28em] text-neutral-500">Reading Guide</p>
            <h2 className="mt-2 text-2xl font-semibold">How to Read the Analysis</h2>
            <div className="mt-6 grid gap-3 text-sm text-neutral-300">
              <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
                Positive means the language around the economy is constructive or improving.
              </article>
              <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
                Neutral captures informational reporting without a strong directional tone.
              </article>
              <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
                Negative reflects concern, pressure, or dissatisfaction in the source language.
              </article>
              <article className="rounded-2xl border border-white/10 bg-black/20 p-4 text-neutral-400">
                Use the Operations page for source runs, feed inspection, and scheduler behavior.
              </article>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
