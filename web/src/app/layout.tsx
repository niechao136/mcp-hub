import type { Metadata } from "next";
import { Providers } from "./providers";
import { getServerMode } from "@/utils/cookie";
import "./globals.css";

export const metadata: Metadata = {
  title: "MCP Hub",
  description: "MCP Hub Management Platform",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const initialMode = await getServerMode();

  return (
    <html lang="zh-CN" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        <Providers initialMode={initialMode}>{children}</Providers>
      </body>
    </html>
  );
}