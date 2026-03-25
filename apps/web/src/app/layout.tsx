import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hypothesis Lab",
  description: "Web app scaffold for Hypothesis Lab.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
