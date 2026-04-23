import type { AssessmentSentiment, TargetSentiment } from "@/lib/api";

type TargetHeatmapProps = {
  targets: TargetSentiment[];
  assessments: AssessmentSentiment[];
};

export function TargetHeatmap({ targets, assessments }: TargetHeatmapProps) {
  const topTargets = targets.slice(0, 6);
  const topAssessments = assessments.slice(0, 4);

  return (
    <section className="rounded-[1.75rem] border border-blue-200/15 bg-panel/95 p-6 shadow-panel">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Target Heatmap</p>
      <h2 className="mt-2 text-2xl font-semibold">Opinion Targets</h2>
      <div className="mt-6 grid gap-3">
        {topTargets.length === 0 ? (
          <p className="rounded-2xl border border-blue-100/10 bg-blue-950/30 p-4 text-sm text-slate-400">
            No opinion targets found yet.
          </p>
        ) : null}
        {topTargets.map((target) => (
          <div
            key={target.target_name}
            className="flex items-center justify-between rounded-2xl border border-blue-100/10 bg-blue-950/30 px-4 py-3"
          >
            <span className="capitalize text-slate-200">{target.target_name}</span>
            <span className="rounded-full bg-accent/10 px-3 py-1 text-sm text-blue-200">
              {target.mentions} mentions
            </span>
          </div>
        ))}
      </div>
      {topAssessments.length > 0 ? (
        <div className="mt-6 border-t border-blue-100/10 pt-5">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Assessment Signals</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {topAssessments.map((assessment) => (
              <span
                key={assessment.assessment_text}
                className="rounded-full border border-blue-100/10 bg-primary/20 px-3 py-1 text-sm text-slate-200"
              >
                {assessment.assessment_text} ({assessment.mentions})
              </span>
            ))}
          </div>
        </div>
      ) : null}
    </section>
  );
}
