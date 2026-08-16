# Flourish

*Transform your black thumb into a green one.*

![React](https://img.shields.io/badge/React_18-black?style=flat-square&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-black?style=flat-square&logo=typescript&logoColor=3178C6)
![Vite](https://img.shields.io/badge/Vite-black?style=flat-square&logo=vite&logoColor=B73BFE)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-black?style=flat-square&logo=tailwindcss&logoColor=38B2AC)
![FastAPI](https://img.shields.io/badge/FastAPI-black?style=flat-square&logo=fastapi&logoColor=009688)
![Python](https://img.shields.io/badge/Python_3.12-black?style=flat-square&logo=python&logoColor=3776AB)
![LangChain](https://img.shields.io/badge/LangChain-black?style=flat-square&logo=langchain&logoColor=1C3C3C)
![Groq](https://img.shields.io/badge/Groq-black?style=flat-square&logo=groq&logoColor=F55036)
![Firebase](https://img.shields.io/badge/Firebase-black?style=flat-square&logo=firebase&logoColor=FFCA28)
![Vercel](https://img.shields.io/badge/Deployed_on-Vercel-black?style=flat-square&logo=vercel&logoColor=white)
![Render](https://img.shields.io/badge/API_on-Render-black?style=flat-square&logo=render&logoColor=46E3B7)

**[flourish-web-iota.vercel.app](https://flourish-web-iota.vercel.app/)**

Most people don't kill plants because they don't care. They kill plants because caring is hard to do consistently, and every plant needs something slightly different, and nobody tells you *when* until it's already too late. You water on Sundays because that's the day you remember, not because that's the day your fern actually needs it. By the time the leaves say something's wrong, something's already wrong.

Flourish exists because we got tired of that gap — between wanting to keep something alive and actually knowing how.

## What it is

Flourish isn't a watering-reminder app with a plant illustration slapped on it. It's closer to a second pair of eyes on your garden — one that actually knows the difference between a pothos and a peace lily, and treats them like it.

You add a plant, and from that moment it isn't a generic entry in a list. It's a living thing with a species, a light requirement, a watering rhythm, all pulled from real horticultural data rather than guessed. Its care schedule isn't a fixed countdown — it moves when your plant's situation changes. Skip a watering, and the plan doesn't just nag you later; it adjusts. That's the whole idea: care that responds, instead of a checklist that doesn't know it's being ignored.

And when you're not sure what's going on — a curling leaf, a yellow patch, a plant that's just *acting weird* — you don't have to go dig through five different forum threads with five different answers. You ask. PlantMind, the assistant built into Flourish, is there for exactly that: real plant-care questions, answered with the same grounded knowledge behind your care schedules, not a generic chatbot improvising.

## What it feels like day-to-day

You open the app to a garden, not a dashboard. A short list of what actually needs doing today — not a wall of everything, all the time. You check things off, your plants respond to the care you give them, and the app quietly notices — a streak forms, your garden's health trends upward, and there's a small, honest sense of *I'm actually good at this now*. Not because you memorized a schedule, but because something was watching the details so you didn't have to.

If you're the type who likes a little friendly competition, there's a leaderboard for that too — because keeping a plant alive for six months is a real accomplishment and it should feel like one.

## The bet we're making

Most plant apps assume the hard part is remembering. We think the hard part is *knowing* — knowing what your specific plant needs, right now, given what's actually happened to it lately. So Flourish leans almost all of its intelligence into that: grounding recommendations in real plant-care data first, using AI to fill the gaps and answer what a database can't, and never pretending a generic tip is personal advice.

We also think caring for something living shouldn't feel like admin work. So the app is built to feel warm rather than clinical — more like a garden journal that happens to be smart, less like a spreadsheet with push notifications.

## The stack, for reference

Flourish is a monorepo: a React frontend talking to a FastAPI backend, with Firebase doing the account and data layer for both.

**Frontend** — React 18 + TypeScript, built with Vite. UI is Tailwind CSS on top of shadcn/ui (Radix primitives), with TanStack React Query handling server state, React Router for navigation, and react-hook-form + Zod for forms. Charts via Recharts, PlantMind's replies rendered with react-markdown.

**Backend** — FastAPI on Python 3.12, served by Uvicorn. The care-agent logic runs on LangChain with langchain-groq (Groq for LLM inference) and langchain-tavily (grounded web search), behind an MCP server integration. APScheduler drives the recurring jobs (streak checks, task digests, weekly summaries) when running on a host with a persistent process.

**Data & intelligence** — Perenual supplies the deterministic plant-care facts (watering cadence, sunlight needs) that schedules and recommendations are grounded in; Groq fills in what a database can't answer; OpenWeather adds weather-aware adjustments; Unsplash sources plant photography.

**Platform** — Firebase for Authentication (Google Sign-In), Firestore (the database), and Storage (images), plus the Trigger Email extension for notification delivery. Deployed as a Vite build on Vercel (frontend) and a Docker image on Render (backend), with GitHub Actions running CI and keeping the API warm.

## At a glance

- 🪴 **Grounded, not guessed** — care facts come from a real horticultural database, not an LLM improvising a watering schedule
- 🔁 **Schedules that move** — miss a watering, and the plan adjusts instead of quietly falling out of sync with reality
- 💬 **PlantMind** — an assistant that actually answers plant questions, backed by the same data as your care plan
- 🏆 **Progress that feels like progress** — streaks, garden health trends, and a leaderboard for the mildly competitive

## Try it

**→ [flourish-web-iota.vercel.app](https://flourish-web-iota.vercel.app/)**

Sign in with Google, add the plant that's currently judging you from across the room, and see what Flourish thinks it actually needs.

---

*Building on this, or just curious how it's put together? The engineering docs live in [`docs/`](docs/), starting with [`docs/01-PRD.md`](docs/01-PRD.md).*
