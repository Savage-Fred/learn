# Deploying learn.willmccarty.io to Cloudflare Pages

Decision: `docs/adr/0002-cloudflare-hosting.md`. This is the operational runbook. Steps marked **owner** need the Cloudflare dashboard or DNS registrar and cannot be completed from an agent session.

## 1. Create the Pages Project (owner, once)

Cloudflare dashboard → Workers & Pages → Create → Pages → **Connect to Git**.

| Setting | Value |
|---|---|
| Repository | `Savage-Fred/learn` |
| Production branch | `main` |
| Framework preset | None / Custom |
| Build command | `python3 scripts/build_pages.py` |
| Build output directory | `dist` |
| Root directory | `/` |
| Environment variable | `NODE_VERSION` = `22.23.4` (from `.nvmrc`) |

Leave **Web Analytics OFF**. Cloudflare Web Analytics injects a beacon script that violates the strict Content-Security-Policy in `public/_headers`.

The initial build publishes to `https://<project>.pages.dev`. Non-production branches automatically receive preview deployments.

## 2. Verify the pages.dev Deploy

```sh
# 1. Verify HTTP security headers from public/_headers
curl -sI https://<project>.pages.dev/ | grep -iE 'content-security-policy|x-frame-options|referrer-policy|strict-transport|permissions-policy'

# 2. Verify static catalog endpoint compiles all 11 topics
curl -s https://<project>.pages.dev/static/catalog.json | grep -o '"slug"' | wc -l   # expect >= 11

# 3. Confirm zero unvetted external scripts
curl -s https://<project>.pages.dev/ | grep -c '<script src="http'   # expect 0
```

All security headers specified in `public/_headers` must be present.

## 3. Configure Custom Domain learn.willmccarty.io (owner)

Since `willmccarty.io` DNS is already hosted on Cloudflare (see `willmccarty.io/docs/DEPLOY.md`):

1. Cloudflare dashboard → Workers & Pages → Select `learn` project → **Custom domains** tab.
2. Click **Set up a custom domain**.
3. Enter `learn.willmccarty.io`.
4. Cloudflare automatically configures the CNAME record in the `willmccarty.io` zone pointing `learn` to `<project>.pages.dev` with DNS proxying enabled, and provisions the SSL/TLS certificate.
5. In Cloudflare dashboard → SSL/TLS → confirm encryption mode is **Full (strict)**.

## 4. Verify the Production Cutover

```sh
# 1. Apex/subdomain returns HTTP/2 200
curl -sI https://learn.willmccarty.io/ | head -1

# 2. Plain HTTP redirects to HTTPS 301
curl -sI http://learn.willmccarty.io/ | head -1

# 3. Security headers match exactly
curl -sI https://learn.willmccarty.io/ | grep -i 'content-security-policy'
```

## 5. Live Local Harness Mode (Optional Cloudflare Tunnel)

To connect the local FastAPI interactive harness (`uvicorn app.main:app --port 8795`) for live quiz runs and CLI mock interviews:

1. **Systemd Daemon**: Install and start the systemd unit:
   ```sh
   sudo cp ops/systemd/learn-web.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now learn-web.service
   ```
2. **Tunnel Routing**: Copy `ops/cloudflared/config.yml.example` to `/etc/cloudflared/config.yml` with your tunnel credentials and start `cloudflared`.
3. **Cloudflare Access**: Ensure Zero Trust Access policy is attached to `learn.willmccarty.io` to require identity or Service Token authentication for backend routes.

## Ongoing Operations

- **Merge to `main`**: Automatically deploys the new static site and catalog.
- **Rollback**: Cloudflare dashboard → Deployments → Select previous deployment → **Rollback**.
- **Header Updates**: Modify `public/_headers`, commit, and push.
