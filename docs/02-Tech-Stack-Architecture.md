# Flourish: Tech Stack & Architecture

> System design reference for the Flourish full-stack monorepo.
> **Last updated:** 2026-08-05

---

## 1. Technology Stack

### Monorepo
- **Workspaces:** `npm` workspaces (`apps/*`), concurrently for parallel dev.
- **Tooling:** root `package.json` scripts (`dev`, `build`, `test`, `lint`, `install:all`, `clean`).

### Frontend: `apps/web`
| Concern | Choice |
|---|---|
| Framework | React 18.3 + TypeScript |
| Build | Vite 5.4 (SWC plugin), port 5173 dev |
| Routing | React Router 6 |
| State | TanStack React Query 5 |
| HTTP | Axios (auth interceptor, 401 → redirect to `/auth`) |
| Styling | Tailwind CSS 3.4 + shadcn/ui (Radix UI primitives) |
| Charts | Recharts |
| Calendar | react-day-picker (via CareCalendar) |
| Markdown | react-markdown |
| Forms | react-hook-form + zod |
| Firebase | firebase SDK 12.8 (auth, storage) |
| Theming | next-themes (class-based dark mode) |
| Tests | Vitest + React Testing Library + jsdom |

> Note: `05-UIUX-Rulebook.md`'s Appendix B file-structure convention is written in
> generic Next.js App Router terms (`app/`, `page.tsx`). This repo uses **Vite + React
> Router**, not Next.js. Treat that appendix as naming/organization inspiration
> (route groups, component folders), not a literal directory to recreate. Actual
> frontend routes live in `apps/web/src/pages/`, see §3.

### Backend: `apps/api`
| Concern | Choice |
|---|---|
| Framework | FastAPI 0.115 + Pydantic 2.10 |
| Server | Uvicorn 0.32 on port 8000 |
| Auth | Firebase Admin (verify ID tokens) |
| DB | Cloud Firestore (via `firebase-admin`) |
| Storage | Firebase Cloud Storage |
| LLM | **Groq** via **LangChain** (`langchain-groq` + `langchain.agents` tool-calling agent; plain LangChain, no LangGraph). This is the sole LLM backend (chat, agentic lookup, recommendations). Ollama has been retired; there is no local-model fallback. |
| Agent tools | **Tavily** (web search, via `langchain-tavily`), **OpenWeatherMap** (weather), internal Firestore reads, all wired as LangChain `@tool`s bound per-request to the calling user |
| QA | Real **MCP server** (`mcp_server.py`, official `mcp` SDK + FastMCP) exposing agentic QA tools against a running instance. Separate from the `/api/mcp` REST routes below, which just reuse the "MCP" label |
| Images | **Unsplash**, fetches a representative photo for a plant by name/species; used for `plants.image_url` on add/lookup and for `recommendations.image_url` |
| Email | Firebase **Trigger Email** extension (Firestore-triggered via a `mail` collection), plus an in-process scheduler for automated sends (see §5) |
| External | OpenWeatherMap, Unsplash, Plant.ID, Tavily (optional/required keys, see §6) |
| Tests | pytest + pytest-cov |

### Firebase: Project `flourish-de908`
- Authentication (Google Sign-In)
- Cloud Firestore (NoSQL, real-time)
- Cloud Storage bucket: `flourish-de908.firebasestorage.app`
- **Trigger Email extension**, sends mail for docs written to the `mail` collection
- Console: https://console.firebase.google.com/project/flourish-de908

### External / Optional
- **Groq** (LLM, required) · **Tavily** (web search tool, required for grounded
  recommendations) · **Unsplash** (plant photos) · OpenWeatherMap (weather) · Plant.ID
  (species ID)

### Deployment (live)
**Vercel** (frontend) and **Render** (backend) configs are in the repo:
`vercel.json` (root), `render.yaml` (root, `rootDir: apps/api`), and
`.github/workflows/keep-alive.yml` (pings `/health` every 10 min so Render's free tier
doesn't spin down between requests, which is also what makes `SchedulerService`'s
periodic jobs reliable). Email delivery via the Firebase **Trigger Email** extension is
configured through `firebase.json` / `.firebaserc` / `extensions/firestore-send-email.env`.
None of this has been *executed* (no live deploy, no `firebase ext:install` run); that
requires the account owner's credentials. See the README's Deployment section for the
exact steps.

---

## 2. High-Level Architecture

```
┌─────────────────────────────┐
│         Browser             │
│  React (Vite) :5173         │
│  Auth · Router · Axios      │
└──────────────┬──────────────┘
               │ HTTPS · Bearer (Firebase ID token)
               ▼
┌─────────────────────────────┐
│     FastAPI Backend :8000   │
│  routes/ (auth, plants,     │
│  tasks, dashboard, chat,    │
│  images, mcp,               │
│  notifications, leaderboard,│
│  recommendations, storage)  │
│  services/ (Groq agent,     │
│  Tavily, Weather, Unsplash, │
│  Email, Scheduler, ...)     │
│  core/ (auth, config)       │
│  db/ (firestore, storage)   │
└──────┬──────────────┬───────┘
       │              │
       ▼              ▼
┌──────────────┐  ┌──────────────┐
│   Firestore  │  │ Cloud Storage│
│   (NoSQL)    │  │ (images/docs)│
└──────┬───────┘  └──────────────┘
       │
       ├──────────────┐
       ▼              ▼
┌──────────────┐  ┌────────────────────┐
│ Firebase Auth│  │ Trigger Email ext.  │
│ (Google OAuth)│  │ (mail → SMTP send)  │
└──────────────┘  └────────────────────┘

Agent tool calls (reason → act → observe → answer):
  Groq  ──▶  get_weather (OpenWeatherMap)
        ──▶  web_search (Tavily)
        ──▶  internal Firestore reads (garden, tasks, agent_profile)

In-process scheduler (APScheduler) fires periodic jobs while the app is running:
digest emails, streak-risk sweeps, and task-due reminders, each writing to `mail`
and `email_logs` alongside the usual in-app `notifications`.
```

### Key flows
1. **Auth & onboarding:** Google popup → Firebase ID token → stored in `localStorage` →
   GET `/api/auth/profile`. If no profile exists yet, the frontend routes to
   `/onboarding`, collects full name + phone number, then POSTs `/api/auth/profile` to
   create it (`privacy` and `notification_preferences` are initialized to their private
   defaults at creation; see `03-Data-Schema.md`). Existing users skip straight to
   protected routes.
2. **API call:** Axios injects `Authorization: Bearer <token>`; FastAPI verifies the
   token via `verify_firebase_token` and extracts `uid`; ownership-scoped queries.
3. **Files:** Frontend uploads multipart → `/api/storage/...` → Firebase Storage under
   `users/{uid}/...` → public URL returned.
4. **Real-time:** WebSocket `/api/notifications/ws/{user_id}` for live in-app alerts.
5. **Agentic response (chat / recommendations):** GroqService reasons about the request,
   optionally calls one or more tools (`get_weather`, `web_search` via Tavily, or a
   Firestore read of the user's own garden/tasks/`agent_profile`), then answers and
   appends follow-up suggestion chips. `agent_profile` is updated afterward, not on
   every read.
6. **Event-triggered email:** an action (achievement unlocked, streak at risk) writes an
   in-app `notifications` doc; if the matching `notification_preferences` flag is on,
   the backend also writes a `mail` doc (consumed by the Trigger Email extension) and an
   `email_logs` doc recording the send (`trigger: "event"`).
7. **Scheduled email:** because the backend is kept warm continuously (see keep-alive
   below), an in-process APScheduler job runs on a fixed interval, evaluates all users
   (streak-risk sweep, task-due-today digest, weekly summary), and for each user whose
   preferences allow it, writes `mail` + `email_logs` (`trigger: "scheduled"`) the same
   way an event-triggered email would.
8. **Keep-alive:** a scheduled GitHub Actions workflow pings the backend's `/health`
   (or `/api/health`) endpoint on an interval short enough to prevent a free-tier host
   from spinning down, which is what makes flow 7 reliable ("the app is always active").
   This is a lightweight CI workflow file, unrelated to the deferred `vercel.json` /
   `render.yaml` deployment configs in §1.

---

## 3. Directory Structure

```
Flourish/
├── apps/
│   ├── api/                        # FastAPI backend
│   │   ├── main.py                 # App entry, CORS, router mounting
│   │   ├── mcp_server.py           # Real MCP server for agentic QA (FastMCP, stdio)
│   │   ├── requirements.txt
│   │   ├── api/
│   │   │   ├── core/               # auth.py, config.py
│   │   │   ├── db/                 # firestore.py, storage.py, session.py (empty)
│   │   │   ├── models/             # plant.py, task.py, chat.py, db_models.py (legacy)
│   │   │   ├── routes/             # plants, tasks, dashboard, chat,
│   │   │   │                       # images, mcp, notifications, leaderboard,
│   │   │   │                       # recommendations, storage, auth
│   │   │   └── services/           # groq_service, plant_service (Unsplash),
│   │   │                           # tavily_service, weather_service, plant_id_service,
│   │   │                           # email_service, scheduler_service,
│   │   │                           # multi_modal_chat (empty), autonomous_plant_service
│   │   └── tests/                  # pytest suite
│   └── web/                        # React frontend
│       └── src/
│           ├── pages/              # Index, Auth, Onboarding, Chat, Calendar,
│           │                       # Leaderboard, PlantLookup, Recommendations,
│           │                       # Settings, NotFound
│           ├── components/         # PlantCard, DailyChecklist, LeaderboardPreview,
│           │                       # AddPlantDialog/Form, Navbar, CareCalendar,
│           │                       # ScheduleCalendar, Chat, AIAssistant,
│           │                       # PlantLookup, RecommendationCard, NotificationCenter,
│           │                       # PrivacySettings, ErrorBoundary, ui/ (shadcn primitives)
│           ├── hooks/              # useAuth.tsx, use-mobile, use-toast
│           ├── integrations/api.ts # Axios client + typed API functions
│           ├── lib/                # firebase.ts, firebaseStorage.ts, utils.ts, logger.ts
│           └── test/               # test setup
├── docs/                           # 📚 Documentation set
├── .github/workflows/              # ci.yml (test/lint/build) + keep-alive.yml (health ping)
├── extensions/
│   └── firestore-send-email.env    # Trigger Email extension params (no secrets)
├── firebase.json                   # Declares the Trigger Email extension
├── .firebaserc                     # Points the Firebase CLI at flourish-de908
├── README.md                       # Includes the deploy runbook
├── package.json                    # Monorepo scripts
├── eslint.config.js
├── render.yaml                     # Render deployment config (backend, rootDir apps/api)
├── vercel.json                     # Vercel deployment config (frontend)
```

> `start.bat`, `start.ps1`, `.replit`, root `ARCHITECTURE.md`, and `apps/api/README.md`
> have been removed. Use the `npm run dev` / `npm run build` / `npm run test` scripts
> in root `package.json` and this documentation set instead.

---

## 4. API Endpoint Inventory

All routers are guarded by `Depends(verify_firebase_token)`. Note: the `auth` router
is mounted **without a router-level dependency** in `main.py`, but its `/profile`
handlers still resolve `user_id` via the token dependency individually, so **every
request to `/api/auth/profile` requires a valid Firebase token**.

> Naming note: `01-PRD.md` §8 lists endpoints in a generic `/api/profile`,
> `/api/recommendations` style. This repo keeps FastAPI routers split by resource
> prefix (`/api/auth`, `/api/plants`, ...) as already established. The table below is
> the literal, accurate contract; the PRD's list is the product-level intent it maps to.

### Auth: `/api/auth`
| Method | Path | Purpose |
|---|---|---|
| POST | `/profile` | Create-or-get user profile. On **create**, `full_name` and `phone_number` are required (onboarding); privacy + notification preferences are initialized to their private defaults. |
| GET | `/profile` | Get current user profile (requires token) |
| PATCH | `/profile` | Update editable fields: full name, phone number, display name, photo, bio |
| PATCH | `/profile/privacy` | Update `privacy` (public profile / show email / show phone opt-ins) |
| PATCH | `/profile/notification-preferences` | Update `notification_preferences` |

### Plants: `/api/plants`
| Method | Path | Purpose |
|---|---|---|
| POST | `/lookup` | Agentic plant lookup (Groq) + Unsplash image |
| POST | `/autonomous` | Create plant with AI-generated care info + auto watering task |
| POST | `/` | Create plant |
| GET | `/` | List user plants |
| GET | `/{plant_id}` | Get plant (ownership-checked) |
| PUT | `/{plant_id}` | Update plant |
| DELETE | `/{plant_id}` | Delete plant |
| GET | `/{plant_id}/tasks` | Tasks for a plant |
| POST | `/{plant_id}/health-check` | Create health check |
| GET | `/{plant_id}/health-checks` | Health check history |

### Tasks: `/api/tasks`
| Method | Path | Purpose |
|---|---|---|
| GET | `/today` | Today's incomplete tasks (priority order) |
| POST | `/{task_id}/complete` | Complete → award points + notification |
| POST | `/{task_id}/snooze` | Push `due_date` forward without completing |
| PATCH | `/{task_id}/reschedule` | Set a new `due_date` explicitly |
| GET | `/` | List tasks (`completed` filter) |
| POST | `/` | Create task |
| PUT | `/{task_id}` | Update task |
| DELETE | `/{task_id}` | Delete task |

### Dashboard: `/api/dashboard`
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Aggregate overview (plants by health, today's tasks, stats) |

### Chat: `/api/chat`
| Method | Path | Purpose |
|---|---|---|
| POST | `/` | Agentic multi-modal chat (Groq) + tool calls + follow-up suggestions |
| POST | `/analyze-image` | Image health analysis (currently mocked) |
| GET | `/weather/{lat}/{lon}` | Weather for a location |
| POST | `/care-plan` | Generates a structured care plan from the plant's profile, adjusted for current weather |

### Images: `/api/images`
| Method | Path | Purpose |
|---|---|---|
| GET | `/plant/{plant_name}` | Unsplash image by name/species |

### MCP (Model Context Protocol): `/api/mcp`
| Method | Path | Purpose |
|---|---|---|
| GET | `/weather/{lat}/{lon}` | Weather + humidity-based recommendation |
| GET | `/plant-info/{name}` | Botanical/care data via Groq |

### Recommendations: `/api/recommendations`
| Method | Path | Purpose |
|---|---|---|
| GET | `/` | List this user's pending personalized recommendations |
| POST | `/generate` | Trigger a fresh recommendation pass (Groq agent + Tavily + weather + `agent_profile`) |
| POST | `/{id}/accept` | Accept → creates a `plants` doc, marks `status: "accepted"` |
| POST | `/{id}/dismiss` | Dismiss → marks `status: "dismissed"`, updates `agent_profile.recommendation_preferences.avoided_plants` |

### Notifications: `/api/notifications`
| Method | Path | Purpose |
|---|---|---|
| WS | `/ws/{user_id}` | Real-time notification channel |
| GET | `/` | List notifications (`unread_only`, `limit`) |
| GET | `/unread-count` | Unread count |
| PUT | `/{id}/read` | Mark read |
| PUT | `/mark-all-read` | Mark all read |
| DELETE | `/{id}` | Delete |

> Certain notification types (see `03-Data-Schema.md`) also enqueue a mirrored document
> in `mail` **and** `email_logs`, gated by the user's `notification_preferences`.

### Leaderboard: `/api/leaderboard`
| Method | Path | Purpose |
|---|---|---|
| GET | `/leaderboard` | Top 100 by score: `display_name`, avatar, score, level, streak, badges, rank always; `email`/`phone_number` **only** for users who opted in via `privacy.show_email`/`show_phone` |
| GET | `/leaderboard/me` | Current user's own rank + full stats (always includes their own contact info, regardless of their privacy flags, since it's their own data) |
| GET | `/stats` | Detailed user stats & completion rate |

> Privacy-safe by default (see `01-PRD.md` §5.10, `04-Rules-of-Engagement.md`). This
> **replaces** the earlier all-users-see-everyone's-contact-info decision.

### Storage: `/api/storage`
| Method | Path | Purpose |
|---|---|---|
| POST | `/upload/plant-image/{plant_id}` | Upload plant image |
| POST | `/upload/document` | Upload document |
| POST | `/upload/profile-photo` | Upload avatar (image only) |
| DELETE | `/delete/{file_path:path}` | Delete file (must be under `users/{uid}/`) |

### System
| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check, also the keep-alive workflow's ping target |

> Frontend note: `api.ts` references a few endpoints not currently implemented
> server-side (`/plants/{id}/schedule`, `/plants/{id}/schedule/complete`,
> `/tasks/generate/{id}`). Resolving this mismatch (implement or remove) is scheduled;
> see `06-Phase-Tracker.md` Phase 1.

---

## 5. Services Layer Notes

**Live & wired to routes:**
- **GroqService** (`groq_service.py`, replaces the retired `ollama_service.py`) handles
  chat plus context-aware follow-up suggestions, plant health analysis, agentic plant
  info lookup, and personalized recommendations. `chat_with_ai` builds a
  `langchain.agents.AgentExecutor` (via `create_tool_calling_agent`) per request over
  four LangChain `@tool`s bound to the calling `user_id` (`get_user_garden`,
  `get_task_history`, `get_weather`, `web_search`), capped via `max_iterations` so the
  reason → tool-call → observe → answer loop stays bounded. It's plain LangChain only,
  no LangGraph anywhere in this codebase. The structured-extraction methods
  (`analyze_plant_health`, `get_plant_info_agentic`) call `ChatGroq` directly in JSON
  mode, no tools needed there. Fallback responses kick in gracefully on errors or when
  Groq is down (there is no local-model fallback anymore).
- **TavilyService** (`tavily_service.py`) is a thin wrapper around `langchain-tavily`'s
  `TavilySearch`, used as the agent's `web_search` tool for grounded, current
  information (recommendations, fact-checking care advice).
- **WeatherService** (`weather_service.py`) fetches OpenWeatherMap current conditions
  and returns mock data when there's no key or on error.
- **PlantService** (`plant_service.py`) handles the Unsplash image fetch, used for both
  `plants.image_url` and `recommendations.image_url` when a plant is added to the
  garden. It reads `UNSPLASH_ACCESS_KEY` from settings (sent as `client_id`), falls back
  to Unsplash's public `demo` client ID (heavily rate-limited) when the key is blank,
  and falls back further to a static Unsplash URL if the request fails outright. It
  also pings each photo's `download_location` after a successful fetch, per Unsplash's
  API Guidelines ("track a photo download" is required whenever a fetched photo is
  actually used, not just searched). `UNSPLASH_APPLICATION_ID` and
  `UNSPLASH_SECRET_KEY` are read into settings but never sent on any request:
  Unsplash's public search endpoint only needs the Access Key, and the other two only
  matter for an OAuth flow this app doesn't do. It also defines an unused
  `generate_care_schedule`.
- **EmailService** (`email_service.py`) writes documents to the Firestore `mail`
  collection consumed by the Firebase Trigger Email extension, **and** writes the
  paired `email_logs` entry for every send, whether event- or schedule-triggered.
- **SchedulerService** (`scheduler_service.py`, new) is an in-process APScheduler
  instance started on app startup. It runs periodic jobs (streak-risk sweep, task-due
  digest, weekly summary) that fan out per-user through `EmailService`, gated by each
  user's `notification_preferences`. This only works reliably because the keep-alive
  workflow (§2 flow 8) keeps the process from being killed between runs.

**Scaffolded / present but NOT wired to any route:**
- **AutonomousPlantService** (`autonomous_plant_service.py`) provides a knowledge base
  (4 species) plus schedule and inventory summary. It is **imported** in `plants.py`
  but its `identify_and_create_plant` is **never called**. The `/plants/autonomous`
  route uses `GroqService.get_plant_info_agentic` directly instead.
- **PlantIDService** (`plant_id_service.py`) handles Plant.ID v2 species
  identification. `identify_plant` is **not referenced by any route** (returns mock
  without a key).
- **AIService** (`ai_service.py`) holds the "PlantMind" persona prompt plus an
  image-analysis stub (`analyze_plant_image` returns a hardcoded healthy assessment).
  ⚠️ `chat.py`'s `/chat/care-plan` calls **`AIService.generate_care_plan`, which does
  not exist**, so this endpoint currently returns HTTP 500. `_research_plant_info`
  returns canned JSON.

**Retired:**
- **Ollama** is fully removed. No `OLLAMA_BASE_URL` / `OLLAMA_MODEL` config, no local
  model dependency, no fallback chain to a local LLM.
- **MultiModalChatService** (`multi_modal_chat.py`) is an empty placeholder file
  (0 lines), unrelated to the Groq migration.

**MCP QA server** (`apps/api/mcp_server.py`, run standalone: `python mcp_server.py`):
| Tool | Purpose |
|---|---|
| `check_health` | Hit `GET /health`, report status + latency |
| `check_api_contract` | Diff the live OpenAPI schema against the routes the core loop depends on |
| `list_routes` | Enumerate every route the running backend exposes |
| `authenticated_request` | Make one authenticated call to any endpoint, given a caller-supplied Firebase ID token |
| `run_smoke_suite` | Chain profile/plants/tasks/leaderboard/notifications checks into one pass/fail report |

No credentials are stored in the server. QA tools take a Firebase ID token (e.g. from
a dedicated QA account) as a call argument, not an env var. Point it at a non-default
backend via `FLOURISH_API_BASE_URL` (defaults to `http://localhost:8000`).

---

## 6. Configuration / Deployment

### Backend `apps/api/.env` (via `core/config.py`, pydantic-settings)
| Variable | Default | Used by |
|---|---|---|
| `ALLOWED_ORIGINS` | localhost dev origins | CORS |
| `GROQ_API_KEY` | "" | **Required.** GroqService: chat, lookup, recommendations |
| `GROQ_MODEL` | `qwen/qwen3.6-27b` | GroqService, the model used for both the tool-calling agent and structured extraction (LLM backbone) |
| `TAVILY_API_KEY` | "" | **Required for grounded recommendations.** GroqService web-search tool |
| `UNSPLASH_APPLICATION_ID` | "" | PlantService, captured but not sent on any request (see §5) |
| `UNSPLASH_ACCESS_KEY` | "" | PlantService, sent as `client_id`; falls back to the rate-limited public `demo` ID when blank |
| `UNSPLASH_SECRET_KEY` | "" | PlantService, captured but not sent on any request (see §5) |
| `PLANT_ID_API_KEY` | "" | PlantIDService (unwired) |
| `OPENWEATHER_API_KEY` | "" | WeatherService |
| `FIREBASE_PROJECT_ID` / `_PRIVATE_KEY_ID` / `_PRIVATE_KEY` / `_CLIENT_EMAIL` / `_CLIENT_ID` / `_CLIENT_X509_CERT_URL` | "" | Firebase Admin init: individual service-account fields, **no JSON key file anywhere**; lazily initialized on first authenticated request, not at import time (see `core/auth.py`). `FIREBASE_TYPE`, `_AUTH_URI`, `_TOKEN_URI`, `_AUTH_PROVIDER_X509_CERT_URL`, `_UNIVERSE_DOMAIN` default to the standard Google values and rarely need overriding. |
| `SECRET_KEY` | placeholder | unused (Firebase auth) |

> Never commit real values for the `FIREBASE_*` fields (see `04-Rules-of-Engagement.md`
> Rule 5); `apps/api/.env` is git-ignored. `FIREBASE_PRIVATE_KEY` must keep its
> literal `\n` line breaks (wrap the value in double quotes in `.env`); pydantic-settings
> converts them to real newlines when loading. On Render these are set directly as
> environment variables, no Secret File needed.

### Frontend `apps/web/.env`
| Variable | Purpose |
|---|---|
| `VITE_FIREBASE_API_KEY` / AUTH_DOMAIN / PROJECT_ID / STORAGE_BUCKET / MESSAGING_SENDER_ID / APP_ID | Firebase web config |
| `VITE_API_URL` | Backend base (default `http://localhost:8000`) |
| `VITE_WS_URL` | WebSocket base for the notification channel (default `ws://localhost:8000`) |

### Deployment
Deliberately not being worked on right now; see the note in §1. `render.yaml` exists
from Phase 0 and is left as-is; no `vercel.json` yet. Revisit once the phases in
`06-Phase-Tracker.md` are done.

---

> **Related docs:** `01-PRD.md` · `03-Data-Schema.md` ·
> `04-Rules-of-Engagement.md` · `05-UIUX-Rulebook.md` · `06-Phase-Tracker.md`
