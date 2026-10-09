import type { Config } from "tailwindcss";

/**
 * Colours resolve to CSS variables defined in app/globals.css, so the
 * light/dark toggle only swaps a variable block on <html> and every utility
 * class adapts. The pastel scales are authored separately per theme rather
 * than being an inversion, which keeps text contrast readable in both.
 */
const token = (name: string) => `var(${name})`;

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: token("--canvas"),
        surface: token("--surface"),
        "surface-2": token("--surface-2"),
        rail: token("--rail"),
        track: token("--track"),
        "on-solid": token("--on-solid"),
        overlay: token("--overlay"),

        ink: {
          DEFAULT: token("--ink"),
          soft: token("--ink-2"),
          muted: token("--ink-muted"),
          faint: token("--ink-faint"),
        },
        line: {
          DEFAULT: token("--line"),
          2: token("--line-2"),
        },

        lilac: {
          50: token("--lilac-50"),
          100: token("--lilac-100"),
          200: token("--lilac-200"),
          500: token("--lilac-500"),
          700: token("--lilac-700"),
        },
        mint: {
          50: token("--mint-50"),
          100: token("--mint-100"),
          200: token("--mint-200"),
          500: token("--mint-500"),
          700: token("--mint-700"),
        },
        butter: {
          50: token("--butter-50"),
          100: token("--butter-100"),
          200: token("--butter-200"),
          500: token("--butter-500"),
          700: token("--butter-700"),
        },
        sky: {
          50: token("--sky-50"),
          100: token("--sky-100"),
          200: token("--sky-200"),
          500: token("--sky-500"),
          700: token("--sky-700"),
        },
        blush: {
          50: token("--blush-50"),
          100: token("--blush-100"),
          200: token("--blush-200"),
          500: token("--blush-500"),
          700: token("--blush-700"),
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      borderRadius: {
        xl: "0.875rem",
        "2xl": "1.125rem",
        "3xl": "1.375rem",
      },
      boxShadow: {
        card: "var(--shadow-card)",
        lift: "var(--shadow-lift)",
        pill: "var(--shadow-pill)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(.97)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-500px 0" },
          "100%": { backgroundPosition: "500px 0" },
        },
        breathe: {
          "0%, 100%": { transform: "translateY(0) scale(1)", opacity: "1" },
          "50%": { transform: "translateY(-5px) scale(1.012)", opacity: "0.94" },
        },
        halo: {
          "0%, 100%": { opacity: "0.4", transform: "scale(1)" },
          "50%": { opacity: "0.7", transform: "scale(1.07)" },
        },
        "slide-in": {
          "0%": { opacity: "0", transform: "translateX(10px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        "spin-slow": {
          "0%": { transform: "rotate(0deg)" },
          "100%": { transform: "rotate(360deg)" },
        },
      },
      animation: {
        "fade-up": "fade-up .32s ease-out both",
        "fade-in": "fade-in .3s ease-out both",
        "scale-in": "scale-in .26s ease-out both",
        shimmer: "shimmer 1.4s linear infinite",
        breathe: "breathe 5s ease-in-out infinite",
        halo: "halo 4.5s ease-in-out infinite",
        "slide-in": "slide-in .28s ease-out both",
        "spin-slow": "spin-slow 22s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;