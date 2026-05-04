"use client";

import { useEffect, useState } from "react";

import { AppTopBar } from "@/components/app-top-bar";
import { type SchedulerStatus, getSchedulerStatus } from "@/lib/api";

const DEFAULT_SCHEDULER: SchedulerStatus = {
  enabled: false,
  running: false,
  daily_hour: 6,
  next_run_at: null,
  last_started_at: null,
  last_completed_at: null,
  last_status: null,
  include_news: true,
  skip_news_pages: true,
  news_limit: 20,
};

export function AppTopBarClient() {
  const [scheduler, setScheduler] = useState<SchedulerStatus>(DEFAULT_SCHEDULER);

  async function loadSchedulerStatus() {
    const nextScheduler = await getSchedulerStatus();
    setScheduler(nextScheduler);
  }

  useEffect(() => {
    void loadSchedulerStatus();
  }, []);

  return <AppTopBar scheduler={scheduler} onSchedulerChange={loadSchedulerStatus} />;
}
