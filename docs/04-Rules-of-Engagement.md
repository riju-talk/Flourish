# Flourish: Rules of Engagement

> Working conventions agreed for every change to the Flourish repository, followed by humans and AI agents alike.
> **Last updated:** 2026-08-05

---

## Preamble

These rules keep the codebase consistent, secure, and documented. Treat them as
binding unless an explicit task overrides them. When intent is ambiguous, **ask before
implementing.**

---

## 1. Read before you write
Understand the existing patterns in the file you are touching before editing. Mimic the
style, naming, and structure of neighboring code.

## 2. Never assume libraries
Confirm a dependency exists in `package.json` / `requirements.txt` before using it.
Follow existing conventions rather than introducing parallel patterns.

## 3. Firestore is the single source of truth
Do **not** use the SQLAlchemy models in `apps/api/api/models/db_models.py`. They are
legacy and orphaned. All persistence goes through `apps/api/api/db/firestore.py`
(`FirestoreDB`). Document your changes in `docs/03-Data-Schema.md`, using the field
names the code actually uses. `docs/03-Data-Schema.md` is the literal contract, even
where `01-PRD.md`'s illustrative JSON uses different naming.

## 4. Auth is mandatory
Every `/api/*` route (except `/api/auth`) must be guarded by
`Depends(verify_firebase_token)` and resolve the `user_id`. Enforce ownership checks on
all user-scoped resources (plants, tasks, notifications, recommendations).

## 5. Never commit secrets
Service-account JSON, Firebase keys, and API keys stay out of git and out of `.env`
commits. Use `.env.example` for documentation only. Review `git status`/`diff` before
any commit.
- A Firebase Admin service-account key currently lives untracked at the repo root for
  local development. It is covered by a glob in `.gitignore`
  (`*firebase-adminsdk*.json`). If the key is ever rotated or re-downloaded under a new
  filename, verify the glob still matches before assuming it's ignored; don't rely on
  an exact-filename entry.

## 6. No comments unless asked
Do not add explanatory comments to code; keep it self-documenting. This is an explicit repo rule.

## 7. Frontend talks to backend only via `integrations/api.ts`
Add API functions there and reuse the shared Axios instance (it injects the Firebase
token and redirects on 401). Do not hand-roll `fetch` calls in components.

## 8. Build on shadcn/ui primitives
Reuse components in `src/components/ui/` and existing feature components (`PlantCard`,
`Navbar`, `DailyChecklist`, ...) instead of duplicating behavior.

## 9. Do not touch generated/vendored directories
Never modify: `node_modules`, `dist`, `.venv`, `venv`, `__pycache__`, `.pytest_cache`.

## 10. Keep Markdown tidy
Only `README.md` (root) and files in `docs/` are Markdown in the repo. Keep the 6 core
docs accurate when you change the system (see Docs map below).

## 11. Groq is the sole LLM backend
Ollama has been retired. Do not reintroduce Ollama-specific code paths, config vars
(`OLLAMA_BASE_URL`, `OLLAMA_MODEL`), or a "local model fallback" without an explicit,
new decision from the user. There currently is none, by design. All chat, lookup,
document-analysis, and recommendation code goes through `GroqService`.

## 12. The leaderboard is privacy-safe by default
Every user's `email`, `phone_number`, and `full_name` are **private by default**.
`GET /api/leaderboard` shows `display_name`, avatar, score, level, streak, and badges
for everyone, and only includes a user's `email`/`phone_number` if that specific user
has opted in via `profiles.privacy.show_email` / `show_phone` (see
`03-Data-Schema.md`). **This supersedes an earlier, since-reversed decision to show
every user's contact info to everyone.** Don't resurrect the old behavior; if privacy
defaults need to change again, that's a product decision to raise with the user, not
infer from old context.

## 13. Automated (scheduled) emails must be logged, not just event emails
Any email Flourish sends, whether triggered by a user action or by the in-process
scheduler (`SchedulerService`), must write both a `mail` document (for the Trigger
Email extension to actually send) **and** an `email_logs` document recording that send
for that user (see `03-Data-Schema.md`). Never call `EmailService` in a way that skips
the `email_logs` write. Always check `profiles.notification_preferences` before
sending. A scheduled job must skip users who've opted out of that category.

## 14. Deployment configs are deliberate, not incidental
`vercel.json`, `render.yaml`, `firebase.json`/`.firebaserc`/`extensions/*.env`, and
`.github/workflows/keep-alive.yml` now exist and are live infrastructure. Don't modify
them as a side effect of unrelated work. Changing rootDir, env var names, the health
check path, or the extension config has real deploy consequences; treat those edits
with the same care as a schema change, and update the README's Deployment section if
behavior changes.

## 15. Verify before done
Run the relevant checks:
- Backend: `npm run test:api` (pytest)
- Frontend: `npm run test:web` (vitest), `npm run lint:web`, `npm run typecheck` (in `apps/web`)
- All: `npm test`

## 16. Commit discipline
Only commit when explicitly asked. Write concise messages matching repo style. Never
force-push or amend a failed commit. Do not enable/disable git hooks without permission.

## 17. When in doubt, ask
If scope, intent, or a decision is unclear, clarify before implementing. Prefer explicit
confirmation over assumptions for destructive, security-relevant, or privacy-relevant
changes.

---

## Quality bar

| Area | Standard |
|---|---|
| Backend logic | pytest suites in `apps/api/tests/` |
| Frontend logic | vitest + React Testing Library (`*.test.tsx` / `*.test.ts`) |
| Types | `tsc --noEmit` clean (`apps/web`) |
| Lint | `eslint .` clean (`apps/web`) |
| Docs | update the relevant `docs/*.md` |

## Basic workflow
1. Confirm the task & acceptance criteria.
2. Implement following the relevant `docs/` rules.
3. Run services (`npm run dev`) and verify behavior.
4. Run the quality checks above.
5. Update docs if the system surfaces changed.

---

## Docs map
| File | Covers |
|---|---|
| `README.md` | Project overview + quick start |
| `docs/01-PRD.md` | Product requirements, features, personas, metrics, roadmap |
| `docs/02-Tech-Stack-Architecture.md` | Stack, architecture, endpoints, config |
| `docs/03-Data-Schema.md` | Firestore collections & storage layout (literal, code-accurate) |
| `docs/04-Rules-of-Engagement.md` | Contribution conventions (this file) |
| `docs/05-UIUX-Rulebook.md` | Design system, themes, colors, UX rules |
| `docs/06-Phase-Tracker.md` | Phased execution plan & status |
