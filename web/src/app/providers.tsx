"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v13-appRouter";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeContext } from "@/context/ThemeContext";
import { saveMode, getClientMode } from "@/utils/cookie";

const queryClient = new QueryClient();

interface ProvidersProps {
  children: React.ReactNode;
  initialMode: "light" | "dark";
}

export function Providers({ children, initialMode }: ProvidersProps) {
  const [mode, setMode] = useState<"light" | "dark">(initialMode);

  useEffect(() => {
    const saved = getClientMode();
    if (saved !== mode) {
      setMode(saved);
    }
  }, []);

  const toggleTheme = useCallback(() => {
    setMode((prev) => {
      const newMode = prev === "light" ? "dark" : "light";
      saveMode(newMode);
      return newMode;
    });
  }, []);

  const value = useMemo(() => ({ mode, toggleTheme }), [mode, toggleTheme]);

  const theme = mode === "light"
    ? createTheme({ palette: { mode: "light" } })
    : createTheme({ palette: { mode: "dark" } });

  return (
    <ThemeContext.Provider value={value}>
      <AppRouterCacheProvider>
        <QueryClientProvider client={queryClient}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
          </ThemeProvider>
        </QueryClientProvider>
      </AppRouterCacheProvider>
    </ThemeContext.Provider>
  );
}