import type { Metadata } from "next";

import { AppTopBar } from "@/components/app-top-bar";
import { getSchedulerStatus } from "@/lib/api";

import "./globals.css";

export const metadata: Metadata = {
  title: "Naija Macro Monitor",
  description: "Cloud-hosted Azure sentiment intelligence for Nigeria macroeconomic signals.",
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
