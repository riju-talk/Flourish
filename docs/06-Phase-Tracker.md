# Flourish: Phase Tracker

> Delivery roadmap and progress status. This is the execution plan for taking Flourish
> from "working foundation" to a portfolio-ready autonomous garden agent.
> **Last updated:** 2026-08-05

---

## Definition of Done (per phase)
- All listed goals shipped and verified.
- Tests passing (`npm test`), lint clean, `tsc --noEmit` clean.
- `docs/` updated to reflect new capabilities.
- No secrets in repo; env docs current.

---

## Phase 0: Foundation ✅ Done

**Goal:** Working end-to-end full-stack foundation.

- [x] Monorepo scaffold (npm workspaces, concurrently).
- [x] FastAPI backend + Firebase (Auth, Firestore, Storage) wired end-to-end.
- [x] React + Vite frontend with routing, auth, shadcn/ui, dark mode.
- [x] Core CRUD: profiles, plants, tasks, notifications, health checks.
- [x] Auth flow (Google Sign-In → token → profile creation) complete.
- [x] Dashboard, calendar, chat, leaderboard, plant lookup pages (a documents/AI
      document-analysis page shipped here too, later removed, see below).
- [x] Backend + frontend test suites, CI (`ci.yml`).
- [x] Documentation set in `docs/`, hardened `.gitignore` for the service-account key.

---

## Phase 1: Identity, Privacy & Repair ✅ Done

**Goal:** Land the new identity/privacy model and close existing gaps before building
new AI surface area on top of it.

- [x] `profiles` schema: `bio`, `privacy` (`public_profile_enabled`, `show_email`,
      `show_phone`, all defaulting to `false`), `notification_preferences` (per-category
      bools), `agent_profile`.
- [x] Onboarding flow: `/onboarding` page + `POST /api/auth/profile` requires
      `full_name` + `phone_number` on first create; `PATCH /api/auth/profile`,
      `PATCH /api/auth/profile/privacy`, `PATCH /api/auth/profile/notification-preferences`
      for edits.
- [x] Frontend routing: unauthenticated → `/auth`; authenticated w/o profile →
      `/onboarding`; authenticated w/ profile → normal app.
- [x] Leaderboard: `GET /api/leaderboard` is **privacy-safe by default**, returning only
      `display_name`/avatar/score/level/streak/badges, plus `email`/`phone_number` for
      users who've opted in; added `GET /api/leaderboard/me`. Frontend leaderboard row
      hides contact info unless present in the response.
- [x] Repaired `/api/chat/care-plan` (`AIService.generate_care_plan` implemented).
- [x] Resolved the `/plants/{id}/schedule`, `/schedule/complete`, `/tasks/generate/{id}`
      mismatch, implemented server-side against `care_tasks`.
- [x] Added task `snooze` / `reschedule` endpoints.
- [x] Backend (68 tests) and frontend (46 tests) suites green; `tsc --noEmit` clean.

---

## Phase 2: Groq Migration & Agentic PlantMind ✅ Done

**Goal:** Retire Ollama; make PlantMind a genuine tool-using agent, built on LangChain.

- [x] Added `GroqService` (`groq_service.py`) on **plain LangChain** (`langchain`,
      `langchain-groq`, no LangGraph); ported chat, agentic plant lookup, and health
      analysis off `OllamaService`.
- [x] Deleted `ollama_service.py` and all `OLLAMA_*` config/env references.
- [x] Added `TavilyService` (`tavily_service.py`, wraps `langchain-tavily`) as the web
      search tool.
- [x] Implemented the tool-calling loop via `langchain.agents.AgentExecutor` +
      `create_tool_calling_agent` over four tools (`get_user_garden`,
      `get_task_history`, `get_weather`, `web_search`), bounded by `max_iterations`
      (per `01-PRD.md` §9 constraints). This was originally built on
      `langgraph.prebuilt.create_react_agent`, then rebuilt on plain LangChain per
      explicit instruction. See the Hardening pass below.
- [x] Follow-up suggestions after every PlantMind response.
- [x] Updated `apps/api/requirements.txt` / `pyproject.toml` (added `langchain`,
      `langchain-groq`, `langchain-tavily`; dropped `ollama`) and `apps/api/.env`.
- [x] `profiles.agent_profile` is now updated after chat interactions
      (`GroqService.update_agent_profile_summary`, deterministic, no extra LLM call).
      No longer a stub.
- [ ] AI run logging (request type, user, model, tools called, latency, success/failure)
      per `01-PRD.md` §9 Observability. Not implemented yet (Backlog).

---

## Phase 2.5: MCP Server for Agentic QA ✅ Done

**Goal:** Give an MCP client (Claude Code/Desktop) a way to drive agentic QA against a
running Flourish instance.

- [x] `apps/api/mcp_server.py`, a real MCP server (official `mcp` SDK, FastMCP, stdio
      transport). Tools: `check_health`, `check_api_contract`, `list_routes`,
      `authenticated_request`, `run_smoke_suite`. No credentials are stored server-side;
      auth tools take a Firebase ID token as a call argument.
- [x] Added `mcp` to `requirements.txt` / `pyproject.toml`.
- [ ] Not yet wired into `ci.yml` or documented in a QA runbook. Run it manually with
      `python mcp_server.py` for now (Backlog).

---

## Phase 3: Personalized Plant Recommendations ✅ Done

**Goal:** Ship the recommendation engine end-to-end.

- [x] `recommendations` Firestore collection (see `03-Data-Schema.md`).
- [x] `POST /api/recommendations/generate` + `GET /api/recommendations`: a Groq agent
      using `agent_profile` + Tavily + weather to generate personalized, reasoned
      suggestions, with images via Unsplash.
- [x] `POST /api/recommendations/{id}/accept`, which creates the `plants` doc.
- [x] `POST /api/recommendations/{id}/dismiss`, which updates
      `agent_profile.recommendation_preferences.avoided_plants`.
- [x] Frontend `/recommendations` page + `RecommendationCard` component (design in
      `05-UIUX-Rulebook.md` §8.6) with sourced affordance and "Add to my garden" CTA;
      nav link ("For You") added to `Navbar`.

---

## Phase 4: Automated Notifications & Email ✅ Done

**Goal:** Get proactive alerts into users' inboxes, both event-triggered and
scheduled, with a durable per-user record of what was sent.

- [x] Firebase **Trigger Email** extension declared (`firebase.json`, `.firebaserc`,
      `extensions/firestore-send-email.env`). Installing it against a live SMTP
      provider is a manual `firebase ext:install` step; see README's Deployment section.
- [x] Added `EmailService` (`email_service.py`), which writes to `mail` **and**
      `email_logs` together, every time, gated by `notification_preferences`.
- [x] Added `SchedulerService` (`scheduler_service.py`), an in-process APScheduler
      started on app boot (`main.py` startup/shutdown events). It runs an hourly
      streak-risk sweep, a daily 08:00 task-due digest, and a Monday 09:00 weekly
      summary, fanned out per-user.
- [x] `.github/workflows/keep-alive.yml`: a scheduled ping (every 10 min, via the
      `RENDER_API_URL` repo variable) against `/health` so the backend process, and
      therefore the scheduler, stays alive between runs.
- [x] Wired `task_due`, `streak_risk`, and `recommendation_ready` notification types
      (achievement/task_completed already existed). `health_score_change` and
      `analysis_complete` remain unwired; no code path produces them yet (Backlog).

---

## Deployment: ✅ Configs in place, not yet executed

**Goal:** Make Flourish deployable end-to-end on Vercel + Render.

- [x] `vercel.json` (repo root): builds `apps/web`, outputs `apps/web/dist`, SPA
      rewrite to `index.html`.
- [x] `render.yaml`: `rootDir: apps/api`, Python 3.12, health check `/health`, env
      vars listed with `sync: false` for secrets (set manually in the Render dashboard).
- [x] Brief deploy runbook written to `README.md` §Deployment (Render steps, Vercel
      steps, keep-alive variable, Trigger Email extension install command).
- [ ] **Not executed.** No live Render/Vercel deploy has been performed, and
      `firebase ext:install` hasn't been run. Both require the account owner's
      credentials/login, which this agent doesn't have. Follow the README runbook.
- [x] `apps/api/Dockerfile` fixed and verified (builds, boots, `/health` responds), as
      an alternative to Render's native Python runtime. Bumped 3.11 to 3.12, fixed a
      broken `curl`-based healthcheck (not present in the slim image), and added
      `.dockerignore` (the old Dockerfile would have baked `.venv` and `.env`, secrets
      included, straight into the image). `npm run docker:build:api` /
      `docker:run:api` at the repo root.

---

## Hardening pass: ✅ Done

**Goal:** Fix real bugs surfaced by actually running the app, not just reading it.

- [x] **Removed the Document Analyzer feature entirely**: `/api/documents` route,
      `DocumentAnalyzer.tsx`, `Documents.tsx` page, `GroqService.analyze_document`,
      the file-upload affordance in Chat, and the PyPDF2/Pillow/pytesseract
      dependencies it needed. This was a deliberate removal, not a stub. See the note
      in Known gaps below.
- [x] **Fixed `npm run dev` at the monorepo level.** Root `package.json`'s `*:api`
      scripts called bare `python`, which resolved to an unrelated system Python with
      none of the project's dependencies, so `npm run dev` never actually worked. It
      now points at `apps/api/.venv/Scripts/python.exe` directly (also fixed the venv
      itself, which was missing `pip`). Verified: `npm run dev:api` boots and
      `/health` responds.
- [x] **Fixed a real authentication bug, not just a style one.** `core/auth.py`
      initialized Firebase Admin **eagerly at module import time**, meaning the
      *entire app*, including `/health` (used by the keep-alive ping and Render's own
      health check), crashed on startup whenever `FIREBASE_SERVICE_ACCOUNT_KEY` was
      missing or invalid. Confirmed by reproducing the crash in the newly-fixed Docker
      container. Rewrote it to initialize lazily on first authenticated request,
      mirroring `FirestoreDB.get_db()`'s existing lazy pattern. `/health` now works
      regardless of Firebase config, and a misconfigured key now fails one request
      with a clear 500 instead of taking the whole process down.
- [x] **Fixed frontend token staleness.** `integrations/api.ts`'s axios interceptor
      read a Firebase ID token from `localStorage` that was set once at sign-in and
      never refreshed. Since ID tokens expire after ~1 hour, every API call would
      start failing with 401s partway through a session even though the user was
      still signed in. It now calls `auth.currentUser.getIdToken()` per request (cheap,
      since Firebase caches and only refreshes over the network when actually near
      expiry), falling back to `localStorage` only for the brief window before
      Firebase's auth state has hydrated.
- [x] **Unsplash now uses all three of its credentials correctly.** Added
      `UNSPLASH_APPLICATION_ID` and `UNSPLASH_SECRET_KEY` to settings/`.env` alongside
      the existing `UNSPLASH_ACCESS_KEY` (the only one Unsplash's search endpoint
      actually needs as `client_id`). Also implemented the download-tracking ping
      Unsplash's API Guidelines require when a fetched photo is actually used, not
      just searched.
- [x] **Firebase Admin credentials moved from a JSON key file to individual env
      vars.** `core/auth.py` now builds a credentials dict from `FIREBASE_PROJECT_ID` /
      `_PRIVATE_KEY_ID` / `_PRIVATE_KEY` / `_CLIENT_EMAIL` / `_CLIENT_ID` /
      `_CLIENT_X509_CERT_URL` (plus fixed-default OAuth endpoint fields) instead of
      reading a file path, so there is no service-account JSON anywhere in the repo or
      the deployed container anymore. `setup_database.py` reuses the same
      `ensure_firebase_initialized()` helper instead of duplicating the old file-path
      logic. Verified: `credentials.Certificate(dict)` parses the PEM and
      `firebase_admin.initialize_app()` succeeds with zero files on disk.
- [x] **LLM backbone switched to `qwen/qwen3.6-27b`** (still served via Groq, via
      `GROQ_MODEL` in `core/config.py` and `.env`; no code changes needed since
      `GroqService` already read the model from settings rather than hardcoding it).

---

## Design & agent-framework polish: ✅ Done

**Goal:** Motion, branding, and agent-framework refinements requested after seeing the
app running.

- [x] **Slower, softer motion throughout.** Base transitions and hover effects moved
      from ~300ms to 500-1000ms with `ease-out`; Tailwind's built-in `animate-bounce`
      (branded loaders, chat typing indicator) is now globally overridden to a 2.4s
      smooth cubic-bezier instead of the default snappy 1s bounce.
- [x] **Animations removed entirely from the Auth screen and the splash/loading
      screens** (`SplashScreen.tsx`, extracted from three duplicated blocks in
      `App.tsx`). Both are now fully static except the functional sign-in spinner.
- [x] **Dashboard:** added a "New Plants Recommended For You" card below Botanist
      Wisdom, linking to `/recommendations`.
- [x] **Footer** (`Footer.tsx`) added to Dashboard, Calendar, Leaderboard, Plant
      Lookup, and Recommendations, deliberately skipping Chat, whose fixed-height
      pinned-input layout a footer would break.
- [x] **Leaderboard rebuilt with a podium-style top 3** (center-elevated rank 1) above
      the rankings list.
- [x] **Real brand logo wired in** (`public/logo.png` opaque/white-background,
      `public/logo_transparent.png` transparent) replacing the generic lucide `Leaf`
      icon in Navbar, Auth, Footer, Onboarding, and the splash screen. The opaque
      variant is used on light surfaces (Navbar, Auth's sign-in panel); the transparent
      variant goes on colored/dark surfaces (Auth's brand panel, Footer, splash screen,
      Onboarding's icon badge) so no white box artifact shows.
- [x] **LangGraph removed, plain LangChain only.** `GroqService`'s agent was
      rebuilt on `langchain.agents.AgentExecutor` + `create_tool_calling_agent`
      instead of `langgraph.prebuilt.create_react_agent`, per explicit instruction.
      Dropped `langgraph` from `requirements.txt`/`pyproject.toml`, added `langchain`
      directly (previously only a transitive dependency).

---

## Backlog: Intelligence, Community & Scale ⬜ Not started

Deliberately not part of the current push.

- [ ] Wire **Plant.ID** species identification into the plant-add flow.
- [ ] Implement **real image health analysis** (e.g. a Groq vision-capable model),
      replacing the current mock stub.
- [ ] Weather-aware scheduling: shift watering days based on local conditions.
- [ ] Weekly/monthly leaderboard periods.
- [ ] Achievements & badges catalog + reward notifications (list drafted in
      `01-PRD.md` §5.9).
- [ ] Opt-in public garden profile page (`privacy.public_profile_enabled`).
- [ ] Firestore composite indexes + caching layer.
- [ ] Monitoring: Firebase Performance, Sentry error tracking, analytics.
- [ ] Mobile-first refinements & PWA support.
- [ ] Rate limiting on AI endpoints (per `01-PRD.md` §10 Security).

---

## Status Legend

| Symbol | Meaning |
|---|---|
| ✅ | Complete |
| 🟡 | In progress / planned (next up) |
| ⬜ | Not started / backlog |

### Quick status snapshot (2026-08-05)
| Phase | Status |
|---|---|
| Phase 0: Foundation | ✅ Done |
| Phase 1: Identity, Privacy & Repair | ✅ Done |
| Phase 2: Groq Migration & Agentic PlantMind | ✅ Done (AI run logging carried to Backlog) |
| Phase 2.5: MCP Server for Agentic QA | ✅ Done |
| Phase 3: Personalized Plant Recommendations | ✅ Done |
| Phase 4: Automated Notifications & Email | ✅ Done |
| Deployment | ✅ Configs in place, not yet executed (needs your login) |
| Hardening pass (dev script, auth, Docker, Unsplash) | ✅ Done |
| Design & agent-framework polish (motion, branding, LangChain-only) | ✅ Done |
| Backlog: Intelligence, Community & Scale | ⬜ Not started |

---

## Known gaps to watch
- **Rotate the Firebase service-account key.** It was pasted directly into a chat
  session to populate `apps/api/.env`'s `FIREBASE_*` fields, meaning it's recorded in
  that conversation's transcript. Generate a new key in Firebase Console → Project
  Settings → Service Accounts, update `.env` (and Render's env vars once deployed),
  then revoke the old one (`private_key_id` starting `e8bf27ed5b...` at time of
  writing). Not yet done as of this entry.
- Image analysis and Plant.ID are scaffolded but not live (Backlog).
- The Document Analyzer feature (upload PDF/TXT → AI care info) was removed entirely
  (route, frontend page/component, `GroqService.analyze_document`, and the
  PyPDF2/Pillow/pytesseract dependencies it needed). Not a stub to revisit, a
  deliberate removal.
- `AutonomousPlantService` is imported but its `identify_and_create_plant` is never
  called (the `/plants/autonomous` route uses the Groq agent directly).
- `PlantIDService.identify_plant` is not wired to any route.
- `care_tasks` uses `due_date` / `recurring_days` / `notifications.type`, field names
  that differ from the legacy SQLAlchemy models (which remain orphaned by design).
- Leaderboard supports all-time only; weekly/monthly periods are Backlog.
- `GROQ_API_KEY` and `TAVILY_API_KEY` are currently blank in `apps/api/.env`. Real keys
  are needed before the agent/recommendations produce real (non-fallback) output.
- The agent's tool-call cap is a soft `recursion_limit`, not a hard per-tool counter.
  Revisit if latency/cost becomes an issue.
- `health_score_change` and `analysis_complete` notification types are documented but
  nothing triggers them yet. No health-score-change detector or analysis-complete
  event exists in the current code.
- Deployment configs exist but nothing has actually been deployed yet: no live Render
  service, no live Vercel project, no `firebase ext:install` run. `RENDER_API_URL` must
  be set as a repo variable before the keep-alive workflow does anything.
- `SchedulerService`'s jobs only run while a backend process is alive; on Render's free
  tier that depends entirely on the keep-alive ping being configured correctly.

---

> **Related docs:** `01-PRD.md` · `02-Tech-Stack-Architecture.md` · `03-Data-Schema.md` ·
> `04-Rules-of-Engagement.md` · `05-UIUX-Rulebook.md`
