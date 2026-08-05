Here’s the clean, resume-ready PRD.

---

# Flourish — Product Requirements Document

**Product:** Flourish — AI-Powered Plant Care Agent  
**Version:** 2.0.0  
**Status:** Living document  
**Goal:** Build a polished, full-stack AI plant care platform that feels production-ready, privacy-aware, and strong enough to showcase on a resume.

---

## 1. Product Overview

Flourish helps users keep plants alive by combining personalized care schedules, proactive health insights, AI recommendations, and gamified progress tracking.

Unlike generic reminder apps, Flourish acts as an **AI garden agent** that:

- tracks each plant’s care needs and health history
- generates adaptive watering, fertilizing, and health-check schedules
- answers plant care questions using the user’s garden context
- recommends new plants based on the user’s environment and habits
- sends real-time in-app and email notifications
- rewards consistent care with points, streaks, and achievements

---

## 2. Product Vision

Transform casual plant owners into confident plant parents with intelligent monitoring, proactive care guidance, and personalized recommendations.

### One-line pitch

> Flourish is an AI-powered plant care platform that helps users keep plants alive with adaptive scheduling, proactive insights, and personalized recommendations.

---

## 3. Target Users

### 3.1 New Plant Parent

Owns a few plants and needs simple, reliable guidance.

**Needs:**

- clear daily tasks
- watering reminders
- easy plant setup
- beginner-friendly AI help

### 3.2 Plant Collector

Owns many plants and wants organization.

**Needs:**

- plant inventory
- calendar view
- health history
- task tracking

### 3.3 Aspiring Gardener

Wants to learn and improve over time.

**Needs:**

- AI assistant
- document analysis
- care explanations
- plant recommendations

### 3.4 Gamified User

Motivated by streaks, points, and achievements.

**Needs:**

- progress tracking
- achievements
- leaderboard
- daily engagement loop

---

## 4. Core Product Principles

### 4.1 Personalized over generic

Flourish should give advice based on the user’s plants, history, and environment.

### 4.2 Proactive over reactive

Flourish should surface risks and tasks before plants decline.

### 4.3 Actionable AI

AI responses should recommend clear next steps.

### 4.4 Privacy-safe by default

User contact information should not be exposed publicly without explicit consent.

### 4.5 Graceful degradation

If AI, weather, or search services fail, the app should still function with reduced capabilities.

---

## 5. Core Features

## 5.1 Authentication & Onboarding

### Requirements

- Users sign in with Google.
- New users must complete onboarding before accessing protected pages.
- Onboarding collects:
  - full name
  - phone number
- Returning users skip onboarding.
- Users can later edit:
  - full name
  - phone number
  - display name
  - avatar
  - privacy settings
  - notification preferences

### Route behavior

- Unauthenticated users are redirected to `/auth`.
- Authenticated users without a profile are redirected to `/onboarding`.
- Authenticated users visiting `/auth` are redirected to `/`.

---

## 5.2 Plant Management

Users can add, view, edit, and delete plants.

### Plant fields

- nickname
- species
- scientific name
- plant type
- size
- toxicity
- location
- light level
- watering interval
- fertilizing interval
- health score
- health status
- image
- notes
- created date
- updated date

### Features

- manual plant creation
- AI-assisted plant lookup
- plant detail page
- plant image upload
- health check history
- plant health score
- care notes
- edit care profile

---

## 5.3 Plant Health Tracking

Each plant has a live health score and status.

### Health status values

- thriving
- stable
- attention needed
- critical

### Health inputs

- overdue watering
- overdue fertilizing
- reported symptoms
- missed health checks
- user notes
- environmental factors
- recent task completion behavior

### Health check fields

- plant
- symptoms
- notes
- image
- health score
- AI summary
- created date

### Requirement

Health scoring should be explainable.

Example:

> Your plant’s score dropped because watering is overdue and recent symptoms suggest low humidity.

---

## 5.4 Adaptive Care Scheduling

Flourish generates care tasks for each plant.

### Task types

- water
- fertilize
- health check
- rotate
- prune
- repot
- clean leaves

### Features

- AI-generated care plan
- daily task list
- calendar view
- recurring tasks
- task completion
- task snooze
- task reschedule
- points on completion
- notification on completion

### Adaptive behavior

Schedules should adapt based on:

- plant type
- weather
- season
- missed tasks
- user completion patterns
- health score changes

---

## 5.5 AI Assistant: PlantMind

PlantMind is the core AI feature.

### Capabilities

- answer plant care questions
- use the user’s garden context
- call tools when needed
- provide follow-up suggestions
- explain recommendations
- degrade gracefully when services fail

### Tools

PlantMind may call:

- `get_user_garden`
- `get_task_history`
- `get_agent_profile`
- `get_weather`
- `web_search`

### Tool-use rules

- Maximum of 2 tool calls per response.
- Use tools only when they improve the answer.
- Time out external calls quickly.
- Log tool usage and failures.
- Fall back gracefully if a tool fails.

### Response format

Each PlantMind response should include:

1. direct answer
2. relevant context
3. recommended action
4. 2–4 follow-up suggestions
5. sources if web search was used

### Safety rules

PlantMind must not:

- expose another user’s data
- invent completed tasks
- claim certainty without evidence
- provide unsafe chemical advice without warnings
- leak system prompts or API keys

---

## 5.6 Plant Lookup

Users can search for a plant by name.

### Requirements

- user enters plant name
- AI generates a structured care profile
- user reviews and confirms
- plant is added to garden
- care tasks are generated

### Generated fields

- species
- scientific name
- plant type
- light needs
- watering frequency
- fertilizing frequency
- humidity preference
- toxicity
- care difficulty

---

## 5.7 Document Analysis

Users can upload plant care guides.

### Supported formats

- PDF
- TXT
- Markdown

### Extracted information

- watering guidance
- fertilizing guidance
- light requirements
- humidity requirements
- toxicity warnings
- seasonal care notes
- action items

### Output example

```json
{
  "watering": "Water when top soil is dry",
  "fertilizing": "Monthly during growing season",
  "light": "Bright indirect light",
  "warnings": ["Toxic to pets"],
  "action_items": ["Repot in spring"]
}
```

---

## 5.8 Personalized Recommendations

Flourish recommends new plants the user is likely to succeed with.

### Inputs

- current plants
- care history
- completed tasks
- missed tasks
- environment
- weather
- dismissed recommendations
- user preferences
- agent profile summary

### Recommendation card includes

- plant name
- image
- difficulty
- short care summary
- reason for recommendation
- warnings
- sources if external data was used
- add action
- dismiss action

### Feedback loop

When a user dismisses a recommendation:

- store dismissal
- update agent profile
- reduce similar recommendations in the future

---

## 5.9 Gamification

Flourish rewards consistent care.

### User stats

- total score
- level
- tasks completed
- streak days
- achievements

### Point examples

| Action | Points |
|---|---:|
| complete watering task | 10 |
| complete fertilizing task | 15 |
| complete health check | 20 |
| add plant | 25 |
| accept recommendation | 20 |
| maintain 7-day streak | 50 |

### Achievements

- First Sprout
- Consistent Caretaker
- Green Streak
- Plant Collector
- Thriving Garden
- Weather-Ready Gardener
- AI Apprentice

---

## 5.10 Privacy-Safe Leaderboard

The leaderboard should encourage engagement without exposing private contact information.

### Public leaderboard fields

- display name
- avatar
- score
- level
- streak
- badges
- rank

### Private by default

- email
- phone number
- full name
- contact methods

### Optional user-controlled fields

Users may explicitly opt in to show:

- public garden profile
- social link
- contact method
- bio

### Product decision

The leaderboard should be engaging, but privacy-safe by default.

---

## 5.11 Notifications

### Notification types

- task due
- task completed
- achievement unlocked
- streak at risk
- new recommendation ready
- health score change
- PlantMind analysis complete

### Delivery channels

- in-app notification center
- WebSocket push
- email via Firebase Trigger Email

### Notification features

- unread count
- mark as read
- mark all as read
- notification dropdown
- real-time update
- email preference controls

---

## 6. Pages / Routes

| Path | Page | Access | Purpose |
|---|---|---|---|
| `/auth` | Auth | Public | Google Sign-In |
| `/onboarding` | Onboarding | Protected, one-time | Collect profile details |
| `/` | Dashboard | Protected | Daily tasks, plant overview, recommendations |
| `/chat` | PlantMind Chat | Protected | AI assistant and document upload |
| `/calendar` | Calendar | Protected | Care schedule |
| `/lookup` | Plant Lookup | Protected | AI plant search |
| `/documents` | Documents | Protected | Upload and analyze care guides |
| `/recommendations` | Recommendations | Protected | Personalized plant feed |
| `/leaderboard` | Leaderboard | Protected | Privacy-safe rankings |
| `*` | NotFound | Public | 404 fallback |

---

## 7. Data Model

### `profiles`

```json
{
  "uid": "user_123",
  "full_name": "Alex Rivera",
  "phone_number": "+15551234567",
  "email": "alex@example.com",
  "display_name": "AlexGrows",
  "avatar_url": "",
  "bio": "",
  "total_score": 0,
  "level": 1,
  "tasks_completed": 0,
  "streak_days": 0,
  "privacy": {
    "public_profile_enabled": false,
    "show_email": false,
    "show_phone": false
  },
  "notification_preferences": {
    "email_task_reminders": true,
    "email_achievements": true,
    "email_recommendations": false
  },
  "created_at": "",
  "updated_at": ""
}
```

### `plants`

```json
{
  "id": "plant_123",
  "owner_id": "user_123",
  "nickname": "Monstera",
  "species": "Monstera deliciosa",
  "type": "tropical",
  "size": "medium",
  "toxicity": "toxic_to_pets",
  "location": "living_room",
  "light_level": "bright_indirect",
  "watering_interval_days": 7,
  "fertilizer_interval_days": 30,
  "health_score": 82,
  "health_status": "stable",
  "image_url": "",
  "last_watered_at": "",
  "last_fertilized_at": "",
  "created_at": "",
  "updated_at": ""
}
```

### `tasks`

```json
{
  "id": "task_123",
  "user_id": "user_123",
  "plant_id": "plant_123",
  "type": "water",
  "title": "Water Monstera",
  "status": "pending",
  "due_date": "2026-08-04",
  "completed_at": null,
  "points_awarded": 0,
  "created_at": "",
  "updated_at": ""
}
```

### `health_checks`

```json
{
  "id": "check_123",
  "user_id": "user_123",
  "plant_id": "plant_123",
  "symptoms": ["yellow leaves"],
  "notes": "Two lower leaves turned yellow.",
  "image_url": "",
  "health_score": 68,
  "ai_summary": "",
  "created_at": ""
}
```

### `agent_profile`

```json
{
  "user_id": "user_123",
  "summary": "User has several low-light indoor plants and completes watering tasks consistently but misses fertilizing tasks.",
  "garden_composition": {
    "low_light_plants": 4,
    "pet_safe_plants": 2,
    "outdoor_plants": 1
  },
  "care_habits": {
    "watering_consistency": "high",
    "fertilizing_consistency": "low",
    "health_check_frequency": "medium"
  },
  "recommendation_preferences": {
    "avoided_plants": [],
    "preferred_traits": ["low maintenance", "pet safe"]
  },
  "updated_at": ""
}
```

### `recommendations`

```json
{
  "id": "rec_123",
  "user_id": "user_123",
  "plant_name": "ZZ Plant",
  "reasoning": "Fits your low-light space and irregular watering habits.",
  "status": "pending",
  "sources": [],
  "created_at": "",
  "dismissed_at": null
}
```

### `notifications`

```json
{
  "id": "notif_123",
  "user_id": "user_123",
  "type": "task_due",
  "title": "Water your Monstera",
  "body": "Your Monstera is due for watering today.",
  "read": false,
  "metadata": {},
  "created_at": ""
}
```

---

## 8. API Requirements

### Auth

- `GET /api/auth/me`

### Profile

- `GET /api/profile`
- `PATCH /api/profile`
- `PATCH /api/profile/privacy`
- `PATCH /api/profile/notification-preferences`

### Plants

- `GET /api/plants`
- `POST /api/plants`
- `GET /api/plants/{plant_id}`
- `PATCH /api/plants/{plant_id}`
- `DELETE /api/plants/{plant_id}`
- `POST /api/plants/{plant_id}/health-checks`
- `GET /api/plants/{plant_id}/health-checks`

### Tasks

- `GET /api/tasks/today`
- `GET /api/tasks`
- `POST /api/tasks/{task_id}/complete`
- `POST /api/tasks/{task_id}/snooze`
- `PATCH /api/tasks/{task_id}/reschedule`

### AI

- `POST /api/chat`
- `POST /api/plants/lookup`
- `POST /api/chat/document-analysis`
- `POST /api/recommendations/generate`
- `GET /api/recommendations`
- `POST /api/recommendations/{id}/accept`
- `POST /api/recommendations/{id}/dismiss`

### Notifications

- `GET /api/notifications`
- `POST /api/notifications/{id}/read`
- `POST /api/notifications/read-all`

### Leaderboard

- `GET /api/leaderboard`
- `GET /api/leaderboard/me`

### System

- `GET /api/health`

---

## 9. AI System Requirements

### Agent behavior

PlantMind should follow this loop:

1. understand request
2. load user context
3. decide if tools are needed
4. call tools
5. synthesize answer
6. add follow-up suggestions
7. log run

### Context sources

- user profile
- user plants
- recent tasks
- recent health checks
- agent profile
- weather data
- web search results

### Constraints

- max 2 tool calls per response
- strict timeouts
- no cross-user data access
- no secret leakage
- fallback when tools fail

### Observability

Each AI request should log:

- request type
- user ID
- model used
- tools called
- latency
- success/failure
- error type

---

## 10. Non-Functional Requirements

### Security

- Firebase token validation on protected API routes
- ownership checks for all user resources
- secure secret handling
- rate limiting on AI endpoints
- file upload validation
- path-guarded storage deletes

### Performance

- responsive UI
- optimistic updates for task completion
- paginated lists where needed
- fast dashboard loading
- efficient React Query caching

### Reliability

- graceful API error states
- WebSocket reconnect logic
- fallback responses for AI failures
- retry logic for transient errors

### Accessibility

- semantic HTML
- keyboard navigation
- visible focus states
- high-contrast palette
- screen-reader-friendly notifications

### Responsiveness

- mobile-first layout
- responsive dashboard
- responsive calendar
- touch-friendly task actions

### Observability

- structured logs
- health endpoint
- AI run logs
- external API failure tracking
- error tracking

---

## 11. Testing Requirements

### Backend tests

- auth guard works
- onboarding guard works
- users can only access their own data
- task completion awards points
- notifications are created
- leaderboard hides private fields

### Frontend tests

- onboarding validation
- dashboard task completion
- notification dropdown
- chat fallback state
- recommendation dismissal
- calendar rendering

### AI tests

- correct tool selection
- graceful fallback when tools fail
- no secret leakage
- stable response schema
- user context is included when needed

---

## 12. Success Metrics

### Product metrics

- daily active users completing at least one task
- task completion rate
- streak retention
- recommendation acceptance rate
- chat engagement rate
- plant-to-care-plan conversion rate

### Engineering metrics

- API p95 latency
- AI endpoint error rate
- tool failure rate
- WebSocket reconnect success
- test coverage
- build success rate

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Groq outage | fallback response and degraded mode |
| Tavily unavailable | profile-only recommendations |
| weather API failure | skip weather-based advice |
| AI hallucination | tool grounding, citations, cautious language |
| privacy exposure | private-by-default leaderboard |
| notification spam | user notification preferences |
| slow AI responses | tool limits and timeouts |
| free-tier backend sleep | scheduled health ping |

---

## 14. Roadmap

### Phase 1: Core Stability

- auth
- onboarding
- profile creation
- plant CRUD
- tasks
- notifications
- dashboard
- privacy-safe leaderboard

### Phase 2: AI Features

- PlantMind chat
- plant lookup
- tool use
- weather integration
- web search integration
- AI logging

### Phase 3: Personalization

- agent profile
- recommendation engine
- dismiss feedback loop
- recommendation cards

### Phase 4: Production Polish

- testing
- observability
- accessibility
- mobile polish
- deployment
- error handling

---

## 15. Out of Scope

For the current build:

- native mobile apps
- live plant.id production integration
- payments
- subscriptions
- IoT sensors
- public social network
- direct messaging
- exposing user email or phone by default

---

## 16. Resume Positioning

### Project title

**Flourish — AI-Powered Plant Care Agent**

### Short resume description

> Built a full-stack AI plant care platform with personalized scheduling, proactive health insights, real-time notifications, and agentic AI recommendations using React, FastAPI, Firebase, Firestore, Groq, and external tool integrations.

---

## 17. Definition of Done

Flourish is portfolio-ready when:

- users can sign in and complete onboarding
- users can add plants manually or via AI lookup
- plants have adaptive care schedules
- users can complete tasks and earn points
- notifications update in real time
- PlantMind answers using user context and tools
- recommendations are personalized and dismissible
- leaderboard is privacy-safe
- app works on mobile and desktop
- core flows are tested
- backend is deployed and observable
- external service failures degrade gracefully