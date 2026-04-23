import type { Metadata } from "next";

import { AppTopBar } from "@/components/app-top-bar";
import { getSchedulerStatus } from "@/lib/api";

import "./globals.css";

export const metadata: Metadata = {
  title: "Naija Sentiment Tracker",
  description: "Dashboard for macroeconomic sentiment around the Nigerian economy.",
};

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const scheduler = await getSchedulerStatus();

  return (
    <html lang="en">
      <body>
        <AppTopBar scheduler={scheduler} />
        {children}
      </body>
    </html>
  );
}
