import { DashboardControls } from "@/components/dashboard-controls";
import { IngestionQualityBoard } from "@/components/ingestion-quality-board";
import { LiveFeed } from "@/components/live-feed";
import {
  getFeed,
  getIngestionRuns,
} from "@/lib/api";

export const dynamic = "force-dynamic";

type OperationsPageProps = {
  searchParams?: Promise<{
    topic?: string;
    sentiment?: string;
  }>;
};

function isPresent(value: string | null): value is string {
  return Boolean(value);
}

export default async function OperationsPage({ searchParams }: OperationsPageProps) {
  const filters = (await searchParams) ?? {};
  const [feed, runs] = await Promise.all([getFeed(), getIngestionRuns()]);

  const topics = Array.from(new Set(feed.map((item) => item.topic_label).filter(isPresent))).sort();
  const sentiments = Array.from(
    new Set(feed.map((item) => item.overall_sentiment).filter(isPresent)),
  ).sort();
  const filteredFeed = feed.filter((item) => {
    const topicMatches = !filters.topic || item.topic_label === filters.topic;
    const sentimentMatches = !filters.sentiment || item.overall_sentiment === filters.sentiment;
    return topicMatches && sentimentMatches;
  });

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
        </section>

        <DashboardControls topics={topics} sentiments={sentiments} />
        <section className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
          <IngestionQualityBoard runs={runs} />
          <LiveFeed items={filteredFeed} totalItems={feed.length} />
        </section>
      </div>
    </main>
  );
}
