# Design System: learn.willmccarty.io

A rigorous, local-first technical learning and L4-L6 interview preparation engine hosted on Cloudflare Pages and backed by high-agency CLI harnesses.

---

## 1. Visual Theme & Atmosphere
- **Atmosphere**: Technical Cockpit meets Architecture Studio. Deeply grounded, utilitarian, and distraction-free. The feeling is that of a high-performance terminal instrument built for engineers mastering distributed systems, security architectures, invariant proofs, and differential privacy.
- **Density**: Cockpit Dense (Level 8/10) with crisp 1px structural borders, compact data rows, and persistent state indicators. Every pixel conveys signal; zero decorative fluff.
- **Variance**: Asymmetric Technical Grid (Level 6/10). Left-heavy structural navigation, sticky priority quick-bar, and a balanced split between problem specifications, code sandboxes, and rubric telemetry.
- **Motion**: Fluid Micro-Engine (Level 6/10). Purposeful spring physics via CSS `linear()` and progressive view transitions; no gratuitous bouncing or distracting animations.

---

## 2. Color Palette & Roles
Grounded in `willmccarty.io`'s signature cobalt paired with calibrated slate neutrals. Strict high-contrast readability in both light and dark modes.

### Light Mode (`data-theme="light"`)
- **Canvas White**: `#F8FAFC` (Slate-50) — Primary application background
- **Surface Pure**: `#FFFFFF` — Cards, table rows, and active pane surfaces
- **Cobalt Accent**: `#0B5CAD` — Primary action buttons, active tab indicators, focus rings
- **Cobalt Deep**: `#084482` — Interactive hover states for primary buttons
- **Charcoal Ink**: `#0F172A` (Slate-900) — Primary headings, titles, and body text
- **Muted Slate**: `#475569` (Slate-600) — Secondary labels, descriptions, and metadata
- **Faint Slate**: `#94A3B8` (Slate-400) — Disabled states and subtle icons
- **Whisper Border**: `#E2E8F0` (Slate-200) — 1px container boundaries and divider lines
- **Code Background**: `#0F172A` (Slate-900) — High-contrast dark container for code blocks
- **Success Emerald**: `#059669` — Passed tests, high ratings, and positive bar decisions
- **Warning Amber**: `#D97706` — Partial gaps, warnings, and hints remaining
- **Danger Crimson**: `#DC2626` — Surrenders, critical gaps, and test regressions

### Dark Mode (`data-theme="dark"`)
- **Canvas Deep**: `#020617` (Slate-950) — Deep space dark background
- **Surface Elevated**: `#0F172A` (Slate-900) — Elevated cards, panels, and modals
- **Cobalt Glow**: `#60A5FA` (Cobalt-400) — High-legibility accent for dark mode
- **Cobalt Hover**: `#93C5FD` (Cobalt-300) — Dark mode hover state
- **Text Crisp**: `#F8FAFC` (Slate-50) — Primary headings and high-contrast text
- **Text Subdued**: `#94A3B8` (Slate-400) — Secondary descriptions and metadata
- **Border Crisp**: `#1E293B` (Slate-800) — 1px dark structural dividers
- **Code Background**: `#020617` (Slate-950) — Recessed dark editor surface

---

## 3. Typography Rules
System fonts with instant zero-latency loading and zero external network requests.

- **Display & Headings**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
  - Controlled weight hierarchy (`font-weight: 700` for titles, `600` for section labels).
  - Letter spacing: `-0.02em` on titles > 20px, tight tracking without clipping.
- **Body & Controls**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
  - Max line length: 72ch for reading curricula fundamentals.
  - Line height: 1.5 for dense information grids; 1.65 for long-form reference documentation.
- **Monospace & Telemetry**: `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace`
  - Used for: Code syntax, API routes, topic slugs, timestamps, ratings, diffs, and benchmark scores.
  - Numbers: `font-variant-numeric: tabular-nums` enforced globally on all metrics, ratings gauges, and countdown timers to eliminate layout jitter during live updates.
- **Banned Typography**:
  - `Inter` is banned.
  - Generic serif fonts (`Times New Roman`, `Georgia`, `Garamond`) are strictly banned across all views.
  - Variable font CDNs (`Google Fonts`, `Typekit`, `jsDelivr`) are prohibited — 100% self-contained system fonts only.

---

## 4. Component Stylings

### Buttons & Interactive Controls
- **Tactile Feedback**: Active buttons depress by `transform: translateY(1px)`.
- **Primary Buttons**: Solid Cobalt `#0B5CAD` (`#60A5FA` in dark), high-contrast white text, zero outer glow or gradient sheen.
- **Secondary / Ghost**: Slate border `1px solid var(--border-light)`, transparent background, color transition on hover.
- **No Neon Flares**: Zero box-shadow glows or pulsating halo rings.

### Badges & Status Indicators
- **Domain Pills**: Compact 11px uppercase pills (`font-family: var(--font-mono)`), 2px 6px padding.
- **Difficulty Tiers**: Calibrated badges for `STARTER`, `L4`, `L5`, and `L6` indicating engineering seniority requirements.
- **Live Connection Pill**: 6px pulsing dot with color status (`#059669` local loopback, `#2563eb` tailnet, `#dc2626` offline).

### Rating Gauges & Progress Meters
- Fixed-width progress tracks (`background: var(--bg-hover)`) with rounded 2px inner bars.
- `tabular-nums` numerical scores (e.g., `3.8 / 5.0`) aligned right to avoid line shifts.

### Code Blocks & Micro-Highlighter
- In-memory regex tokenization for Python, Go, Rust, and YAML.
- High-contrast syntax tokens: comments (`#64748B`), keywords (`#93C5FD`), strings (`#86EFAC`), types (`#FDE047`).
- Zero external syntax highlighting libraries (no Prism.js, no Highlight.js); 100% pure vanilla micro-highlighter.

---

## 5. Layout Principles
- **Spatial Isolation**: Absolute positioning is banned for layout flows; all content uses modern CSS Grid and Flexbox.
- **Viewport Bounds**: Section layouts use `min-height: 100dvh` rather than `100vh` to prevent iOS/mobile URL bar resizing reflows.
- **Zero Horizontal Overflow**: `max-width: 100%` and `overflow-x: hidden` are strictly enforced across all viewports.
- **Asymmetric Split**: Two-pane workspace for problem analysis (left: prompt & rubric; right: candidate workspace and transcript).
- **Collapsible Responsive Design**: Multi-column grids automatically collapse to a single column on viewports under 768px.

---

## 6. Motion & Interaction
- **CSS Spring Physics**: Transition timing utilizes physics-calibrated spring curves rather than generic linear transitions:
  ```css
  --ease-spring: linear(
    0, 0.006, 0.025 2.8%, 0.101 6.1%, 0.539 18.9%, 0.721 25.3%, 0.849 31.5%,
    0.932 38.4%, 0.978 45.9%, 1 100%
  );
  --transition-fast: 150ms var(--ease-spring);
  --transition-normal: 250ms var(--ease-spring);
  ```
- **View Transitions**: Screen transitions leverage the modern Web API `document.startViewTransition()` with fallback for graceful progressive enhancement:
  ```javascript
  if (document.startViewTransition) {
    document.startViewTransition(() => renderView(target));
  } else {
    renderView(target);
  }
  ```
- **Hardware-Accelerated Properties**: Only `transform` and `opacity` are animated. Layout properties (`top`, `left`, `width`, `height`, `margin`, `padding`) must never be animated.
- **Reduced Motion**: Full support for `@media (prefers-reduced-motion: reduce)` disabling all transitions and spring movements.

---

## 7. Anti-Patterns Banned (Strict AI-Slop Prohibitions)
1. **No Emojis Anywhere**: Zero decorative emojis in navigation, headers, status messages, or badges.
2. **No Neon / Glowing Halos**: No blur glows around primary buttons or cards.
3. **No Fabricated / Fake Statistics**: No invented numbers like "99.99% Uptime", "124ms SLA", or "15.4k Happy Engineers". Real telemetry only.
4. **No Marketing Buzzwords**: Banned terms include "Elevate", "Next-Gen", "Seamless", "Unleash", "Revolutionary", "AI-Powered Magic".
5. **No 3-Column Equal Feature Cards**: Banned lazy card triples. Data is displayed via searchable tabular lists and hierarchical domain matrices.
6. **No External CDN Assets**: Zero `<script>` or `<link>` tags fetching from unpkg, cdnjs, Google Fonts, or Cloudflare CDN. The entire app is 100% self-contained.
7. **No Custom Cursor Hacks**: Default native OS cursors are strictly preserved.
8. **No Text-on-Image Overlays**: Clean typographic separation with solid background contrast at all times.
