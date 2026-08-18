"use client";

import "./globals.css";
import { useEffect } from "react";
import { MobileShell } from "@/components/layout/MobileShell";
import { useThemeStore, initTheme } from "@/store/themeStore";
import { useAuth } from "@/hooks/useAuth";
import { Toaster } from "react-hot-toast";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme } = useThemeStore();
  useAuth();

  useEffect(() => {
    initTheme();
  }, []);

  return (
    <html lang="en" className={theme}>
      <head>
        <meta charSet="utf-8" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, viewport-fit=cover"
        />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black" />
        <meta name="apple-mobile-web-app-title" content="CrolGram" />
        <meta name="theme-color" content="#3b82f6" />
        <title>CrolGram</title>
      </head>
      <body>
        <MobileShell>{children}</MobileShell>
        <Toaster position="top-center" />
      </body>
    </html>
  );
}
