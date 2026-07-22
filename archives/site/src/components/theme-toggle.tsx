"use client";

import { Moon, Sun, Monitor } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    if (theme === "light") {
      setTheme("dark");
    } else if (theme === "dark") {
      setTheme("system");
    } else {
      setTheme("light");
    }
  };

  const getIcon = () => {
    if (!mounted) return <Sun className="h-4 w-4" />;

    if (theme === "light") {
      return <Sun className="h-4 w-4" />;
    } else if (theme === "dark") {
      return <Moon className="h-4 w-4" />;
    } else {
      return <Monitor className="h-4 w-4" />;
    }
  };

  const getLabel = () => {
    if (!mounted) return "Loading theme...";

    if (theme === "light") return "Light mode";
    if (theme === "dark") return "Dark mode";
    return "System theme";
  };

  return (
    <button
      onClick={toggleTheme}
      className="rounded-lg p-2.5 text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
      title={getLabel()}
      aria-label={getLabel()}
    >
      {getIcon()}
    </button>
  );
}
