"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useSyncExternalStore } from "react";

function subscribeToHydration(): () => void {
  return () => undefined;
}

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const mounted = useSyncExternalStore(subscribeToHydration, () => true, () => false);

  function toggleTheme() {
    if (theme === "light") setTheme("dark");
    else if (theme === "dark") setTheme("system");
    else setTheme("light");
  }

  const icon = !mounted || theme === "light"
    ? <Sun className="h-5 w-5" />
    : theme === "dark"
      ? <Moon className="h-5 w-5" />
      : <Monitor className="h-5 w-5" />;
  const label = !mounted ? "Loading theme..." : theme === "light" ? "Light mode" : theme === "dark" ? "Dark mode" : "System theme";

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="rounded-lg p-2.5 text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
      title={label}
      aria-label={label}
    >
      {icon}
    </button>
  );
}
