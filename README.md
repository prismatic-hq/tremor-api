# tremor-api

Seismic signal streams and alerts. FastAPI + Postgres CRUD service with an `alerts` resource.
Owns the `tremor` Postgres schema, including its Alembic version table.

Related repos:
- [caldera-platform](https://github.com/prismatic-hq/caldera-platform): CDK, GitOps, shared Helm chart, event contracts
- [applications-infra](https://github.com/prismatic-hq/applications-infra): desired state per environment
- [steward-api](https://github.com/prismatic-hq/steward-api): resource and operations management service

## Quick Start

Requires `uv`, `task` and Docker.

```sh
task init && task up   # API on http://localhost:8001/docs
```

## Key Commands

| Command | What it does |
|---|---|
| `task init` | Install dependencies and git hooks, create `.env` from `.env.example` |
| `task dev` | Postgres in Docker, API with hot reload |
| `task test` | pytest against real Postgres (testcontainers) |
| `task lint` | ruff lint and format check |
| `task build` | Build the container image |
| `task up` / `task down` | Start / stop the Docker Compose stack |

## Configuration

Database settings come from `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` and `DB_PASSWORD`.
Endpoints: `/alerts`, `/healthz`, `/readyz`, `/metrics`.
Migrations: `uv run alembic upgrade head`.

## CI

Every push runs lint, tests and one multi-arch (amd64, arm64) image build in parallel jobs; pull
requests run them only when they come from forks. When the repo variable `AWS_ROLE_ARN` is set,
pushes publish `sha-<short-sha>` (plus `main` on `main`) to ECR with a BuildKit registry cache, and
skip the build when that tag already exists. Fork code never gets AWS credentials.
