# Deployment

The API (`apps/api`) runs on **Render** (persistent process, in-process scheduler) or
**Vercel** (serverless, scheduled jobs driven by GitHub Actions). The web app
(`apps/web`) deploys to Vercel from the repo root `vercel.json`.

## Setting / rotating the Groq API key

The AI features (PlantMind chat, plant lookup, recommendations) need exactly one secret:
`GROQ_API_KEY`. It is read from the server environment only - it is never sent to or
stored in the frontend, so rotating it needs no web redeploy.

1. Create a key at <https://console.groq.com/keys>.
2. Set it on the host:
   - **Render:** Dashboard > `flourish-api` > Environment > `GROQ_API_KEY` (declared in
     `render.yaml` with `sync: false`, so it is never committed). Save, then redeploy.
   - **Vercel:** Project (API) > Settings > Environment Variables > `GROQ_API_KEY`
     (Production), then redeploy - Vercel only applies env changes to new deployments.
   - **Local:** `apps/api/.env` (git-ignored; copy from `.env.example`).
3. Optional: `GROQ_MODEL` (default `qwen/qwen3.8-27b`). If Groq retires a model the AI
   falls back to its "trouble reaching PlantMind" reply; check
   `GET https://api.groq.com/openai/v1/models` (with your key) for current IDs.
4. Verify:
   ```
   curl https://<your-api-host>/health
   # {"status":"ok","service":"Flourish API","ai":{"configured":true,"model":"qwen/qwen3.8-27b"}}
   ```
   `"configured": false` means the host did not pick the key up (wrong variable name,
   wrong environment, or no redeploy yet). The startup log also prints a `WARNING` in
   that case. Leading/trailing spaces, newlines and wrapping quotes in the pasted value
   are stripped automatically.

If the key is missing or Groq is unreachable the API still starts and every AI endpoint
returns a graceful fallback message instead of a 500.

## Rate limiting (AI endpoints)

Per-user limits protect your Groq quota from a single heavy user or a client bug. Over the
limit the API returns **HTTP 429** with a `Retry-After` header and a friendly message; the
web app shows it as a toast. Rejected requests are not counted, so waiting out the
`Retry-After` is always enough.

| Feature | Endpoint(s) | Per minute | Per hour |
| --- | --- | --- | --- |
| PlantMind chat | `POST /api/chat/`, `POST /api/chat/sessions/{id}/messages` | 10 | 120 |
| Explore lookup | `POST /api/plants/lookup`, `GET /api/context/plant-info/{name}` | 8 | 60 |
| Recommendations | `POST /api/recommendations/generate` | 3 | 15 |
| AI add-plant | `POST /api/plants/autonomous` | 6 | 40 |
| Image analysis / care plan | `POST /api/chat/analyze-image`, `POST /api/chat/care-plan` | 5 | 30 |

Tune them in `apps/api/api/core/rate_limit.py` (`LIMITS`). Set `RATE_LIMIT_ENABLED=false` to
disable (local load tests only). Counters live in process memory: exact on a single
long-lived server (Render), best-effort on Vercel serverless where each warm instance
counts separately. If you need hard global limits on Vercel, move the counters to Firestore
or Redis.

## Other required environment variables

See `apps/api/.env.example` for the full list. Required for a working deployment:

| Variable | Purpose |
| --- | --- |
| `ALLOWED_ORIGINS` | Comma-separated frontend origins (CORS) |
| `FIREBASE_*` | Firebase Admin service-account fields (auth + Firestore) |
| `SECRET_KEY` | Random value; never keep the example default |
| `PERENUAL_API_KEY`, `TAVILY_API_KEY` | Plant-care facts and live web search |
| `UNSPLASH_ACCESS_KEY`, `OPENWEATHER_API_KEY` | Photos and weather (optional features) |

## Scheduled jobs

- **Render:** the in-process APScheduler runs the jobs; nothing else to configure.
- **Vercel:** set `CRON_SECRET` on the API project, then in the GitHub repo set the
  variable `VERCEL_API_URL` and the secret `CRON_SECRET` (same value). The
  `vercel-cron.yml` workflow calls `/api/cron/*` hourly/daily/weekly.

## Pre-deploy checklist

```
# backend
cd apps/api && uv run python -m pytest -q
# frontend
cd apps/web && npm run typecheck && npm run lint && npm test && npm run build
```
