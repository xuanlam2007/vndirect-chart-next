import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "VN30 · live chart",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
