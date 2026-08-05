# 🌱 Flourish
### AI-Powered Plant Care That Actually Works

> Transform your black thumb into a green one with intelligent plant monitoring, proactive care recommendations, and personalized schedules that adapt to your plants' unique needs.

---

## 🔥 **Firebase Integration Complete!**

✅ **Firebase Authentication** (Google Sign-In)  
✅ **Cloud Firestore Database** (Real-time sync)  
✅ **Firebase Storage** (File uploads)  
✅ **Production Ready** (Security & documentation)

**→ [Full documentation set](docs/)** — start with [`docs/01-PRD.md`](docs/01-PRD.md) and [`docs/02-Tech-Stack-Architecture.md`](docs/02-Tech-Stack-Architecture.md)

---

## 🌿 Why Flourish?

Most plant care apps are glorified reminders that treat every plant the same. **Flourish is different.**

We've built an AI agent that actually understands your plants - monitoring their health, predicting problems before they happen, and creating dynamic care schedules that evolve based on how your plants respond. No more guesswork, no more dead plants.

### ✨ What Makes It Special

🧠 **Intelligent Monitoring**  
Our AI continuously analyzes your plants' health metrics and environmental conditions, spotting issues before they become problems.

📸 **Multi-Modal Analysis**  
Take a photo of your plant and get instant health assessments, disease identification, and personalized care recommendations.

🎯 **Adaptive Scheduling**  
Care plans that learn and adjust based on your plants' actual responses - not generic timers that ignore reality.

💬 **Expert AI Assistant**  
Chat with our plant care expert AI for instant answers about watering, lighting, diseases, and more.

📊 **Garden Dashboard**  
Beautiful visualizations of your garden's overall health with actionable insights and progress tracking.

---

## 🚀 Experience the Difference

### Before Flourish
- ❌ Generic watering reminders every 3 days
- ❌ Guessing what's wrong when plants look sick  
- ❌ One-size-fits-all care instructions
- ❌ Learning about problems too late

### With Flourish
- ✅ Smart schedules that adapt to each plant's needs
- ✅ AI-powered health analysis from photos
- ✅ Personalized care plans that evolve over time
- ✅ Proactive alerts before problems develop

---

## 🎨 Built for Plant Lovers

Flourish features a beautiful, cheerful design that makes plant care feel delightful rather than daunting. Our custom color palette and intuitive interface create a welcoming experience that encourages consistent care.

**Core Features:**
- 🌱 **Plant Health Tracking** - Monitor growth, watering needs, and overall wellness
- 📅 **AI-Generated Schedules** - Dynamic care plans that adapt to plant responses  
- 🔍 **Image Analysis** - Instant plant health assessment from photos
- 💡 **Smart Insights** - Proactive recommendations to optimize plant health
- 📈 **Progress Tracking** - Visualize your garden's health trends over time

---

## 🛠️ Technology Stack

Flourish is built with modern, reliable technologies to ensure fast performance and seamless user experience:

**Frontend:** React 18 + TypeScript + Vite for lightning-fast development and optimized builds  
**UI/UX:** Tailwind CSS + shadcn/ui components with custom Flourish design system  
**Backend:** FastAPI (Python) with clean architecture and type-safe data models  
**AI Integration:** Groq language models for advanced plant care intelligence  
**Authentication:** Firebase Auth with Google OAuth for secure, hassle-free sign-in  
**State Management:** React Query for efficient server state and caching  
**Development:** Turborepo monorepo with optimized build pipelines

---

## � Quick Start

### Prerequisites
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Firebase Account** - Project: `flourish-de908` (already configured)
- **Groq API key** - required, no local model fallback ([console.groq.com](https://console.groq.com))
- **Tavily API key** - required for grounded recommendations ([tavily.com](https://tavily.com))

### One-time backend setup
All `*:api` npm scripts run through a virtualenv at `apps/api/.venv` (they call
`.venv/Scripts/python` directly, not whatever `python` happens to be on your `PATH` -
that was a real bug: it silently ran against a system Python with none of the project's
dependencies installed). Create it once before your first `npm run dev`:
```bash
cd apps/api
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
cd ../..
```
After that, `npm run dev` / `npm test` / `npm run build` all work from the repo root.

### NPM Scripts (Monorepo Management)

**Development (runs both services):**
```bash
npm run dev              # Start both API and web in watch mode
npm run dev:api          # Start API only (port 8000)
npm run dev:web          # Start web only (port 5173)
```

**Production:**
```bash
npm run build            # Build both services
npm run build:api        # Install/refresh backend dependencies into apps/api/.venv
npm run build:web        # Build web for production
npm start                # Start both services in production mode
```

**Testing:**
```bash
npm test                 # Run all tests (frontend + backend)
npm run test:api         # Run backend tests (pytest)
npm run test:web         # Run frontend tests (vitest)
npm run test:watch       # Run frontend tests in watch mode
npm run test:ui          # Open vitest UI
```

**Maintenance:**
```bash
npm run lint             # Lint all workspaces
npm run clean            # Clean all build artifacts
npm run install:all      # Install all dependencies
npm run typecheck        # TypeScript type checking
```

**Access:**
- 🌐 Frontend: http://localhost:5173
- ⚙️ Backend: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs

### Manual Start (Alternative)

**Backend:**
```bash
cd apps/api
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

### First Time Setup

1. **Firebase Configuration**
   - Download the service-account key JSON for `flourish-de908` and copy its fields
     into the `FIREBASE_*` variables in `apps/api/.env` (`FIREBASE_PROJECT_ID`,
     `FIREBASE_PRIVATE_KEY_ID`, `FIREBASE_PRIVATE_KEY`, `FIREBASE_CLIENT_EMAIL`,
     `FIREBASE_CLIENT_ID`, `FIREBASE_CLIENT_X509_CERT_URL`) — there's no key file on
     disk to manage, `apps/api/.env` is already git-ignored.
   - `FIREBASE_PRIVATE_KEY` must be double-quoted with its `\n` line breaks kept
     literal, exactly as they appear in the downloaded JSON's `private_key` field.
   - Add `GROQ_API_KEY` and `TAVILY_API_KEY` to `apps/api/.env` — both required, see
     `docs/02-Tech-Stack-Architecture.md` §6.

2. **Sign In**
   - Go to http://localhost:5173
   - Click "Sign in with Google"
   - First-time sign-in asks for your full name + phone number (onboarding), then
     you're in — start managing your plants! 🌱

---

## 🔥 Tech Stack

![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![Groq](https://img.shields.io/badge/Groq-00A0FF?style=for-the-badge&logo=groq&logoColor=white)

---

## 📂 Project Structure

```
Flourish/
├── apps/
│   ├── api/                    # Backend (FastAPI + Python)
│   │   ├── api/
│   │   │   ├── core/          # Auth & config
│   │   │   ├── db/            # Firestore & Storage
│   │   │   ├── routes/        # API endpoints
│   │   │   └── services/      # Business logic
│   │   ├── main.py            # API entry point
│   │   └── requirements.txt   # Python dependencies
│   └── web/                   # Frontend (React + TypeScript)
│       ├── src/
│       │   ├── components/    # React components
│       │   ├── hooks/         # Custom hooks (useAuth)
│       │   ├── lib/           # Firebase & utilities
│       │   ├── pages/         # App pages
│       │   └── integrations/  # API client
│       └── package.json       # Node dependencies
├── docs/                       # Full documentation set (PRD, architecture, schema, ...)
├── .github/workflows/          # CI (ci.yml) + Render keep-alive ping (keep-alive.yml)
├── render.yaml                 # Render deployment (backend)
├── vercel.json                 # Vercel deployment (frontend)
└── README.md                   # This file
```

---

## 🔐 Firebase Services

This project uses **Firebase** for all backend services:

### Authentication
- Google Sign-In provider
- JWT token-based API security
- Automatic session management

### Database (Firestore)
- **profiles** - User profiles & gamification
- **plants** - Plant inventory
- **care_tasks** - Scheduled tasks
- **notifications** - Real-time alerts
- **health_checks** - Plant health tracking

### Storage
- Plant images: `users/{userId}/plants/{plantId}/`
- Documents: `users/{userId}/documents/`
- Profile photos: `users/{userId}/profile/`

**Firebase Console:** https://console.firebase.google.com/project/flourish-de908

---

## 🚀 Deployment

Frontend → **Vercel**, backend → **Render**, both already have config files in this
repo (`vercel.json`, `render.yaml`). You said you already have accounts for both, so
this is the short version - full detail in `docs/02-Tech-Stack-Architecture.md` §6.

### Backend (Render)
1. New Web Service → connect this repo. Render will read `render.yaml` (root
   directory `apps/api`, Python 3.12, health check `/health`).
2. **Environment** tab → set the `sync: false` vars from `render.yaml`:
   `ALLOWED_ORIGINS` (your Vercel URL), `GROQ_API_KEY`, `TAVILY_API_KEY`,
   `OPENWEATHER_API_KEY`, `PLANT_ID_API_KEY`, `UNSPLASH_APPLICATION_ID`,
   `UNSPLASH_ACCESS_KEY`, `UNSPLASH_SECRET_KEY` (only the Access Key is actually
   used - see `docs/02-Tech-Stack-Architecture.md` §5), and the Firebase fields
   below - **no Secret File needed**, Firebase Admin credentials are plain env vars:
   `FIREBASE_PROJECT_ID`, `FIREBASE_PRIVATE_KEY_ID`, `FIREBASE_PRIVATE_KEY` (paste
   with its literal `\n` sequences intact, in quotes), `FIREBASE_CLIENT_EMAIL`,
   `FIREBASE_CLIENT_ID`, `FIREBASE_CLIENT_X509_CERT_URL`.
3. Deploy. Confirm `GET https://<your-service>.onrender.com/health` returns `{"status":"ok"}`.

### Backend (Docker, alternative to Render's native Python runtime)
`apps/api/Dockerfile` is a working multi-stage build (build context is the repo root,
since it references `apps/api/...` paths):
```bash
npm run docker:build:api   # docker build -f apps/api/Dockerfile -t flourish-api .
npm run docker:run:api     # docker run --rm -p 8000:8000 --env-file apps/api/.env flourish-api
```
`/health` works even with no Firebase credentials configured (auth initializes lazily
on first authenticated request, not at startup - see `docs/02-Tech-Stack-Architecture.md`
§5). Authenticated routes work out of the box too - `--env-file apps/api/.env` passes
the `FIREBASE_*` fields straight through as env vars, no file mount needed.

### Frontend (Vercel)
1. New Project → import this repo. `vercel.json` at the repo root handles the
   monorepo build (`apps/web` → `apps/web/dist`) and SPA rewrites - no need to set a
   Root Directory.
2. **Environment Variables** → copy every `VITE_*` key from `apps/web/.env`, plus set
   `VITE_API_URL` and `VITE_WS_URL` (`wss://...`) to your Render URL.
3. Deploy.
4. Back in Render, update `ALLOWED_ORIGINS` to include the resulting Vercel domain,
   then redeploy the backend so CORS allows it.

### Keep the backend from sleeping
Render's free tier spins down after ~15 minutes idle. `.github/workflows/keep-alive.yml`
pings `/health` every 10 minutes to prevent that (and to keep the in-process
`SchedulerService` jobs firing reliably). After the backend is deployed:
1. Repo → Settings → Secrets and variables → Actions → **Variables** tab.
2. Add `RENDER_API_URL` = `https://<your-service>.onrender.com`.
3. The workflow picks it up on its next scheduled run (or trigger it manually from the Actions tab).

### Email (Firebase Trigger Email extension)
`firebase.json` / `.firebaserc` / `extensions/firestore-send-email.env` are already in
the repo. To actually enable sending:
1. `firebase login`, then from the repo root: `firebase ext:install firebase/firestore-send-email --project=flourish-de908`
2. When prompted, provide your SMTP connection URI and password (stored in Secret
   Manager, never written to the repo) - Gmail/Workspace SMTP or a transactional
   provider both work.
3. `firebase deploy --only extensions`

Without this step, `EmailService` still writes to the `mail` collection correctly -
the documents just won't be picked up and sent until the extension is installed.

---

<div align="center">

**Ready to transform your plant care experience?**  
*Start your journey with Flourish today.* 🌿✨

</div>