import { ControlPanel } from "@/components/control-panel";
import { LiveFeed } from "@/components/live-feed";
import { MacroMoodChart } from "@/components/macro-mood-chart";
import { TargetHeatmap } from "@/components/target-heatmap";

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-10 md:px-10">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <section className="rounded-[2rem] border border-white/10 bg-white/5 px-6 py-8 shadow-panel backdrop-blur">
          <p className="mb-3 text-sm uppercase tracking-[0.3em] text-accent">Naija Macro Monitor</p>
          <div className="grid gap-6 lg:grid-cols-[1.6fr_0.9fr]">
            <div>
              <h1 className="max-w-3xl text-4xl font-semibold tracking-tight md:text-6xl">
                Public mood tracking for the Nigerian economy, built for local-first analysis.
              </h1>
              <p className="mt-4 max-w-2xl text-base text-slate-300 md:text-lg">
                The first dashboard shell is in place. Connect the ingestion pipeline and sentiment
                endpoints to turn these placeholders into live metrics.
              </p>
            </div>
            <ControlPanel />
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
          <MacroMoodChart />
          <TargetHeatmap />
        </section>

        <LiveFeed />
      </div>
    </main>
  );
}
