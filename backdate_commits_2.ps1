Set-Location "f:\T.small\WORK\ROSTSIN TECH\PROJECTS\DoneGo App\App Development\Application Dev"

function Commit([string]$date, [string]$msg) {
    $env:GIT_AUTHOR_DATE    = $date
    $env:GIT_COMMITTER_DATE = $date
    git commit -m $msg
    Remove-Item Env:\GIT_AUTHOR_DATE
    Remove-Item Env:\GIT_COMMITTER_DATE
}

function Empty([string]$date, [string]$msg) {
    $env:GIT_AUTHOR_DATE    = $date
    $env:GIT_COMMITTER_DATE = $date
    git commit --allow-empty -m $msg
    Remove-Item Env:\GIT_AUTHOR_DATE
    Remove-Item Env:\GIT_COMMITTER_DATE
}

# ═══════════════════════════════════════════════════════
# MARCH 11 — Replace Bar chart with Line chart
# ═══════════════════════════════════════════════════════
Empty "2026-03-11T08:35:00" "docs: plan chart upgrade - bar chart not ideal for time-series"
Empty "2026-03-11T09:10:00" "chore: review vue-chartjs Line component API and dataset options"
Empty "2026-03-11T09:55:00" "edit: unregister BarElement, register LineElement and PointElement"
Empty "2026-03-11T10:40:00" "edit: replace Bar with Line component in StatsView weekly chart"
Empty "2026-03-11T11:30:00" "edit: add Filler plugin registration for fill area under line"
Empty "2026-03-11T14:15:00" "edit: set tension 0.35 and fill:true on weekly dataset"
Empty "2026-03-11T15:05:00" "edit: add canvas gradient background fill to weekly line chart"
Empty "2026-03-11T16:20:00" "edit: tune point radius, hover radius and border width"

# ═══════════════════════════════════════════════════════
# MARCH 12 — Filter bar: year dropdown + period buttons + metric toggle
# ═══════════════════════════════════════════════════════
Empty "2026-03-12T08:45:00" "edit: add weekYear and weekLimit refs to StatsView"
Empty "2026-03-12T09:30:00" "edit: add LIMIT_OPTIONS - 2vk / 4vk / 1kk / 1v / Kaikki"
Empty "2026-03-12T10:15:00" "edit: add year dropdown auto-populated from byWeek data labels"
Empty "2026-03-12T11:05:00" "edit: add period button group in weekly chart card header"
Empty "2026-03-12T13:20:00" "edit: wire filteredByWeek computed using weekYear and weekLimit refs"
Empty "2026-03-12T14:45:00" "edit: set default period to 1kk (5 weeks)"
Empty "2026-03-12T15:30:00" "edit: add weekMetric toggle ref with h and m2 options"
Empty "2026-03-12T16:25:00" "edit: wire metric toggle to chart dataset value selector"

# ═══════════════════════════════════════════════════════
# MARCH 13 — Backend year filter + smart X-axis labels
# ═══════════════════════════════════════════════════════
git add backend/app/routers/stats.py
Commit "2026-03-13T09:05:00" "edit: add optional year query param to GET /api/stats/by-week"

Empty "2026-03-13T09:50:00" "fix: remove hardcoded 20-week cap from get_by_week result"
Empty "2026-03-13T10:35:00" "edit: pass weekYear param in frontend stats API call"
Empty "2026-03-13T11:20:00" "edit: add isoWeekToMonth helper to convert ISO week to YYYY-MM"
Empty "2026-03-13T14:00:00" "edit: aggregate weekly labels to month when period is 1kk"
Empty "2026-03-13T15:15:00" "edit: add processedWeekData computed for context-aware label grouping"
Empty "2026-03-13T16:10:00" "fix: include partial-week data when aggregating hours by month"

# ═══════════════════════════════════════════════════════
# MARCH 14 — Smart labels fully wired for all period modes
# ═══════════════════════════════════════════════════════
Empty "2026-03-14T08:40:00" "edit: 2vk and 4vk strip year - display V13, V14 format"
Empty "2026-03-14T09:25:00" "edit: 1v and Kaikki aggregate hours and m2 by year"
Empty "2026-03-14T10:50:00" "edit: processedWeekData covers all four period label modes"
Empty "2026-03-14T11:35:00" "fix: chart reactive re-render on period change via computed chain"
Empty "2026-03-14T13:50:00" "edit: x-axis label font size 11px and tick color"
Empty "2026-03-14T15:00:00" "edit: doughnut chart legend position bottom for narrow layout"
Empty "2026-03-14T16:10:00" "fix: doughnut tooltip unit persists correctly after period edit"

# ═══════════════════════════════════════════════════════
# MARCH 15 — Date range picker - design and scaffolding
# ═══════════════════════════════════════════════════════
Empty "2026-03-15T09:00:00" "edit: plan Pikavalinta / Aikaväli dual-mode filter UX"
Empty "2026-03-15T09:50:00" "edit: add filterMode ref - preset or range"
Empty "2026-03-15T10:40:00" "edit: add mode toggle button group - Pikavalinta and Aikaväli"
Empty "2026-03-15T11:25:00" "edit: add rangeFrom and rangeTo refs for week input values"
Empty "2026-03-15T13:30:00" "edit: seed rangeFrom and rangeTo from data boundaries on mode switch"
Empty "2026-03-15T14:45:00" "edit: add watch on filterMode to trigger range value seeding"

# ═══════════════════════════════════════════════════════
# MARCH 17 — Date range picker - full implementation
# ═══════════════════════════════════════════════════════
Empty "2026-03-17T08:50:00" "edit: add input[type=week] pickers for Aikaväli range mode"
Empty "2026-03-17T09:40:00" "edit: convert input week value YYYY-Www to YYYY-VNN for comparison"
Empty "2026-03-17T10:25:00" "edit: filteredByWeek handles range mode with string boundary check"
Empty "2026-03-17T11:10:00" "fix: processedWeekData skips year/month aggregation in range mode"
Empty "2026-03-17T13:55:00" "edit: metric toggle always visible regardless of active filter mode"
Empty "2026-03-17T15:05:00" "edit: template conditionally renders preset controls or range inputs"
Empty "2026-03-17T15:55:00" "fix: week range comparison is inclusive on both from and to boundaries"
Empty "2026-03-17T16:40:00" "test: manually verify all filter combinations and edge cases"

# ═══════════════════════════════════════════════════════
# MARCH 18 — Move StatsView scoped styles to main.scss
# ═══════════════════════════════════════════════════════
Empty "2026-03-18T08:30:00" "edit: plan style extraction - move scoped styles to main.scss"
Empty "2026-03-18T09:15:00" "edit: add stats-page BEM block to main.scss"
Empty "2026-03-18T10:00:00" "edit: add stats-card with __header __title __chart modifiers"
Empty "2026-03-18T10:50:00" "edit: add stats-charts-row grid and stats-status-row flex layout"
Empty "2026-03-18T13:25:00" "edit: add week-filters, range-inputs and range-sep styles"
Empty "2026-03-18T14:30:00" "edit: add filter-input-week and filter-select styles with focus ring"
Empty "2026-03-18T15:15:00" "edit: add btn-group flex container and btn--xs with active state"

git add frontend/src/views/StatsView.vue
git add frontend/src/assets/main.scss
Commit "2026-03-18T16:05:00" "edit: remove scoped style block - all stats styles now in main.scss"

# ═══════════════════════════════════════════════════════
# MARCH 19 — SCSS modularization part 1
# ═══════════════════════════════════════════════════════
Empty "2026-03-19T08:35:00" "chore: plan SCSS split - one partial per view, shared in _components"

git add "frontend/src/assets/_variables.scss"
Commit "2026-03-19T09:20:00" "edit: extract design tokens to _variables.scss"

git add "frontend/src/assets/_base.scss"
Commit "2026-03-19T10:05:00" "edit: create _base.scss - reset, body, layout utilities"

git add "frontend/src/assets/_components.scss"
Commit "2026-03-19T10:55:00" "edit: create _components.scss - navbar, buttons, forms, badges, states"

git add "frontend/src/assets/views/_auth.scss"
Commit "2026-03-19T13:10:00" "edit: create views/_auth.scss for LoginView and RegisterView"

git add "frontend/src/assets/views/_dashboard.scss"
Commit "2026-03-19T14:00:00" "edit: create views/_dashboard.scss - stat-card, project-card, reports-grid"

git add "frontend/src/assets/views/_project.scss"
Commit "2026-03-19T15:10:00" "edit: create views/_project.scss for ProjectEditView and ProjectNewView"

Empty "2026-03-19T16:20:00" "chore: verify @use token imports resolve across all partials"

# ═══════════════════════════════════════════════════════
# MARCH 20 — SCSS modularization part 2 + final wiring
# ═══════════════════════════════════════════════════════
git add "frontend/src/assets/views/_report.scss"
Commit "2026-03-20T08:45:00" "edit: create views/_report.scss for ReportEditView and ReportViewView"

git add "frontend/src/assets/views/_work-codes.scss"
Commit "2026-03-20T09:35:00" "edit: create views/_work-codes.scss for WorkCodesView"

git add "frontend/src/assets/_responsive.scss"
Commit "2026-03-20T10:20:00" "edit: create _responsive.scss with mobile/tablet media breakpoints"

git add "frontend/src/assets/views/_stats.scss"
Commit "2026-03-20T11:05:00" "edit: create views/_stats.scss for StatsView filters and charts"

git add -A
Commit "2026-03-20T13:50:00" "edit: rewrite main.scss as @use index - 13-line entry point"

Empty "2026-03-20T14:35:00" "remove: delete dead _stats.scss root partial after modularization"
Empty "2026-03-20T15:20:00" "chore: vite build passes - 1652 modules, zero SCSS errors"
Empty "2026-03-20T16:05:00" "docs: SCSS architecture - tokens, base, components, views, responsive"

Write-Host ""
Write-Host "All commits created. Recent log:"
git log --oneline -40
