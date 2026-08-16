# Flourish Data Schema

> Persistence reference for Cloud Firestore.
> **Source of truth:** Cloud Firestore. The SQLAlchemy models in
> `apps/api/api/models/db_models.py` are legacy/orphaned and not used at runtime.
> **Last updated:** 2026-08-05

---

## Overview

- **Database:** Cloud Firestore (NoSQL, document store).
- **Access:** `apps/api/api/db/firestore.py` → `FirestoreDB` (lazy-initialized client).
- **IDs:** Firestore documents use auto-generated UUIDs (except `profiles`, keyed by the
  Firebase `uid`, and `mail`, keyed by an auto-ID the Trigger Email extension manages).
  Timestamps use `firestore.SERVER_TIMESTAMP`.
- **Field naming note:** `01-PRD.md` §7 shows illustrative, product-level JSON examples
  (e.g. `owner_id`, `nickname`, `type`, `light_level`). This document is the literal,
  implementation-accurate schema, and it keeps the field names the running code actually
  reads and writes (`user_id`, `name`, `plant_type`, `sunlight_requirement`, ...). When in
  doubt while developing, **this file wins**; treat the PRD's JSON as intent, not a
  literal contract.

### Collections
| Collection | Document ID | Owner key |
|---|---|---|
| `profiles` | Firebase `uid` | (self) |
| `plants` | UUID | `user_id` → profiles |
| `care_tasks` | UUID | `user_id` → profiles |
| `health_checks` | UUID | `plant_id` → plants |
| `notifications` | UUID | `user_id` → profiles |
| `recommendations` | UUID | `user_id` → profiles |
| `email_logs` | UUID | `user_id` → profiles |
| `mail` | auto-ID (Trigger Email extension) | `to` (email address, not a profile FK) |

---

## Collection: `profiles`  (document id = Firebase `uid`)
| Field | Type | Notes |
|---|---|---|
| email | string | required, unique, from Firebase Auth |
| full_name | string | **required**, collected at onboarding (first sign-in only) |
| phone_number | string | **required**, collected at onboarding (first sign-in only) |
| display_name | string | from Google profile; may differ from `full_name` |
| photo_url | string | |
| bio | string | optional, editable, shown only on an opted-in public profile |
| total_score | int | gamification |
| level | int | |
| tasks_completed | int | |
| streak_days | int | |
| last_activity | timestamp | |
| achievements | array | |
| privacy | object | see below (default: everything private) |
| notification_preferences | object | see below |
| agent_profile | object | maintained by GroqService for personalization context (see below) |
| created_at / updated_at | timestamp | server timestamps |

### `privacy` object (sub-field of `profiles`)
Governs what other authenticated users can see about you. **Privacy-safe by default is
the standing product decision** (see `01-PRD.md` §5.10 and
`04-Rules-of-Engagement.md`).

| Field | Type | Default | Notes |
|---|---|---|---|
| public_profile_enabled | bool | `false` | opt-in to a public garden profile page |
| show_email | bool | `false` | if true, `GET /api/leaderboard` includes this user's email for other users |
| show_phone | bool | `false` | if true, `GET /api/leaderboard` includes this user's phone for other users |

> `GET /api/leaderboard` **never** returns `email`/`phone_number` for a user whose
> corresponding flag is `false`. Those keys are omitted from that user's entry
> entirely (not returned as `null`), to avoid leaking presence-of-data. A user's own
> entry always includes their own full data regardless of their privacy flags.

### `notification_preferences` object (sub-field of `profiles`)
| Field | Type | Default | Notes |
|---|---|---|---|
| email_task_reminders | bool | `true` | |
| email_achievements | bool | `true` | |
| email_streak_risk | bool | `true` | |
| email_recommendations | bool | `false` | |

### `agent_profile` object (sub-field of `profiles`)
Maintained by `GroqService` after meaningful interactions (not recomputed from scratch
on every request), used to personalize chat and recommendations.

| Field | Type | Notes |
|---|---|---|
| summary | string | short rolling summary of the user's garden + care behavior |
| garden_composition | object | e.g. `{low_light_plants, pet_safe_plants, outdoor_plants}` counts |
| care_habits | object | e.g. `{watering_consistency, fertilizing_consistency, health_check_frequency}` |
| recommendation_preferences | object | `{avoided_plants: [], preferred_traits: []}`, grows from dismiss/accept feedback |
| updated_at | timestamp | |

---

## Collection: `plants`

Field set corresponds to the `Plant` Pydantic model (`apps/api/api/models/plant.py`),
persisted via `plant.dict()` on `POST /api/plants/`. Manual/autonomous creation writes
an overlapping but smaller set.

| Field | Type | Notes |
|---|---|---|
| id | string (uuid) | added by `create_plant` |
| user_id | string | FK → profiles |
| name | string | required (the user's nickname for the plant) |
| species | string | required (in `/autonomous`, holds scientific name) |
| scientific_name | string | |
| plant_type | string | `indoor` / `outdoor` / `both` |
| size | string | `small` / `medium` / `large` |
| toxicity | string | `non-toxic` / `mildly-toxic` / `toxic` / `highly-toxic` |
| location | string | e.g. `Living Room` |
| preferred_locations | array | |
| sunlight_requirement | string | |
| temperature_range | object | `{min, max}` °C |
| watering_frequency_days | int | default 7 |
| watering_amount | string | |
| soil_type | string | |
| humidity_preference | string | |
| fertilizer_type | string | |
| fertilizer_frequency_days | int | default 30 |
| fertilizer_season | string | |
| pesticide_needs | array | |
| common_pests | array | |
| health_status | string | **lowercase for dashboard:** `healthy` / `needs_attention` / `critical` |
| health_score | float | default 100.0 |
| last_watered / last_fertilized / last_health_check | timestamp | |
| next_watering | string/timestamp | written by `/autonomous` (may be `null`) |
| image_url | string | Unsplash-sourced (see `02-Tech-Stack-Architecture.md` §5); may be `null` |
| care_instructions | string **or** object | model default string; `/autonomous` stores the plant-info dict |
| fun_facts | array | |
| notes | string | |
| days_since_watering / days_since_fertilizing | int | |
| needs_watering / needs_fertilizing | bool | |
| created_at / updated_at | timestamp | |

> Health-status values are **case-sensitive**. The dashboard summary matches exactly
> `healthy`, `needs_attention`, and `critical` (`dashboard.py` lines 41-43).

---

## Collection: `care_tasks`

> ⚠️ **Field names differ from the legacy SQLAlchemy model.** The active code reads and
> writes **`due_date`** (not `scheduled_date`) and **`recurring_days`** (not
> `recurrence_days`). `due_date` is parsed from an ISO string at query time
> (`tasks.py`, `dashboard.py`).

| Field | Type | Notes |
|---|---|---|
| id | string (uuid) | |
| plant_id | string (nullable) | FK → plants |
| user_id | string | FK → profiles |
| task_type | string | watering / fertilizing / pruning / checking |
| title | string | required |
| description | text | |
| due_date | string (ISO datetime) | **required**, used by `/tasks/today` & dashboard |
| priority | string | `high` / `medium` / `low` |
| completed | bool | default false |
| completed_at | string (ISO datetime) | set by `/complete` |
| snoozed_until | string (ISO datetime) | nullable, set by task snooze |
| notes | text | |
| points | int | default 10 |
| recurring | bool | default false |
| recurring_days | int | interval (e.g. `7`) |
| created_at | timestamp | |

---

## Collection: `health_checks`
| Field | Type | Notes |
|---|---|---|
| id | string (uuid) | |
| plant_id | string | FK → plants |
| user_id | string | FK → profiles (added by route) |
| check_type | string | leaves / soil / growth / pests / general |
| status | string | excellent / good / fair / poor / critical |
| notes | text | |
| image_url | string | |
| symptoms | array<string> | |
| ai_summary | string | short, explainable reason the health score changed (see `01-PRD.md` §5.3) |
| checked_at | timestamp | |

---

## Collection: `notifications`

> ⚠️ The active code writes **`type`** (not `notification_type`). Notifications are
> created by `FirestoreDB.create_notification` with `{user_id, type, title, message,
> read}`.

| Field | Type | Notes |
|---|---|---|
| id | string (uuid) | |
| user_id | string | FK → profiles |
| title | string | required |
| message | text | required |
| type | string | `task_due` / `task_completed` / `achievement` / `streak_risk` / `recommendation_ready` / `health_score_change` / `analysis_complete` |
| read | bool | default false |
| action_url | string | declared in legacy model; not written by current code |
| created_at | timestamp | |

> For `type` in `{achievement, streak_risk, task_due, recommendation_ready}`, the
> backend also enqueues a mirrored document in `mail` **and** logs it to `email_logs`,
> but only if the user's `notification_preferences` for that category is `true` (see
> `profiles.notification_preferences` above).

---

## Collection: `recommendations`
Personalized suggestions generated by `GroqService` (see `01-PRD.md` §5.8), grounded by
`agent_profile`, Tavily web search, and current weather.

| Field | Type | Notes |
|---|---|---|
| id | string (uuid) | |
| user_id | string | FK → profiles |
| plant_name | string | |
| scientific_name | string | |
| image_url | string | Unsplash-sourced, same pipeline as `plants.image_url` |
| reasoning | text | why this plant fits *this* user's garden |
| difficulty | string | `easy` / `moderate` / `advanced` |
| warnings | array<string> | e.g. toxicity, invasive-species notes |
| sources | array<string> | URLs surfaced via Tavily, if any were used |
| status | string | `pending` / `accepted` / `dismissed` |
| created_at | timestamp | |
| dismissed_at | timestamp | nullable |

> On `accepted`, the backend creates a `plants` document from the recommendation (same
> path as manual/lookup creation) and marks `status: "accepted"` here for history. On
> `dismissed`, `profiles.agent_profile.recommendation_preferences.avoided_plants` is
> updated so the same plant isn't resurfaced.

---

## Collection: `email_logs`
Durable record of every email Flourish has sent or attempted to send, per user.
**Both** event-triggered (achievement unlocked, streak at risk) **and** scheduled
(daily/weekly digest) emails are logged here, independent of whatever the `mail`
collection's own extension-managed delivery status says.

| Field | Type | Notes |
|---|---|---|
| id | string (uuid) | |
| user_id | string | FK → profiles |
| type | string | matches the triggering `notifications.type`, or `digest` for scheduled summaries |
| subject | string | |
| trigger | string | `event` (fired by user/system action) or `scheduled` (cron/APScheduler job) |
| mail_ref | string | document ID of the corresponding `mail` collection entry |
| sent_at | timestamp | when the `mail` doc was enqueued (not confirmed delivery; the extension owns that) |

---

## Collection: `mail`
Firebase **Trigger Email** extension convention: the backend only ever writes to this
collection; the extension owns delivery and updates its own status fields on the
document after send. Every write here is paired with an `email_logs` entry.

| Field | Type | Notes |
|---|---|---|
| to | array<string> | recipient email address(es) |
| message.subject | string | |
| message.html / message.text | string | body |
| template | object | optional, if using the extension's template feature |

---

## Cloud Storage layout
```
users/{userId}/
  ├── plants/{plantId}/{timestamp}.jpg
  ├── documents/{timestamp}_{filename}
  └── profile/avatar.jpg
```

---

## Relationships (logical)
```
profiles 1──N plants 1──N care_tasks       (task_type: watering/fertilizing/pruning/checking)
profiles 1──N care_tasks                  (user-level tasks, plant_id nullable)
plants   1──N health_checks
profiles 1──N notifications
profiles 1──N recommendations
profiles 1──N email_logs
notifications ─▶ mail ─▶ email_logs        (mirrored for email-worthy, opted-in notification types)
```

## Indexing / queries
- `plants` queried by `user_id` (Firestore `where`).
- `care_tasks` queried by `user_id` (Firestore `where`); `completed` filtering and
  `due_date` "today" filtering are done **in Python** (`get_user_tasks`,
  `tasks.py`, `dashboard.py`).
- `notifications` queried by `user_id`, optionally `read == False`, ordered by
  `created_at` desc (Firestore `where` + `order_by` + `limit`).
- `health_checks` queried by `plant_id`, ordered by `checked_at` desc.
- `recommendations` queried by `user_id`, `status == "pending"`, ordered by
  `created_at` desc.
- `email_logs` queried by `user_id`, ordered by `sent_at` desc (support/debug use).
- `profiles` ordered by `total_score` desc for the leaderboard; `privacy.show_email` /
  `privacy.show_phone` are read per-row to decide what to include in the response.

> Composite indexes may be required in Firestore for combined filters (e.g.
> `user_id` + `read` ordering, `user_id` + `status`). Planned once the app is under
> real load, see `06-Phase-Tracker.md`.

---

> **Related docs:** `01-PRD.md` · `02-Tech-Stack-Architecture.md` ·
> `04-Rules-of-Engagement.md` · `05-UIUX-Rulebook.md` · `06-Phase-Tracker.md`
