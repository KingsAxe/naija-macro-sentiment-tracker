"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import type { SchedulerStatus } from "@/lib/api";

type AppTopBarProps = {
  scheduler: SchedulerStatus;
  onSchedulerChange?: () => Promise<void> | void;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

function formatTimestamp(value: string | null): string {
  if (!value) {
    return "No run scheduled";
  }

  return new Intl.DateTimeFormat("en-NG", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function AppTopBar({ scheduler, onSchedulerChange }: AppTopBarProps) {
  const pathname = usePathname();
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

      await onSchedulerChange?.();
    } catch {
      setError("Scheduler toggle failed.");
    } finally {
      setPending(false);
    }
  }

  const links = [
    { href: "/", label: "Analysis" },
    { href: "/operations", label: "Operations" },
  ];

  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-black/80 backdrop-blur">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 px-6 py-4 md:px-10 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-center">
          <div>
            <p className="text-xs uppercase tracking-[0.32em] text-neutral-500">Naija Macro Monitor</p>
            <h1 className="mt-1 text-lg font-semibold text-neutral-100">Azure Sentiment Watch</h1>
          </div>
          <nav className="flex flex-wrap gap-2">
            {links.map((link) => {
              const active = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`rounded-full border px-4 py-2 text-sm transition ${
                    active
                      ? "border-white bg-white text-black"
                      : "border-white/10 bg-white/5 text-neutral-300 hover:bg-white/10"
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex flex-col gap-3 xl:items-end">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-neutral-300">
              {scheduler.running ? "Scheduler running" : scheduler.enabled ? "Scheduler enabled" : "Scheduler disabled"}
            </span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-neutral-300">
              Daily at {scheduler.daily_hour}:00
            </span>
            <button
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                scheduler.enabled
                  ? "border border-white/10 bg-white text-black hover:bg-neutral-200"
                  : "border border-white/10 bg-white/5 text-neutral-100 hover:bg-white/10"
              }`}
              type="button"
              onClick={toggleScheduler}
              disabled={pending}
            >
              {pending ? "Updating..." : scheduler.enabled ? "Disable" : "Enable"}
            </button>
          </div>
          <div className="text-xs text-neutral-500">
            Next refresh: {formatTimestamp(scheduler.next_run_at)}
          </div>
          {error ? <div className="text-xs text-rose-300">{error}</div> : null}
        </div>
      </div>
    </header>
  );
}
