import type { FeedItem } from "@/lib/api";

type LiveFeedProps = {
  items: FeedItem[];
};

const sentimentTone: Record<string, string> = {
  positive: "bg-teal-400/15 text-teal-300",
  neutral: "bg-amber-400/15 text-amber-300",
  negative: "bg-rose-400/15 text-rose-300",
  mixed: "bg-blue-300/15 text-blue-200",
};

export function LiveFeed({ items }: LiveFeedProps) {
  return (
    <section className="rounded-[1.75rem] border border-blue-200/15 bg-panel/95 p-6 shadow-panel">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Live Feed</p>
          <h2 className="mt-2 text-2xl font-semibold">Recent Records</h2>
        </div>
        <span className="rounded-full border border-blue-100/10 px-3 py-1 text-sm text-slate-400">
          {items.length} documents
        </span>
      </div>
      <div className="mt-6 grid gap-3">
        {items.length === 0 ? (
          <article className="rounded-2xl border border-blue-100/10 bg-blue-950/30 p-4">
            <p className="text-sm leading-6 text-slate-400">No feed records available yet.</p>
          </article>
        ) : null}
        {items.map((item) => (
          <article key={item.id} className="rounded-2xl border border-blue-100/10 bg-blue-950/30 p-4">
            <div className="mb-3 flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.18em]">
              <span className="text-slate-500">{item.source}</span>
              {item.topic_label ? <span className="text-blue-200">{item.topic_label}</span> : null}
              {item.overall_sentiment ? (
                <span
                  className={`rounded-full px-2 py-1 normal-case tracking-normal ${
                    sentimentTone[item.overall_sentiment] ?? "bg-white/10 text-slate-300"
                  }`}
                >
                  {item.overall_sentiment}
                </span>
              ) : null}
            </div>
            <p className="text-sm leading-6 text-slate-300">{item.content}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
