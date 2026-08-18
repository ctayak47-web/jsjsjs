import { create } from "zustand";

type Theme = "light" | "dark" | "amoled";

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: "light",
  setTheme: (theme) => {
    set({ theme });
    if (typeof window !== "undefined") {
      localStorage.setItem("cg-theme", theme);
      applyTheme(theme);
    }
  },
  toggleTheme: () => {
    const themes: Theme[] = ["light", "dark", "amoled"];
    const current = get().theme;
    const nextIndex = (themes.indexOf(current) + 1) % themes.length;
    get().setTheme(themes[nextIndex]);
  },
}));

export function applyTheme(theme: Theme) {
  const root = document.documentElement;
  root.classList.remove("light", "dark", "amoled");
  root.classList.add(theme);
}

export function initTheme() {
  if (typeof window === "undefined") return;
  const stored =
    (localStorage.getItem("cg-theme") as Theme) || "light";
  const { setTheme } = useThemeStore.getState();
  setTheme(stored);
}
