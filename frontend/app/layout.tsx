import type { Metadata } from "next";

import { AppTopBarClient } from "@/components/app-top-bar-client";

import "./globals.css";

export const metadata: Metadata = {
  title: "Naija Macro Monitor",
  description: "Cloud-hosted Azure sentiment intelligence for Nigeria macroeconomic signals.",
};

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AppTopBarClient />
        {children}
      </body>
    </html>
  );
}
