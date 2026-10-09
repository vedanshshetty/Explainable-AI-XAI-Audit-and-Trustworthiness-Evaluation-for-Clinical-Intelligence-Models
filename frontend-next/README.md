# Clinical Intelligence System — Next.js frontend

React + TypeScript + Tailwind interface for the FastAPI RAG / XAI / Trust backend.

> **Research use only.** Not a medical device.

## Run

```bash
cd frontend-next
npm install
npm run dev
```

Open http://localhost:3000

The backend must be running separately:

```bash
cd ..                       # project root
python run_backend.py       # backend only, safe from any directory
# or
python run.py               # backend + Streamlit UI
```

## Requirements

| Requirement | Version |
|---|---|
| Node.js | 18+ |
| npm | 9+ |
| Next.js | 16.4 |
| React | 19.2 |
| Tailwind CSS | 3.4 |
| TypeScript | 5.7 |

## How it talks to the backend

The browser calls `/api/backend/api/v1/...`, which `next.config.mjs` rewrites
to `http://localhost:8000/...`.

The FastAPI app only allows `http://localhost:8501` in CORS, and this UI runs
on `:3000`. Proxying through Next makes every request same-origin, so **the
backend is not modified at all** — no CORS changes, no `allow_origins` edits.

Point elsewhere without touching code:

```bash
BACKEND_URL=http://192.168.1.10:8000 npm run dev          # Linux / macOS
$env:BACKEND_URL="http://192.168.1.10:8000"; npm run dev # PowerShell
```

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Dev server on `:3000` |
| `npm run build` | Production build |
| `npm start` | Serve the production build |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run lint` | Next lint |

## Views

Navigation in the left sidebar. Each view degrades gracefully when the
corresponding data was not requested.

| View | Shows |
|---|---|
| Analysis | Everything, in order: summary, flags, hypotheses, reasoning, citations, XAI, trust |
| Sample Cases | The five built-in vignettes, loadable in one click |
| Explainable AI | Attribution, grounding, counterfactual, unsupported claims |
| Trust Evaluation | Component bars, overall gauge, audit checklist, abstention |

## Project structure

```
app/
  layout.tsx        Root layout, metadata, Inter webfont
  page.tsx          Single route
  globals.css       Tailwind layers, scrollbars, focus rings
components/
  Dashboard.tsx     State, data fetching, loading/error/consent, view routing
  Sidebar.tsx       Navigation + quick case list
  Topbar.tsx        Search, research badge, backend status, profile
  Results.tsx       The seven result sections
  Charts.tsx        Evidence SVG chart, confidence bars, radial gauge, sparkline
  Anatomy.tsx       Original inline SVG anatomy figures
  ui.tsx            Card, SectionHeading, StatTile, Meter, BarRow, Badge, Skeleton
lib/
  types.ts          Types mirroring the FastAPI response + sample cases
  api.ts            fetch client with typed errors
  utils.ts          Tone helpers, percentage clamps, marker parsing
```

## Anatomy artwork

`components/Anatomy.tsx` contains hand-authored **inline SVG** — lungs with
bronchial tree, heart with ECG trace, brain with neural pathways, and a
cell-pathology figure. They are original vectors: no binary assets, no
licensing constraints, and crisp at any resolution.

Which figure renders is derived from the case text by `figureForText()`, which
scores respiratory, cardiac, neurological and systemic keywords. The pneumonia
case shows lungs; the MI case shows a heart; the stroke case shows a brain.

## Theme

Light and dark, with a segmented switch in the header. The choice persists to
`localStorage` and falls back to the operating system preference on first visit.

A small blocking script in `app/layout.tsx` applies the stored theme before
first paint, so there is no flash of the wrong theme on reload.

All colour comes from CSS variables in `app/globals.css`. Tailwind's palette
maps to those variables (`tailwind.config.ts`), so a single variable swap on
`<html>` restyles the whole app. Both themes are authored separately rather
than one being an inversion of the other: the dark set keeps the same accent
hues at lower lightness so contrast stays readable.

Two tokens exist specifically to keep text legible on coloured fills:

| Token | Purpose |
|---|---|
| `--on-solid` | Foreground for saturated fills; flips between themes |
| `--ink-faint` | Small metadata; tuned in both themes to clear WCAG AA |

Every foreground/background pair used by the UI clears 4.5:1 (normal text) or
3:1 (large text and UI) in **both** themes. The only hard-coded hex values left
in the app are inside `Anatomy.tsx`, where the SVG illustrations carry their own
gradients and are theme-independent by design.

## Search

The header search filters the citation cards by title, journal, PMID and
excerpt. It requires two or more characters and affects nothing else.

## Type safety

`lib/types.ts` is a hand-maintained mirror of the FastAPI response schema. The
UI reads nothing else. **If the backend response changes, update that file.**

`npm run typecheck` passes with no errors.

## Dependencies

Only `next`, `react` and `react-dom`. No charting library, no icon package, no
UI kit — charts and icons are hand-built so the whole surface keeps one visual
language.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| "Backend offline" badge | Backend not running | Start `python run_backend.py` |
| Blank page after install | Stale `.next` | `rm -rf .next && npm run dev` |
| Hydration warning | Dev-only | Reload; do not ship `.next` |
| Port 3000 in use | Another dev server | `npm run dev -- -p 3001` |
| CORS error | Calling the backend directly | Use `/api/backend/*` |
| Port 3000 fetches fail with ECONNREFUSED | Backend down | Check `/api/v1/status` first |