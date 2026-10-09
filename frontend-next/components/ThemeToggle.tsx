"use client";

import { useTheme } from "@/lib/useTheme";
import { cx } from "@/lib/utils";

/**
 * Segmented light/dark switch. Shows a sun and a moon; both icons stay legible
 * in either theme because each sits on its own tinted background.
 */
export function ThemeToggle({ className = "" }: { className?: string }) {
  const { theme, toggle, ready } = useTheme();

  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
      title={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
      className={cx(
        "relative flex h-9 w-[68px] items-center rounded-full border border-line bg-surface p-1",
        "shadow-pill transition-colors duration-200 hover:border-line-2",
        className,
      )}
    >
      {/* sliding thumb */}
      <span
        aria-hidden="true"
        className={cx(
          "absolute top-1 h-7 w-7 rounded-full shadow-pill transition-transform duration-300 ease-out",
          theme === "dark" ? "translate-x-[32px] bg-lilac-500" : "translate-x-0 bg-butter-500",
        )}
      />
      <span
        className={cx(
          "relative z-10 flex h-7 w-7 items-center justify-center transition-colors duration-200",
          theme === "dark" ? "text-ink-faint" : "text-surface",
        )}
      >
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8">
          <circle cx="10" cy="10" r="3.6" />
          <path d="M10 1.8v2M10 16.2v2M18.2 10h-2M3.8 10h-2M15.8 4.2l-1.4 1.4M5.6 14.4l-1.4 1.4M15.8 15.8l-1.4-1.4M5.6 5.6L4.2 4.2" strokeLinecap="round" />
        </svg>
      </span>
      <span
        className={cx(
          "relative z-10 flex h-7 w-7 items-center justify-center transition-colors duration-200",
          theme === "dark" ? "text-surface" : "text-ink-faint",
        )}
      >
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.8">
          <path d="M16.5 12.4A7 7 0 017.6 3.5a7 7 0 108.9 8.9z" strokeLinejoin="round" />
        </svg>
      </span>
      {!ready && <span className="sr-only">Loading theme</span>}
    </button>
  );
}