import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "cg-primary": "#3b82f6",
        "cg-secondary": "#8b5cf6",
        "cg-success": "#10b981",
        "cg-warning": "#f59e0b",
        "cg-danger": "#ef4444",
        "cg-bg-light": "#ffffff",
        "cg-bg-dark": "#0f172a",
        "cg-bg-amoled": "#000000",
        "cg-surface-light": "#f8fafc",
        "cg-surface-dark": "#1e293b",
        "cg-border-light": "#e2e8f0",
        "cg-border-dark": "#334155",
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "sans-serif"],
      },
      spacing: {
        "safe-t": "env(safe-area-inset-top)",
        "safe-r": "env(safe-area-inset-right)",
        "safe-b": "env(safe-area-inset-bottom)",
        "safe-l": "env(safe-area-inset-left)",
      },
    },
  },
  plugins: [],
  darkMode: "class",
};

export default config;
