# Development workflow (solo agile)

How FabPilot is built, end to end. Written to be reused for future products.

## 1. The loop

```
 Vision ─► Backlog ─► Iteration plan ─► Branch ─► Code + tests ─► PR ─► CI ─► Merge ─► Release ─► Review
   ▲                                                                                              │
   └──────────────────────────────── learnings, new stories ◄─────────────────────────────────────┘
```

| Step | Artifact | Rule |
|---|---|---|
| Vision | README "what & why", [roadmap](../roadmap.md) | Changes rarely. Every story must serve it. |
| Backlog | GitHub Issues (user stories), [backlog.md](../backlog.md) until Issues are set up | Ordered by value; top items are *ready*. |
| Iteration | GitHub Milestone, 1 week | Pick only what can be *done* this week. |
| Branch | `feat/<issue>-short-name`, `fix/...`, `docs/...`, `chore/...` | Short-lived (≤ 2–3 days); branch from `main`. |
| PR | PR template checklist | Even solo: review your own diff the next morning. |
| CI | `.github/workflows/ci.yml` | Red CI never merges. |
| Merge | Squash merge into `main` | `main` is always releasable. |
| Release | Git tag `vMAJOR.MINOR.PATCH`, [CHANGELOG](../../CHANGELOG.md) | One minor release per roadmap phase. |
| Review | 15-min retro note at the end of each iteration | What to keep / change next week. |

## 2. User stories

```
As a <role: process engineer / yield engineer / PIE / manager>,
I want <capability>,
so that <business value>.

Acceptance criteria (Given / When / Then):
- Given ..., when ..., then ...
```

Keep stories **vertical**: each one delivers something usable through all layers (API + UI +
test), not "build the DB layer".

Prioritise with **MoSCoW** (Must / Should / Could / Won't-now) and value vs. effort. Most
important first; iterate on the rest.

### Definition of Ready (before starting a story)
- Clear user value and acceptance criteria.
- Small enough for ≤ 3 days; otherwise split.
- Dependencies known (data, model, decisions).

### Definition of Done (before merging)
- Acceptance criteria met and demonstrated (screenshot or test).
- Unit tests for new logic; integration test for new adapters.
- `make check` green locally, CI green.
- Module boundaries respected (`lint-imports`), API contract regenerated if changed.
- Docs updated: README / architecture / ADR when a decision was made.
- CHANGELOG entry under *Unreleased*.

## 3. Commits

[Conventional Commits](https://www.conventionalcommits.org): `type(scope): summary`

| type | for |
|---|---|
| `feat` | user-visible capability |
| `fix` | bug fix |
| `refactor` | no behaviour change |
| `test`, `docs`, `chore`, `ci`, `build` | as named |

Scope = module or area: `feat(fabdata): add lot history query`. Breaking API change: add `!`
(`feat(api)!: ...`) and bump `/api/vN`.

## 4. Quality gates (automated)

| Gate | Local | CI |
|---|---|---|
| Format + lint (Python) | `ruff format`, `ruff check` (pre-commit) | ✓ |
| Architecture rules | `lint-imports` | ✓ |
| Tests (unit, contract, integration) | `pytest` | ✓ with Postgres |
| .NET build (warnings = errors), format, tests | `dotnet build/format/test` | ✓ |
| API contract up to date | contract tests | ✓ |
| Container images build | `docker compose build` | ✓ |

## 5. Versioning

Semantic versioning. Before 1.0, each roadmap phase is a minor release (`v0.1.0` = P0,
`v0.2.0` = P1 ...). `1.0.0` = first version shown to real users.
