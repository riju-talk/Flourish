# 🌱 Flourish
### AI-Powered Plant Care That Actually Works

> Transform your black thumb into a green one with intelligent plant monitoring, proactive care recommendations, and personalized schedules that adapt to your plants' unique needs.

---

## 🔥 **Firebase Integration Complete!**

✅ **Firebase Authentication** (Google Sign-In)  
✅ **Cloud Firestore Database** (Real-time sync)  
✅ **Firebase Storage** (File uploads)  
✅ **Production Ready** (Security & documentation)

**→ [Architecture Documentation](ARCHITECTURE.md)**

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
- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Firebase Account** - Project: `flourish-de908` (already configured)

### One-Command Start (Windows)
```bash
# Using batch file (recommended)
start.bat

# Or using PowerShell
.\start.ps1
```

This automated script will:
- ✅ Check all dependencies
- ✅ Install missing packages
- ✅ Start backend API on port 8000
- ✅ Start frontend on port 5173
- ✅ Open the app in your browser

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
npm run build:api        # Build API Docker image
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
   - Service account key is already configured at `apps/api/firebase-service-account.json`
   - Environment variables are set in `.env` files

2. **Sign In**
   - Go to http://localhost:5173
   - Click "Sign in with Google"
   - Start managing your plants! 🌱

3. **Optional: AI Features**
   - Install [Ollama](https://ollama.ai) for local AI
   - Run: `ollama pull llama3`
   - Or use Groq API (add `GROQ_API_KEY` to `apps/api/.env`)

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
├── ARCHITECTURE.md            # System architecture docs
├── README.md                  # This file
└── start.ps1                  # Development start script
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

<div align="center">

**Ready to transform your plant care experience?**  
*Start your journey with Flourish today.* 🌿✨

</div>