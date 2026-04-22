import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Naija Sentiment Tracker",
  description: "Dashboard for macroeconomic sentiment around the Nigerian economy.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
