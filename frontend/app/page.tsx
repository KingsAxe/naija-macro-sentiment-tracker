import { ControlPanel } from "@/components/control-panel";
import { DashboardControls } from "@/components/dashboard-controls";
import { LiveFeed } from "@/components/live-feed";
import { MacroMoodChart } from "@/components/macro-mood-chart";
import { TargetHeatmap } from "@/components/target-heatmap";
import { getAssessments, getFeed, getSentimentSummary, getTargets } from "@/lib/api";

export const dynamic = "force-dynamic";

type HomePageProps = {
  searchParams?: Promise<{
    topic?: string;
    sentiment?: string;
  }>;
};

function isPresent(value: string | null): value is string {
  return Boolean(value);
}

export default async function HomePage({ searchParams }: HomePageProps) {
  const filters = (await searchParams) ?? {};
  const [summary, targets, assessments, feed] = await Promise.all([
    getSentimentSummary(),
    getTargets(),
    getAssessments(),
    getFeed(),
  ]);
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
    <main className="min-h-screen px-6 py-10 md:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <section className="relative overflow-hidden rounded-[2rem] border border-blue-200/15 bg-gradient-to-br from-primary/55 via-panel to-slate-950/80 px-6 py-8 shadow-panel backdrop-blur">
          <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-blue-400/10 blur-3xl" />
          <p className="mb-3 text-sm uppercase tracking-[0.3em] text-accent">Naija Macro Monitor</p>
          <div className="grid gap-6 lg:grid-cols-[1.6fr_0.9fr]">
            <div>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight md:text-6xl">
                Public mood tracking for the Nigerian economy, built for local-first analysis.
              </h1>
              <p className="mt-4 max-w-2xl text-base text-slate-300 md:text-lg">
                Live sentiment, opinion target, and feed views now read from the local FastAPI
                analysis pipeline.
              </p>
            </div>
            <ControlPanel summary={summary} />
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <MacroMoodChart summary={summary} />
          <TargetHeatmap targets={targets} assessments={assessments} />
        </section>

        <DashboardControls topics={topics} sentiments={sentiments} />
        <LiveFeed items={filteredFeed} totalItems={feed.length} />
      </div>
    </main>
  );
}
