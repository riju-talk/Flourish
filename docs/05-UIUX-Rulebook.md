Flourish: Design System & UX Rulebook v3.0
A production-grade design system for the "Botanical Journal" experience.
Version: 3.0 · Last updated: 2026-08-05

> **v3.0 supersedes "Cosmic Garden" (v2.0).** The glassmorphism/emerald-gradient
> look is gone, replaced by something warmer and more editorial: cream backgrounds,
> a deep forest-green primary, a serif display face paired with a clean sans for UI,
> and flat, solid cards instead of blurred glass. Navigation is now a **single top
> navbar everywhere**, with no sidebar anywhere in the app, on any page. Section
> numbers below are unchanged from v2.0 where the underlying pattern (spacing, motion,
> accessibility, page templates) still applies. Only the color, typography, and
> surface tokens, along with the navigation pattern, actually changed.
Table of Contents
Design Identity
Design Tokens
Typography System
Elevation & Shadows
Spacing Scale
Animation & Motion
Layout Patterns
Component Specifications
Page Templates
Empty & Error States
Form UX Patterns
Feedback & Notifications
Accessibility (A11y)
Responsive Behavior
Brand Voice & Microcopy
UX Rules
1. Design Identity ("Botanical Journal")
Flourish reads like a premium field journal for plant people: warm cream paper, deep
forest-green ink, an elegant serif for headlines, and generous whitespace. It's
confident and editorial, never glassy or "techy."
Core Principles
Table
Principle	Description
Warm	Cream backgrounds, deep forest-green accents, and friendly microcopy replace cold clinical interfaces.
Editorial	A serif display face for headings gives the app a considered, journal-like feel, never a gimmick font.
Calm & flat	Solid cards with soft shadows, not blur/glass. No jarring transitions, no harsh reds. Errors are handled gracefully.
Uncluttered	One navigation surface (the top navbar) on every page, with no sidebar and no competing nav patterns.
Brand Personality
Voice: Your knowledgeable, encouraging gardening friend, not a botanist professor.
Tone: Warm, playful, confident. Never apologetic for being helpful.
Metaphors: Growth, seasons, nurturing, blooming, roots, sunlight.
2. Design Tokens
Theme Architecture
Light & dark modes via next-themes, darkMode: "class".
All colors are CSS variables (hsl(var(--token))) defined in src/index.css and mapped in tailwind.config.ts.
Never hardcode raw colors in components. Always use semantic tokens.
Color Palette
Light Mode (:root)
Table
Token	HSL Value	Usage
--background	40 30% 96%	App canvas, warm cream
--foreground	155 35% 12%	Primary text, deep forest green-black
--card	40 35% 99%	Elevated surfaces (near-white warm)
--popover	40 35% 99%	Dropdowns, tooltips, menus
--primary	155 45% 18%	Deep forest green for CTAs, focus, active states, and logo
--primary-foreground	40 30% 98%	Cream/white text on primary
--secondary	140 20% 92%	Soft sage/mint surfaces, secondary buttons
--muted	35 15% 93%	Subtle backgrounds, disabled states
--accent	145 30% 90%	Hover/emphasis tint, selected rows
--destructive	0 72% 51%	Errors, destructive actions
--destructive-foreground	40 30% 98%	Text on destructive backgrounds
--border	35 15% 87%	Dividers, input borders
--input	35 15% 87%	Form field borders
--ring	155 45% 18%	Focus rings, selected indicators
--radius	1rem	Global corner radius (16px)
Dark Mode (.dark)
Table
Token	HSL Value	Usage
--background	155 25% 8%	Deep charcoal-forest canvas
--foreground	40 20% 95%	Warm near-white text
--card	155 20% 11%	Elevated dark surfaces
--popover	155 20% 11%	Dark dropdowns, menus
--primary	140 40% 55%	Brighter sage-green for dark contrast
--primary-foreground	155 30% 10%	Dark text on primary
--secondary	155 15% 16%	Muted dark surfaces
--muted	155 15% 16%	Subtle dark backgrounds
--accent	140 25% 18%	Green-tinted dark accent
--destructive	0 62% 50%	Softer red for dark mode
--destructive-foreground	40 20% 95%	Text on destructive
--border	155 15% 18%	Dark dividers
--input	155 15% 18%	Dark form borders
--ring	140 40% 55%	Bright sage-green focus ring
Brand Palette (Extended)
plain
colors.flourish = {
  cream:   '#F5F1E8',  // Warm neutrals, backgrounds
  sage:    '#A3B18A',  // Secondary accents, icons
  green:   '#4A7856',  // Primary brand green
  dark:    '#1F3B2C',  // Deep green text, headers
  forest:  '#16261E',  // Darkest green, borders
}
Semantic Status Colors
Table
Status	Light	Dark	Usage
Success	hsl(142 76% 36%)	hsl(142 70% 45%)	Growth, completion, healthy plants
Warning	hsl(38 92% 50%)	hsl(38 90% 55%)	Needs attention, upcoming tasks
Info	hsl(200 90% 45%)	hsl(200 85% 55%)	Tips, educational content
Error	hsl(0 72% 51%)	hsl(0 62% 50%)	Failures, destructive actions
Card Surface Tokens (formerly "Glassmorphism")
Cards are now flat and solid, with no backdrop blur. The token names kept the `--glass-*`
prefix so existing `.glass-card` markup across the app didn't need to change, but the
values now describe a plain card with a soft shadow:
css
--glass-bg:        hsl(var(--card));
--glass-border:    hsl(var(--border));
--glass-blur:      0px;
--glass-shadow:    0 1px 2px hsl(30 20% 20% / 0.04), 0 8px 24px hsl(30 20% 20% / 0.06);
3. Typography System
Font Family
Display/headings: **Fraunces** (Google Fonts, `font-serif`), a warm, editorial serif
used for the wordmark, page titles, and section headings. This is the single biggest
visual signal of the new identity, so don't fall back to the sans for anything that reads
as a "headline."
Body/UI: **Outfit** (Google Fonts, default `font-sans`), geometric, friendly, and modern.
Used for body copy, nav links, buttons, form inputs, everything that isn't a headline.
Monospace: JetBrains Mono (for data, timestamps, debug info only).
Type Scale
Table
Token	Size	Weight	Line Height	Letter Spacing	Usage
display	3rem (48px)	800	1.1	-0.02em	Hero headlines, onboarding
h1	2.25rem (36px)	800	1.15	-0.02em	Page titles
h2	1.5rem (24px)	700	1.25	-0.01em	Section headers
h3	1.25rem (20px)	600	1.35	0	Card titles, modal headers
h4	1rem (16px)	600	1.4	0	Subsection labels
body	1rem (16px)	400	1.6	0	Primary body text
body-sm	0.875rem (14px)	400	1.5	0	Secondary text, descriptions
caption	0.75rem (12px)	500	1.4	0.01em	Labels, metadata, timestamps
overline	0.6875rem (11px)	600	1.2	0.08em	ALL CAPS section labels
Text Color Hierarchy
Primary text: text-foreground, for names, headings, key data.
Secondary text: text-muted-foreground, for descriptions, hints, timestamps.
Tertiary text: text-muted-foreground/60, for metadata, disabled hints.
Emphasis: text-primary, for links, active states, scores.
Gradient accent: .text-gradient for hero headlines only.
4. Elevation & Shadows
Shadow Scale
Table
Token	Value	Usage
shadow-sm	0 1px 2px hsl(145 60% 10% / 0.05)	Inline inputs, small badges
shadow-md	0 4px 12px hsl(145 60% 10% / 0.08)	Cards, buttons at rest
shadow-lg	0 8px 24px hsl(145 60% 10% / 0.12)	Modals, dropdowns, elevated cards
shadow-xl	0 16px 48px hsl(145 60% 10% / 0.16)	Full-screen overlays, onboarding
shadow-glow	0 0 24px hsl(150 100% 35% / 0.25)	Primary CTA hover, active states
shadow-glow-dark	0 0 32px hsl(150 80% 50% / 0.35)	Dark mode glow accents
Z-Index Scale
Table
Layer	Z-Index	Elements
Base	0	Page content
Sticky	10	Sticky headers, navbars
Dropdown	50	Select menus, autocomplete
Overlay	100	Backdrops, dimmers
Modal	200	Dialogs, drawers
Toast	300	Notifications, toasts
Tooltip	400	Tooltips, popovers
Loader	500	Full-screen loaders
5. Spacing Scale
Based on 0.25rem (4px) increments. Use these consistently, not arbitrary values.
Table
Token	Value	Usage
space-1	0.25rem (4px)	Icon gaps, inline spacing
space-2	0.5rem (8px)	Tight padding, badge gaps
space-3	0.75rem (12px)	Button internal padding (vertical)
space-4	1rem (16px)	Card internal padding, section gaps
space-5	1.25rem (20px)	Modal padding
space-6	1.5rem (24px)	Section margins
space-8	2rem (32px)	Card gaps in grids
space-10	2.5rem (40px)	Page section spacing
space-12	3rem (48px)	Large section breaks
space-16	4rem (64px)	Hero spacing, onboarding gaps
Layout Grid
Container: max-w-7xl mx-auto px-4 sm:px-6 lg:px-8
Content max-width: 640px for forms, 960px for dashboards, 1200px for marketing.
Grid gap: space-6 (24px) default, space-4 on mobile.
6. Animation & Motion
Philosophy
Motion should feel like a gentle breeze, noticeable but never distracting. Every animation has to serve a purpose: orientation, feedback, or delight.
Timing Tokens
Table
Token	Duration	Usage
duration-instant	100ms	Hover color changes, opacity shifts
duration-fast	200ms	Button presses, toggles, small UI feedback
duration-normal	300ms	Card transitions, modal open/close
duration-slow	500ms	Page transitions, large element entrances
duration-ambient	3000-6000ms	Floating, pulsing, breathing animations
Easing Tokens
Table
Token	Value	Usage
ease-default	cubic-bezier(0.4, 0, 0.2, 1)	Standard transitions
ease-enter	cubic-bezier(0, 0, 0.2, 1)	Elements entering the viewport
ease-exit	cubic-bezier(0.4, 0, 1, 1)	Elements leaving the viewport
ease-bounce	cubic-bezier(0.34, 1.56, 0.64, 1)	Playful micro-interactions
ease-spring	cubic-bezier(0.175, 0.885, 0.32, 1.275)	Buttons, toggles, switches
Reusable Animations
css
/* Ambient float — cards, decorative elements */
.animate-float {
  animation: float 6s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

/* Gentle pulse — status indicators, live data */
.leaf-pulse {
  animation: leafPulse 3s ease-in-out infinite;
}
@keyframes leafPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.05); }
}

/* Staggered entrance — lists, grids */
.stagger-in > * {
  animation: fadeSlideUp 0.4s ease-out both;
}
.stagger-in > *:nth-child(1) { animation-delay: 0ms; }
.stagger-in > *:nth-child(2) { animation-delay: 80ms; }
.stagger-in > *:nth-child(3) { animation-delay: 160ms; }
.stagger-in > *:nth-child(4) { animation-delay: 240ms; }
/* Continue pattern or use JS for dynamic lists */

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Hover lift — interactive cards */
.hover-lift {
  transition: transform 0.3s ease-spring, box-shadow 0.3s ease-default;
}
.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

/* Shimmer loading — skeletons */
.shimmer {
  background: linear-gradient(
    90deg,
    hsl(var(--muted)) 25%,
    hsl(var(--muted) / 0.5) 50%,
    hsl(var(--muted)) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
Motion Rules
Respect prefers-reduced-motion: All animations must have @media (prefers-reduced-motion: reduce) fallbacks that snap instantly.
Never animate layout properties (width, height, top, left). Use transform and opacity only, for 60fps performance.
Loading states: Always show a branded loader or skeleton. Never leave blank space.
Page transitions: Use AnimatePresence with a gentle fade + 8px slide. Duration: 300ms.
7. Layout Patterns
App Shell
plain
┌─────────────────────────────────────┐
│  Navbar (sticky, glass, z-10)       │  64px height
├─────────────────────────────────────┤
│                                     │
│  Main Content                       │  flex-1, scrollable
│  (container mx-auto px-4)           │
│                                     │
├─────────────────────────────────────┤
│  Bottom Nav (mobile only)           │  64px height
└─────────────────────────────────────┘
Dashboard Layout (Desktop)
plain
┌──────────────────────────────────────────────────────────┐
│  Page Header (greeting + date + action)                  │
├──────────────────────────────┬───────────────────────────┤
│                              │                           │
│  Main Content (col-span-8)   │  Sidebar (col-span-4)     │
│  - Plant grid                │  - Daily checklist        │
│  - Activity feed             │  - Weather widget         │
│  - Recommendations           │  - Leaderboard preview    │
│                              │  - Quick stats            │
│                              │                           │
└──────────────────────────────┴───────────────────────────┘
Card Grid Responsive
plain
Mobile:  grid-cols-1  gap-4
Tablet:  grid-cols-2  gap-6
Desktop: grid-cols-3  gap-6
Large:   grid-cols-4  gap-8
8. Component Specifications
8.1 Glass Card (.glass-card)
The foundational surface of Flourish.
css
.glass-card {
  background: var(--glass-bg);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--glass-border);
  border-radius: var(--radius);        /* 1.25rem = 20px */
  box-shadow: var(--glass-shadow), var(--glass-highlight);
  transition: transform 0.3s ease-spring, box-shadow 0.3s ease-default;
}
Anatomy:
Padding: space-5 (20px) default, space-6 (24px) for feature cards.
No internal borders; use space-4 gaps and dividers instead.
Header (optional): flex row, justify-between, items-center, bottom margin space-4.
Footer (optional): flex row, justify-end, top margin space-4, top border border-border.
8.2 Primary Button
plain
Background:    vibrant-gradient (green-500 → emerald-700)
Text:          white, font-semibold, tracking-tight
Padding:       space-3 vertical, space-5 horizontal
Border-radius: full (pill shape)
Shadow:        shadow-md at rest, shadow-glow on hover
Transform:     scale(1.02) on hover, scale(0.98) on active
Icon:          lucide icon, size 18px, margin-right space-2
States:
Table
State	Style
Default	Gradient bg, white text, shadow-md
Hover	Brighter gradient, shadow-glow, translateY(-1px)
Active	scale(0.98), shadow-sm
Loading	Spinner replaces icon, disabled cursor, reduced opacity
Disabled	Muted bg, muted text, no shadow, cursor-not-allowed
8.3 Secondary Button
plain
Background:    hsl(var(--secondary))
Text:          hsl(var(--foreground)), font-medium
Border:        1px solid hsl(var(--border))
Border-radius: full
Padding:       space-3 vertical, space-4 horizontal
8.4 Input Fields
plain
Background:    hsl(var(--background))
Border:        1px solid hsl(var(--input))
Border-radius: 0.75rem (12px), slightly tighter than cards
Padding:       space-3 vertical, space-4 horizontal
Focus:         ring-2 ring-primary ring-offset-2 ring-offset-background
Placeholder:   text-muted-foreground/50
Error:         border-destructive, text-destructive, shake animation (200ms)
8.5 Plant Card
plain
┌─────────────────────────────┐
│  [Image] 16:10 aspect       │  rounded-t-3xl, object-cover
│  Water badge (absolute)     │  top-3 right-3, glass pill
├─────────────────────────────┤
│  🌿 Plant Name              │  h3, font-semibold
│  Scientific name            │  caption, italic, muted
│  ─────────────────────────  │  divider
│  🌤️  Sun  💧 Water  🌡️ Temp │  icon row, body-sm, muted
│  [Care for Plant]           │  primary button, full width
└─────────────────────────────┘
Specs:
Aspect ratio: aspect-[4/5] on mobile, aspect-[3/4] on desktop.
Image: rounded-t-3xl, object-cover, lazy-loaded.
Status badge: Absolute positioned, glass-card pill, px-3 py-1, text-xs font-medium.
Hover: .hover-lift, translateY(-4px) + enhanced shadow.
8.6 Recommendation Card
plain
┌─────────────────────────────────────┐
│  [Plant Image]  1:1 square          │
├─────────────────────────────────────┤
│  🌿 Plant Name          [× dismiss] │
│  "Perfect for your sunny balcony"   │  body-sm, muted
│  [🔗 sourced]                       │  caption, link icon
│  [Add to My Garden]                 │  primary button
└─────────────────────────────────────┘
Dismiss: × icon button, top-right of card, ghost variant, hover:bg-destructive/10.
Sourced affordance: Small Link lucide icon + "Sourced" caption, opens Tavily reference in new tab.
8.7 Leaderboard Row
plain
┌────────────────────────────────────────────────────────────┐
│  #1  [Avatar]  Alex Johnson          1,240 pts    🏆      │
│      📧 alex@email.com  📱 +1 555-0123                     │
└────────────────────────────────────────────────────────────┘
Specs:
Rank: w-8 text-center font-bold text-primary for top 3, text-muted-foreground for others.
Avatar: w-10 h-10 rounded-full.
Name: font-semibold text-foreground.
Score: font-bold text-primary text-lg, right-aligned.
Contact: text-muted-foreground text-xs, Mail + Phone icons (14px), below name.
Top 3: Gold/Silver/Bronze subtle left border or background tint.
8.8 Daily Checklist Item
plain
┌─────────────────────────────────────┐
│  [✓] Water Monstera                 │  Checkbox + task
│  Every 3 days · Due today           │  caption, muted
│  [Mark Done]                        │  small secondary button
└─────────────────────────────────────┘
States:
Pending: Normal opacity, checkbox empty.
Completed: Strikethrough text, muted color, checkbox checked with primary fill.
Overdue: Left border border-destructive, text text-destructive, overdue badge.
8.9 Navbar
plain
┌────────────────────────────────────────────────────────────┐
│  🌿 Flourish          [Garden] [Leaderboard] [PlantMind] [Profile]  │
└────────────────────────────────────────────────────────────┘
Mobile: Hamburger menu → sheet drawer from right.
Active link: text-primary + subtle underline animation.
Scroll behavior: Transparent at top, glass-card background + shadow-sm after 20px scroll.
8.10 Toast Notifications (Sonner)
plain
┌─────────────────────────────────────┐
│  ✅  Plant added successfully!        │
│     Monstera is now in your garden.   │
└─────────────────────────────────────┘
Specs:
Position: Bottom-right desktop, bottom-center mobile.
Duration: 4000ms default, 6000ms for action-required toasts.
Types: Success (green left border), Error (red left border), Info (blue left border).
Action buttons: Small secondary button inside toast for undo/primary action.
9. Page Templates
9.1 Auth Page (/auth)
Layout: Centered single column, max-width 420px, vertically centered.
Background: Full-bleed mesh gradient (fixed), animated ambient orbs.
Card: Glass card, space-8 padding, shadow-xl.
Header: App logo + "Welcome back, gardener" (display-sm, text-gradient).
Form: Email + password inputs, primary CTA "Sign In", divider "or", OAuth buttons.
Footer: "Don't have an account? Sign up" as a muted link.
9.2 Onboarding Page (/onboarding)
Gate: Redirect here immediately after first sign-in if no profile exists. No skip.
Layout: Centered, max-width 480px, generous vertical padding (space-16).
Card: Glass card, space-8 padding, shadow-xl.
Header: "Let's get you growing" + subtitle "Tell us a bit about yourself."
Form: Full name + phone number inputs, primary CTA "Start My Garden".
Loading: Branded "Flourishing..." loader while profile creates, then redirect to /garden.
Progress: Single step, no stepper UI needed. Keep it focused.
9.3 Garden Dashboard (/garden)
Header: Personalized greeting ("Good morning, Alex!"), date, weather widget.
Main (8 cols):
Plant grid: 3 columns desktop, responsive.
"Add Plant" floating action button (FAB): primary, bottom-right, shadow-glow.
Sidebar (4 cols):
Daily checklist (collapsible).
Quick stats (streak, total plants, health score).
Leaderboard preview (top 3 + "View All" link).
PlantMind quick chat button.
9.4 Plant Detail Page (/garden/[id])
Hero: Large plant image (40vh), gradient overlay, plant name + scientific name.
Stats row: Sun, water, temperature, humidity, as icon + value cards in a row.
Care log: Timeline of past care actions, add new action FAB.
Notes: Editable notes section, auto-save.
Delete: Destructive button at bottom, requires confirmation modal.
9.5 Leaderboard Page (/leaderboard)
Header: "Community Garden" + subtitle + your rank badge.
Filters: Time range (Week / Month / All Time), search input.
Table/Grid: Ranked rows with avatar, name, score, contact info.
Your row: Sticky at bottom if not in view, highlighted with accent background.
Empty: "Be the first to bloom!" illustration + CTA.
9.6 PlantMind Chat (/plantmind)
Layout: Full-height chat interface, message bubbles.
User bubbles: Primary bg, right-aligned, rounded-2xl.
AI bubbles: Card bg, left-aligned, rounded-2xl.
Input: Sticky bottom, glass input bar with send button.
Follow-up chips: Below each AI response, 2-4 pill buttons, secondary style.
Typing indicator: Animated dots, "PlantMind is thinking..."
10. Empty & Error States
Empty State Pattern
Every empty state must include:
Illustration/Icon: lucide-react icon at 48px, muted color, or a custom SVG illustration.
Headline: h3, friendly, never "No data found."
Description: body-sm, text-muted-foreground, explains what will appear here.
CTA: Primary or secondary button to take the user forward.
Examples:
Table
Context	Headline	Description	CTA
Empty garden	"Your garden is waiting"	"Add your first plant and start tracking its growth."	"Add My First Plant"
Empty checklist	"All caught up!"	"Your plants are happy. Check back tomorrow."	"Browse Plants"
Empty leaderboard	"Be the first to bloom!"	"Complete care tasks to earn points and top the chart."	"Start Caring"
No recommendations	"We're still learning about your garden"	"Add more plants to get personalized suggestions."	"Add a Plant"
No search results	"No plants match your search"	"Try a different name or browse our plant library."	"Browse All"
Error State Pattern
Icon: AlertTriangle or WifiOff, text-destructive, 48px.
Headline: Clear, non-technical. Never "Error 500."
Description: What happened + what to do.
Actions: Retry button (primary) + contact support link (secondary).
Examples:
Table
Error	Headline	Description	Action
Network	"Connection lost"	"Check your internet and try again."	"Retry"
Server	"Something went wrong"	"Our servers are having a moment. We're on it."	"Retry"
Auth	"Session expired"	"Please sign in again to continue."	"Sign In"
Not found	"Page not found"	"This page may have moved or doesn't exist."	"Go Home"
Loading States
Page load: Branded "Flourishing..." loader with animated leaf icon, centered, full-screen.
Section load: Skeleton screens matching the final layout shape. Never generic spinners.
Button load: Spinner replaces icon/text, button remains same size to prevent layout shift.
Image load: Blur-up placeholder or dominant color placeholder.
11. Form UX Patterns
Input Validation
Real-time: Validate on blur, not on every keystroke.
Inline errors: Below input, text-destructive text-sm, with AlertCircle icon.
Success indicators: Green checkmark on valid fields (optional, for long forms).
Shake animation: Brief translateX shake on submit with errors.
Form Layout
Single column for mobile and most desktop forms.
Two columns only for closely related pairs (First/Last name, City/State).
Submit button: Full width on mobile, auto-width on desktop, always at bottom.
Cancel: Ghost button left of submit, or text link above.
Confirmation Patterns
Destructive actions: Modal confirmation with red CTA. "Delete Monstera? This cannot be undone."
Settings changes: Auto-save with toast confirmation. No "Save" button for toggles.
Bulk actions: Checkbox selection + floating action bar at bottom.
12. Feedback & Notifications
Toast Types
Table
Type	Icon	Color	Duration	Usage
Success	CheckCircle2	Green left border	3s	Actions completed
Error	XCircle	Red left border	5s	Failures, need attention
Warning	AlertTriangle	Amber left border	4s	Attention needed
Info	Info	Blue left border	3s	Tips, updates
Inline Feedback
Optimistic UI: Update UI immediately on action, roll back on error.
Skeletons: Match final layout dimensions exactly. Use shimmer animation.
Progress indicators: For multi-step actions (image upload, AI generation), use a progress bar or stepper.
Haptic & Sound (Mobile)
Success: Light haptic feedback on task completion.
Error: Medium haptic on validation failure.
No sound by default, out of respect for quiet environments.
13. Accessibility (A11y)
WCAG Compliance Target: AA
Color & Contrast
Normal text: Minimum 4.5:1 contrast ratio.
Large text (18px+ bold, 24px+ normal): Minimum 3:1.
UI components: Minimum 3:1 against adjacent colors.
Never rely on color alone to convey information. Always pair with icons or text.
Focus Management
Visible focus rings: ring-2 ring-primary ring-offset-2 on all interactive elements.
Focus trapping: Modal dialogs trap focus within the modal while open.
Return focus: On modal close, return focus to the element that triggered it.
Skip links: Provide "Skip to main content" link for keyboard users.
Screen Readers
Landmarks: Use <main>, <nav>, <aside>, <header>, <footer>.
Headings: Logical hierarchy; never skip levels (h1 → h3).
Images: All informative images have alt text. Decorative images have alt="".
Icons: All lucide-react icons in buttons must have aria-label or aria-hidden.
Live regions: Use aria-live="polite" for toast announcements, dynamic score updates.
Form labels: Every input has an associated <label>. Use aria-describedby for error messages.
Motion
Respect prefers-reduced-motion: Disable ambient animations, instant transitions.
No auto-playing video/audio without user control.
Touch Targets
Minimum: 44×44px for all interactive elements.
Recommended: 48×48px for primary actions.
Spacing: Minimum 8px between adjacent touch targets.
14. Responsive Behavior
Breakpoints
Table
Name	Width	Key Changes
sm	640px	2-column grids, side margins increase
md	768px	Content aside/sidebar columns appear, navbar nav links expand from hidden
lg	1024px	3-column grids, dashboard 8/4 split
xl	1280px	4-column grids, max container width
2xl	1536px	Extra padding, larger typography
Mobile-First Patterns
Navigation: Bottom tab bar (iOS style) or hamburger sheet.
Cards: Full width, single column, larger touch targets.
Modals: Full-screen sheets sliding up from bottom.
Tables: Convert to card lists on mobile.
FAB: Primary action as floating button, bottom-right, 56px, shadow-glow.
Tablet Adaptations
Dashboard: 2-column main + sidebar becomes bottom sheet or collapsible.
Forms: Two-column layout for related fields.
Images: Larger aspect ratios, more generous spacing.
15. Brand Voice & Microcopy
Voice Characteristics
Table
Trait	Do	Don't
Warm	"Your Monstera is thriving!"	"Plant status: optimal."
Encouraging	"Keep your streak alive!"	"You have not missed any days."
Playful	"Time to quench that thirst!"	"Watering is required."
Confident	"We'll remind you when it's time."	"You may possibly receive a reminder."
Personal	"Your garden is looking lush."	"The user has 5 plants."
Contextual Microcopy
Onboarding:
"Let's get you growing"
"Tell us a bit about yourself"
"Start My Garden"
Empty States:
"Your garden is waiting"
"All caught up!"
"Be the first to bloom!"
Success:
"Plant added! 🌱"
"Care logged. Great job!"
"Streak extended! 🔥"
AI / PlantMind:
"PlantMind is thinking..."
"Botanist Wisdom"
"Here's what I'd recommend..."
Loading:
"Flourishing..."
"Watering the servers..."
"Growing your recommendations..."
Errors (friendly):
"Oops, something didn't sprout."
"Our servers are having a moment."
"Couldn't connect to the greenhouse."
16. UX Rules
16.1 Authentication & Routing
Protected routes: Every page except /auth requires sign-in.
Auth loader: Show the branded "Flourishing..." loader while auth state resolves. Never show a blank page or flash of unauthenticated content.
Onboarding gate: After a brand-new sign-in (no profile exists), redirect to /onboarding before any other page. No skip/dismiss path.
Onboarding loading: Use the same branded loader while the profile is being created, then redirect to /garden.
Returning users: Never see onboarding. Land directly on /garden.
16.2 Data & Feedback
Optimistic UI: Update the interface immediately on user actions (add plant, mark done). Roll back with an error toast if the server fails.
React Query invalidation: Invalidate relevant queries after mutations. Stale data is a bug.
Skeleton loading: Use <Skeleton> components that match the final layout dimensions. Never use generic spinners for content areas.
Toasts on every action: success, error, or info. The user must always know their action registered.
Auto-save: Settings and notes auto-save. Show a subtle "Saved" indicator, not a blocking toast.
16.3 Layout & Visual
Consistent container: container mx-auto px-4 sm:px-6 lg:px-8 on all pages.
Section rhythm: Consistent vertical spacing, space-10 between major sections, space-6 within sections.
Responsive grids: grid-cols-1 → sm:grid-cols-2 → lg:grid-cols-3 for cards. Dashboard uses 12-col layout (8/4 split on desktop).
Glass cards as default: All content surfaces should use .glass-card or shadcn Card with glass overrides.
Gradient buttons for primary actions only. Secondary and tertiary actions use solid or ghost styles.
16.4 Motion & Interaction
Gentle entry animations: animate-in fade-in slide-in-from-bottom-4 for page content, duration-300.
Hover-lift on all cards: Interactive cards must have .hover-lift, translateY(-4px) + enhanced shadow.
Ambient motion in moderation: .animate-float for decorative elements, .leaf-pulse for status indicators. Never on primary content.
No layout shift: Buttons maintain size in loading state. Images have defined aspect ratios.
Reduced motion respect: All animations must have prefers-reduced-motion fallbacks.
16.5 AI & Recommendations
Follow-up chips: Every PlantMind response renders 2-4 tappable follow-up suggestion chips below the message, as small, secondary-styled pill buttons. Never more than one row on mobile.
Recommendation cards: Plant image/icon, name, short reasoning blurb (why it fits this user), "Add to my garden" primary CTA, subtle dismiss (×) action.
Sourced affordance: If Tavily sources were used, show a small link icon ("Sourced") rather than raw URLs in the card body. Click opens reference in new tab.
AI transparency: Always label AI-generated content. PlantMind messages should be clearly from the assistant.
16.6 Leaderboard & Social
Contact info display: Each leaderboard row shows email and phone as secondary, muted text beneath the name/score. Use small Mail / Phone lucide icons + text-muted-foreground. Keep name, avatar, and score visually dominant.
Rank styling: Top 3 get special treatment, a gold/silver/bronze tint or left border. Your own row is always highlighted.
Privacy: Contact info only visible to authenticated users. Never expose in public API responses without auth.
16.7 Forms & Input
Label every input: Never rely on placeholder text as the only label.
Error clarity: Error messages explain how to fix the issue, not just that it's wrong.
Destructive confirmations: Delete actions require a confirmation modal. The CTA is red and says the action ("Delete Monstera"), not generic "Yes."
16.8 Performance
Image optimization: Use Next.js <Image> with proper sizing, lazy loading below fold, blur placeholders.
Font loading: Preload Outfit weights 400, 500, 600, 700, 800. Use font-display: swap.
Code splitting: Lazy load heavy components (charts, image galleries, PlantMind chat).
Appendix A: CSS Utility Quick Reference
css
/* Glass surface */
.glass-card { /* see §8.1 */ }

/* Hover interaction */
.hover-lift { /* see §6 */ }

/* Gradient fills */
.vibrant-gradient {
  background: linear-gradient(135deg, hsl(142 71% 45%) 0%, hsl(160 84% 39%) 100%);
}
.text-gradient {
  background: linear-gradient(135deg, hsl(150 100% 35%) 0%, hsl(170 80% 40%) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Ambient animations */
.animate-float { /* see §6 */ }
.leaf-pulse { /* see §6 */ }

/* Mesh gradient background */
.bg-mesh {
  background-color: hsl(var(--background));
  background-image: 
    radial-gradient(at 40% 20%, hsl(150 40% 85% / 0.4) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsl(160 30% 80% / 0.3) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsl(140 35% 82% / 0.3) 0px, transparent 50%);
  background-attachment: fixed;
}
.dark .bg-mesh {
  background-image: 
    radial-gradient(at 40% 20%, hsl(150 60% 15% / 0.4) 0px, transparent 50%),
    radial-gradient(at 80% 0%, hsl(170 50% 12% / 0.3) 0px, transparent 50%),
    radial-gradient(at 0% 50%, hsl(140 45% 10% / 0.3) 0px, transparent 50%);
}
Appendix B: File Structure Convention
plain
src/
├── app/                    # Next.js App Router
│   ├── (auth)/
│   │   ├── auth/page.tsx
│   │   └── onboarding/page.tsx
│   ├── (dashboard)/
│   │   ├── garden/page.tsx
│   │   ├── garden/[id]/page.tsx
│   │   ├── leaderboard/page.tsx
│   │   ├── plantmind/page.tsx
│   │   └── layout.tsx      # Dashboard shell (single top Navbar only - no sidebar)
│   ├── layout.tsx          # Root layout (providers, fonts, theme)
│   └── globals.css         # CSS variables, utilities, animations
├── components/
│   ├── ui/                 # shadcn/ui primitives
│   ├── layout/             # Navbar, Footer, AppShell
│   ├── plants/             # PlantCard, PlantGrid, PlantDetail
│   ├── dashboard/          # DailyChecklist, StatsWidget, WeatherWidget
│   ├── leaderboard/        # LeaderboardRow, LeaderboardTable
│   ├── plantmind/          # ChatBubble, ChatInput, FollowUpChips
│   ├── onboarding/         # OnboardingForm
│   └── shared/             # GlassCard, BrandedLoader, EmptyState, ErrorState
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities, API clients, constants
├── types/                  # TypeScript definitions
└── public/                 # Static assets, illustrations
Related docs: 01-PRD.md · 02-Tech-Stack-Architecture.md · 03-Data-Schema.md · 04-Rules-of-Engagement.md · 06-Phase-Tracker.md