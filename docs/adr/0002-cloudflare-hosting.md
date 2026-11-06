# ADR 0002 — Hosting on Cloudflare Pages and Cloudflare Tunnel

- Status: accepted (owner, 2026-11-03)
- Date: 2026-11-03
- Issue: #2

## Context

`Savage-Fred/learn` produces both a self-contained static curriculum distribution (`dist/`) and an active local FastAPI backend (`127.0.0.1:8795`) powering live LLM CLI harnesses (`claude`, `codex`, `agy`).

To publish `learn.willmccarty.io` as part of the `willmccarty.io` public infrastructure, the platform must satisfy:

1. **Custom Response Headers**: Enforce strict Content-Security-Policy (CSP), `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and HSTS HTTP headers at the edge via `public/_headers`.
2. **Zero-Fluff Static Serving**: Serve compiled curricula catalogs (`static/catalog.json`), high-performance client styling, and vanilla SPA JavaScript without server cost, maintenance, or cold starts.
3. **Continuous Deployment from `main`**: Automatically rebuild and publish on push to `main` via Cloudflare Pages Git integration, providing PR preview builds on `*.pages.dev`.
4. **Dual Mode (Static Catalog & Live Local Harness)**: Enable public review of curricula, rubrics, and exercises on `learn.willmccarty.io` while allowing seamless local or authenticated remote tunnel connectivity (`cloudflared` + Cloudflare Access) for live interactive quiz and mock interview sessions.
5. **No Third-Party Analytics or Injected Scripts**: Zero external trackers, web beacons, or unvetted scripts.

## Decision

**Host static distribution on Cloudflare Pages connected to `Savage-Fred/learn` GitHub repository via Git integration, with custom domain `learn.willmccarty.io`.**

- Cloudflare Pages builds `python3 scripts/build_pages.py` on push: `main` deploys to production, branches and PRs receive preview URLs.
- `public/_headers` carries edge HTTP response headers.
- DNS for `learn.willmccarty.io` is managed on Cloudflare DNS as a CNAME pointing to `<project>.pages.dev`.
- For live local CLI harness sessions, an optional `cloudflared` tunnel profile routes `learn.willmccarty.io` to `http://127.0.0.1:8795` behind Cloudflare Access Service Token authentication.

## Why Git Integration rather than Direct Upload

- **No Long-Lived Deploy Tokens**: No Cloudflare API tokens stored in GitHub Actions secrets; the Cloudflare GitHub App connects directly with read-only repository permissions.
- **Preview Environments**: Automated staging deployments on every branch push without extra CI workflow logic.
- **Simplicity**: Build script `scripts/build_pages.py` uses standard library Python, generating `dist/` with all static assets and compiled catalog metadata.

## Consequences

- Build configuration is specified in `wrangler.toml` (`pages_build_output_dir = "dist"`) and `package.json` (`npm run build` -> `python3 scripts/build_pages.py`).
- DNS record: CNAME `learn` -> `learn-xyz.pages.dev` with Cloudflare Proxy enabled.
- Cloudflare Web Analytics must remain **disabled** to avoid script injection and CSP violations.
- Runbook and cutover steps are documented in `docs/DEPLOY.md`.
