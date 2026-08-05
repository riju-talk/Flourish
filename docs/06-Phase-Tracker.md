# Flourish — Phase Tracker

> Delivery roadmap and progress status — the execution plan for taking Flourish from
> "working foundation" to a portfolio-ready autonomous garden agent.
> **Last updated:** 2026-08-05

---

## Definition of Done (per phase)
- All listed goals shipped and verified.
- Tests passing (`npm test`), lint clean, `tsc --noEmit` clean.
- `docs/` updated to reflect new capabilities.
- No secrets in repo; env docs current.

---

## Phase 0 — Foundation ✅ Done

**Goal:** Working end-to-end full-stack foundation.

- [x] Monorepo scaffold (npm workspaces, concurrently).
- [x] FastAPI backend + Firebase (Auth, Firestore, Storage) wired end-to-end.
- [x] React + Vite frontend with routing, auth, shadcn/ui, dark mode.
- [x] Core CRUD: profiles, plants, tasks, notifications, health checks.
- [x] Auth flow (Google Sign-In → token → profile creation) complete.
- [x] Dashboard, calendar, chat, documents, leaderboard, plant lookup pages.
- [x] Backend + frontend test suites, CI (`ci.yml`).
- [x] Documentation set in `docs/`, hardened `.gitignore` for the service-account key.

---

## Phase 1 — Identity, Privacy & Repair ✅ Done

**Goal:** Land the new identity/privacy model and close existing gaps before building
new AI surface area on top of it.

- [x] `profiles` schema: `bio`, `privacy` (`public_profile_enabled`, `show_email`,
      `show_phone` — all default `false`), `notification_preferences` (per-category
      bools), `agent_profile`.
- [x] Onboarding flow: `/onboarding` page + `POST /api/auth/profile` requires
      `full_name` + `phone_number` on first create; `PATCH /api/auth/profile`,
      `PATCH /api/auth/profile/privacy`, `PATCH /api/auth/profile/notification-preferences`
      for edits.
- [x] Frontend routing: unauthenticated → `/auth`; authenticated w/o profile →
      `/onboarding`; authenticated w/ profile → normal app.
- [x] Leaderboard: `GET /api/leaderboard` is **privacy-safe by default** — only
      `display_name`/avatar/score/level/streak/badges, plus `email`/`phone_number` for
      users who've opted in; added `GET /api/leaderboard/me`. Frontend leaderboard row
      hides contact info unless present in the response.
- [x] Repaired `/api/chat/care-plan` (`AIService.generate_care_plan` implemented).
- [x] Resolved the `/plants/{id}/schedule`, `/schedule/complete`, `/tasks/generate/{id}`
      mismatch — implemented server-side against `care_tasks`.
- [x] Added task `snooze` / `reschedule` endpoints.
- [x] Backend (68 tests) and frontend (46 tests) suites green; `tsc --noEmit` clean.

---

## Phase 2 — Groq Migration & Agentic PlantMind ✅ Done

**Goal:** Retire Ollama; make PlantMind a genuine tool-using agent, built on LangChain.

- [x] Added `GroqService` (`groq_service.py`) on **LangChain** (`langchain-groq` +
      `langgraph`); ported chat, agentic plant lookup, document analysis, and health
      analysis off `OllamaService`.
- [x] Deleted `ollama_service.py` and all `OLLAMA_*` config/env references.
- [x] Added `TavilyService` (`tavily_service.py`, wraps `langchain-tavily`) — web
      search tool.
- [x] Implemented the tool-calling loop via `langgraph.prebuilt.create_react_agent`
      over four tools (`get_user_garden`, `get_task_history`, `get_weather`,
      `web_search`), bounded by `recursion_limit` (per `01-PRD.md` §9 constraints).
- [x] Follow-up suggestions after every PlantMind response.
- [x] Updated `apps/api/requirements.txt` / `pyproject.toml` (added `langchain-groq`,
      `langchain-tavily`, `langgraph`; dropped `ollama`) and `apps/api/.env`.
- [x] `profiles.agent_profile` is now updated after chat interactions
      (`GroqService.update_agent_profile_summary`, deterministic/no extra LLM call) —
      no longer a stub.
- [ ] AI run logging (request type, user, model, tools called, latency, success/failure)
      per `01-PRD.md` §9 Observability — not implemented yet (Backlog).

---

## Phase 2.5 — MCP Server for Agentic QA ✅ Done

**Goal:** Give an MCP client (Claude Code/Desktop) a way to drive agentic QA against a
running Flourish instance.

- [x] `apps/api/mcp_server.py` — real MCP server (official `mcp` SDK, FastMCP, stdio
      transport). Tools: `check_health`, `check_api_contract`, `list_routes`,
      `authenticated_request`, `run_smoke_suite`. No credentials stored server-side —
      auth tools take a Firebase ID token as a call argument.
- [x] Added `mcp` to `requirements.txt` / `pyproject.toml`.
- [ ] Not yet wired into `ci.yml` or documented in a QA runbook — manual `python
      mcp_server.py` for now (Backlog).

---

## Phase 3 — Personalized Plant Recommendations ✅ Done

**Goal:** Ship the recommendation engine end-to-end.

- [x] `recommendations` Firestore collection (see `03-Data-Schema.md`).
- [x] `POST /api/recommendations/generate` + `GET /api/recommendations` — Groq agent
      using `agent_profile` + Tavily + weather to generate personalized, reasoned
      suggestions, images via Unsplash.
- [x] `POST /api/recommendations/{id}/accept` — creates the `plants` doc.
- [x] `POST /api/recommendations/{id}/dismiss` — updates
      `agent_profile.recommendation_preferences.avoided_plants`.
- [x] Frontend `/recommendations` page + `RecommendationCard` component (design in
      `05-UIUX-Rulebook.md` §8.6) with sourced affordance and "Add to my garden" CTA;
      nav link ("For You") added to `Navbar`.

---

## Phase 4 — Automated Notifications & Email ✅ Done

**Goal:** Get proactive alerts into users' inboxes — both event-triggered and
scheduled — with a durable per-user record of what was sent.

- [x] Firebase **Trigger Email** extension declared (`firebase.json`, `.firebaserc`,
      `extensions/firestore-send-email.env`) — installing it against a live SMTP
      provider is a manual `firebase ext:install` step, see README's Deployment section.
- [x] Added `EmailService` (`email_service.py`) — writes to `mail` **and** `email_logs`
      together, every time, gated by `notification_preferences`.
- [x] Added `SchedulerService` (`scheduler_service.py`) — in-process APScheduler
      started on app boot (`main.py` startup/shutdown events), running: an hourly
      streak-risk sweep, a daily 08:00 task-due digest, and a Monday 09:00 weekly
      summary, fanned out per-user.
- [x] `.github/workflows/keep-alive.yml` — scheduled ping (every 10 min, via the
      `RENDER_API_URL` repo variable) against `/health` so the backend process (and
      therefore the scheduler) stays alive between runs.
- [x] Wired `task_due`, `streak_risk`, and `recommendation_ready` notification types
      (achievement/task_completed already existed). `health_score_change` and
      `analysis_complete` remain unwired — no code path produces them yet (Backlog).

---

## Deployment — ✅ Configs in place, not yet executed

**Goal:** Make Flourish deployable end-to-end on Vercel + Render.

- [x] `vercel.json` (repo root) — builds `apps/web`, outputs `apps/web/dist`, SPA
      rewrite to `index.html`.
- [x] `render.yaml` — `rootDir: apps/api`, Python 3.12, health check `/health`, env
      vars listed with `sync: false` for secrets (set manually in the Render dashboard).
- [x] Brief deploy runbook written to `README.md` §Deployment (Render steps, Vercel
      steps, keep-alive variable, Trigger Email extension install command).
- [ ] **Not executed** — no live Render/Vercel deploy has been performed, and
      `firebase ext:install` hasn't been run. Both require the account owner's
      credentials/login, which this agent doesn't have. Follow the README runbook.

---

## Backlog — Intelligence, Community & Scale ⬜ Not started

Deliberately not part of the current push.

- [ ] Wire **Plant.ID** species identification into the plant-add flow.
- [ ] Implement **real image health analysis** (e.g. a Groq vision-capable model),
      replacing the current mock stub.
- [ ] OCR pipeline (tesseract) for printed care guides and image documents.
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
| Phase 0 — Foundation | ✅ Done |
| Phase 1 — Identity, Privacy & Repair | ✅ Done |
| Phase 2 — Groq Migration & Agentic PlantMind | ✅ Done (AI run logging carried to Backlog) |
| Phase 2.5 — MCP Server for Agentic QA | ✅ Done |
| Phase 3 — Personalized Plant Recommendations | ✅ Done |
| Phase 4 — Automated Notifications & Email | ✅ Done |
| Deployment | ✅ Configs in place — not yet executed (needs your login) |
| Backlog — Intelligence, Community & Scale | ⬜ Not started |

---

## Known gaps to watch
- `UNSPLASH_ACCESS_KEY` is blank in `apps/api/.env` — `PlantService` now reads it
  correctly (fixed the old hardcoded-`"demo"` bug), but falls back to Unsplash's
  heavily-rate-limited public `demo` client ID until a real key is added.
- Image analysis, Plant.ID, and OCR are scaffolded but not live (Backlog).
- `AutonomousPlantService` is imported but its `identify_and_create_plant` is never
  called (the `/plants/autonomous` route uses the Groq agent directly).
- `PlantIDService.identify_plant` is not wired to any route.
- `care_tasks` uses `due_date` / `recurring_days` / `notifications.type` — field names
  differ from the legacy SQLAlchemy models (which remain orphaned by design).
- Leaderboard supports all-time only; weekly/monthly periods are Backlog.
- `GROQ_API_KEY` and `TAVILY_API_KEY` are currently blank in `apps/api/.env` — real keys
  are needed before the agent/recommendations produce real (non-fallback) output.
- The agent's tool-call cap is a soft `recursion_limit`, not a hard per-tool counter —
  revisit if latency/cost becomes an issue.
- `health_score_change` and `analysis_complete` notification types are documented but
  nothing triggers them yet — no health-score-change detector or analysis-complete
  event exists in the current code.
- Deployment configs exist but nothing has actually been deployed yet — no live Render
  service, no live Vercel project, no `firebase ext:install` run. `RENDER_API_URL` must
  be set as a repo variable before the keep-alive workflow does anything.
- `SchedulerService`'s jobs only run while a backend process is alive; on Render's free
  tier that depends entirely on the keep-alive ping being configured correctly.

---

> **Related docs:** `01-PRD.md` · `02-Tech-Stack-Architecture.md` · `03-Data-Schema.md` ·
> `04-Rules-of-Engagement.md` · `05-UIUX-Rulebook.md`
