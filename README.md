# 🎬 CinemaApp — Cinema Reservation System

[![CI/CD](https://github.com/damiankowalczykdk/cinema-reservation-system/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/damiankowalczykdk/cinema-reservation-system/actions/workflows/ci-cd.yaml)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Temporal](https://img.shields.io/badge/Temporal-workflows-000000)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Helm-326CE5?logo=kubernetes&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-payments-635BFF?logo=stripe&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-assistant-412991?logo=openai&logoColor=white)

A microservice cinema booking platform: browse the repertoire, pick seats on an interactive hall map,
pay with Stripe and receive tickets with QR codes by e-mail — or let an **AI assistant** book
the whole thing for you in a chat.

---

## ✨ Features

- **Repertoire & trailers** — movies currently in cinemas, a day-by-day schedule filtered by cinema, and YouTube trailers
- **TMDB integration** — the admin adds a movie by title; its poster and trailer are fetched from TMDB automatically
- **Interactive seat map** — choose several seats at once, seats already taken are blocked
- **Guest checkout** — booking works without an account; tickets go to the e-mail given at checkout
- **My tickets** — logged-in users see their bookings and can cancel them before the screening, with an automatic Stripe refund
- **Stripe Checkout** — secure payment, confirmed via Stripe webhooks; automatic refund if the payment
  arrives after the reservation has already expired
- **Reservation hold with expiry** — seats are held for a limited time; a durable Temporal workflow releases them if the payment never arrives
- **Tickets by e-mail** — after payment the customer gets one e-mail with an HMAC-signed QR code for the whole booking,
  verifiable at the entrance via `/reservations/ticket/verify`
- **AI assistant** — an OpenAI tool-calling agent that searches screenings, shows the seat map and creates a reservation from a conversation
- **Auth0 login & roles** — JWT verified only in the API gateway; admin console for cinemas, halls, movies,
  screenings and reservations
- **PL / EN** interface

## 📸 Screenshots

| Home page | Seat selection |
|---|---|
| ![Home page](docs/images/home.png) | ![Seat selection](docs/images/seat-selection.png) |

| AI assistant | Booking through the chat |
|---|---|
| ![AI assistant](docs/images/assistant.png) | ![AI assistant chat](docs/images/assistant-chat.png) |

| Stripe Checkout (test mode) | Payment confirmed |
|---|---|
| ![Stripe Checkout](docs/images/stripe-checkout.png) | ![Payment confirmed](docs/images/payment-success.png) |

| Ticket e-mail with QR code | Admin console |
|---|---|
| ![Ticket e-mail](docs/images/ticket-email.png) | ![Admin console](docs/images/admin-screenings.png) |

---

## 🏗️ Architecture

Every API request from the browser goes through the **gateway** — the only backend service exposed to the
outside world and the only place where authentication happens. Internal services trust the gateway.
In Kubernetes the Ingress serves the frontend, and its nginx proxies `/api/*` to the gateway, so the whole
app lives under a single origin.

```mermaid
flowchart LR
    user([👤 Browser])

    subgraph cluster[" Kubernetes cluster "]
        ingress[Ingress]
        frontend[frontend<br/>React SPA on nginx]
        gateway[gateway<br/>FastAPI · Auth0 JWT · rate limit]

        cinema[cinema-service<br/>cinemas · halls · movies<br/>screenings · reservations]
        payment[payment-service<br/>Stripe Checkout + webhooks]
        ai[ai-service<br/>OpenAI tool-calling agent]
        worker[worker-service<br/>Temporal worker]

        pg[(PostgreSQL<br/>cinema_db)]
        pgpay[(PostgreSQL<br/>payment_db)]
        redis[(Redis<br/>chat history)]
        temporal{{Temporal}}
        mail[Mailpit / SMTP]
    end

    auth0[[Auth0]]
    stripe[[Stripe]]
    openai[[OpenAI]]
    tmdb[[TMDB]]

    user --> ingress
    ingress --> frontend
    frontend -->|"/api/*"| gateway
    user -. login .-> auth0
    gateway -. JWKS .-> auth0

    gateway --> cinema
    gateway --> payment
    gateway --> ai

    cinema --> pg
    cinema --> tmdb
    cinema -- start workflow --> temporal

    payment --> pgpay
    payment -- confirm --> cinema
    payment <--> stripe
    payment -- signal paid --> temporal

    ai --> openai
    ai --> redis
    ai --> cinema

    worker <--> temporal
    worker --> cinema
    worker --> mail
```

| Service | Responsibility | Tech |
|---|---|---|
| `frontend` | SPA: repertoire, trailers, seat map, checkout, AI chat, my tickets, admin console | React 19, React Router, Radix UI, Vite, nginx |
| `gateway` | Single entry point, Auth0 login flow and JWT validation, roles, rate limiting, proxy to services | FastAPI, PyJWT, slowapi |
| `cinema-service` | Core domain — cinemas, halls, movies, screenings, reservations, seat map, ticket summary | FastAPI, SQLAlchemy 2 (async), asyncpg, Alembic |
| `payment-service` | Stripe Checkout sessions, webhook verification, payment status | FastAPI, Stripe, SQLAlchemy, Alembic |
| `ai-service` | Booking assistant — OpenAI function calling over the cinema API, conversation history per user | FastAPI, OpenAI SDK, Redis |
| `worker-service` | Temporal workflows & activities: reservation expiry, ticket e-mails with QR codes | Temporal, aiosmtplib, qrcode |

## 🔄 Booking flow

The reservation lifecycle is a **Temporal workflow**. It survives restarts of any service, waits for the
payment signal and either sends the tickets or releases the seats when the hold expires.

Starting a payment extends the hold so it always outlives the Stripe session. The workflow is never told
about the extension. When its timer fires, cinema-service decides: if the hold was extended, it returns
the new deadline and the workflow simply waits again.

```mermaid
sequenceDiagram
    autonumber
    actor U as Customer
    participant G as gateway
    participant C as cinema-service
    participant T as Temporal
    participant W as worker-service
    participant P as payment-service
    participant S as Stripe

    U->>G: choose seats + e-mail
    G->>C: POST reservation
    C->>C: hold seats (PENDING, expires_at)
    C->>T: start ReservationWorkflow
    U->>G: pay
    G->>C: GET reservation
    G->>G: check owner / guest e-mail, status PENDING
    G->>P: create checkout session
    P->>C: GET total price
    P->>C: POST extend
    Note over P,C: hold extended to cover the Stripe session (capped by max hold time)
    P->>S: Checkout Session (expires_at)
    S-->>U: Stripe payment page
    U->>S: pays
    S->>P: webhook checkout.session.completed
    P->>P: verify signature, mark paid
    P->>C: confirm reservation
    Note over P,C: if the hold already expired: 409 → automatic refund, flow stops here
    P->>T: signal "paid"

    alt paid before expires_at
        T->>W: send_tickets activity
        W->>C: GET reservation summary (+ signed ticket code)
        W->>U: 📧 e-mail with the QR-code ticket
    else timer fires at expires_at
        T->>W: expire_reservation activity
        W->>C: POST expire
        alt hold was extended
            C-->>W: still PENDING + new expires_at
            Note over T: workflow waits again until the new deadline
        else really expired
            C-->>W: CANCELLED → seats released
            Note over T: workflow ends
        end
    end
```

## 🧠 Design decisions

- **Auth only in the gateway** — services sit on a private network and never parse tokens; user identity
  is forwarded in headers. One place to secure, simpler services. The gateway runs the Auth0 login itself
  and keeps the access token in an HttpOnly cookie, so JavaScript in the browser never touches it.
- **Database per service** — `cinema-service` and `payment-service` each own a separate PostgreSQL instance
  (in Compose and in Kubernetes) and talk only over HTTP, so neither can break the other's data.
- **Temporal instead of a cron job** for the payment hold — the timeout and the "paid" signal live in one
  durable workflow, so a crash or redeploy never loses a pending expiry or an unsent ticket. As a safety
  net, stale holds are also expired lazily whenever a screening's seats are read.
- **Idempotent payments** — clicking "pay" twice returns the same open Stripe session instead of creating a
  new one, and repeated webhooks for an already completed or refunded payment are ignored.
- **One booking = N seats** — seats reserved together share a `group_id`, so a single payment and a single
  e-mail cover the whole group.
- **QR tickets without an extra column** — the ticket code is an HMAC-SHA256 signature of the booking id,
  recomputed on demand, so it can be verified at the door (`/reservations/ticket/verify`) but cannot be forged.
- **AI assistant with hard limits** — capped tool-call rounds and output tokens, rate-limited in the
  gateway, conversation history kept in our own Redis (TTL + owner check) with `store=False` on the OpenAI side.
- **One Helm chart for all apps** — every app is "a container with env vars", optionally with an HTTP port,
  health probes and a migrations `initContainer`; a small `values.yaml` per app switches these on, so one
  generic chart replaces six copies of manifests.

---

## 🧰 Tech stack

- **Backend:** Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2 (async), Alembic, httpx, Poetry
- **Workflows:** Temporal
- **Data:** PostgreSQL 16, Redis 7
- **Integrations:** Auth0, Stripe Checkout, OpenAI Responses API (function calling), TMDB
- **Frontend:** React 19, React Router, Vite, Radix UI, oxlint
- **Testing:** pytest, pytest-asyncio, pytest-cov (100% line coverage), testcontainers (real PostgreSQL in integration tests), respx
- **Quality:** mypy, ruff, gitleaks, pre-commit, Conventional Commits
- **Local dev tools:** Stripe CLI (webhook forwarding), Mailpit (e-mail catcher), Temporal UI
- **Infrastructure:** Docker (multi-stage builds), Docker Compose, Kubernetes (minikube, k3s), Helm, NGINX Ingress
- **CI/CD:** GitHub Actions → GitHub Container Registry

## 📁 Project structure

```
.
├── apps/
│   ├── frontend/          # React SPA (served by nginx in Docker)
│   ├── gateway/           # API gateway, auth
│   ├── cinema-service/    # core domain + Alembic migrations
│   ├── payment-service/   # Stripe + Alembic migrations
│   ├── ai-service/        # AI booking assistant
│   └── worker-service/    # Temporal worker
├── k8s/
│   ├── chart/             # one generic Helm chart for every app
│   ├── apps/<service>/    # per-service values and ConfigMaps (Secrets are gitignored)
│   ├── infra/             # Postgres, Redis, Temporal, Mailpit
│   ├── ingress.yaml
│   └── namespace.yaml
├── docker-compose.yml     # full local environment
└── .github/workflows/ci-cd.yaml
```

---

## 🚀 Running locally

### Docker Compose

Requirements: Docker, Node.js 24, plus Auth0 / Stripe (test mode) / OpenAI / TMDB keys.

**1. Environment files** — copy the examples and fill in your keys:

```bash
cp .env.example .env
cp apps/cinema-service/.env.example apps/cinema-service/.env
cp apps/payment-service/.env.example apps/payment-service/.env
cp apps/ai-service/.env.example apps/ai-service/.env
cp apps/worker-service/.env.example apps/worker-service/.env
cp apps/gateway/.env.example apps/gateway/.env
```

**2. Start the backend** (all services, two PostgreSQL instances, Redis, Temporal, Mailpit, Stripe CLI):

```bash
docker compose up --build -d
```

**3. First run only — database migrations:**

```bash
docker compose exec cinema-service alembic upgrade head
docker compose exec payment-service alembic upgrade head
```

**4. Stripe webhook secret** — the `stripe-cli` container prints a `whsec_...` secret on start. Put it into
`STRIPE_WEBHOOK_SECRET` in `apps/payment-service/.env` and restart the service:

```bash
docker compose logs stripe-cli
docker compose restart payment-service
```

**5. Start the frontend:**

```bash
cd apps/frontend
npm install
npm run dev
```

| URL | What |
|---|---|
| http://localhost:3000 | Frontend |
| http://localhost:8000/docs | API gateway (Swagger) |
| http://localhost:8233 | Temporal UI |
| http://localhost:8025 | Mailpit — caught ticket e-mails |
| `localhost:5432` / `localhost:5433` | PostgreSQL — `cinema_db` / `payment_db` (for a DB client) |

Test payments work with card `4242 4242 4242 4242`, any future date and any CVC.

#### Auth0 setup

- **Application** (Regular Web App):
  - *Allowed Callback URLs*: `http://localhost:8000/auth/callback` (Compose), `http://localhost/api/auth/callback` (Kubernetes)
  - *Allowed Logout URLs*: `http://localhost:3000` (Compose), `http://localhost` (Kubernetes) — must match `APP_BASE_URL`
- **API**: its identifier is `AUTH0_AUDIENCE` in `apps/gateway/.env`.
- **Roles**: create `admin` and `user`, and assign `admin` to your account to unlock the admin console.
- **Post-login Action**: add the custom claims the gateway reads from the access token —
  `my-namespace/globalRoles` (list of role names) and `my-namespace/email`.

> **Empty home page?** It lists only movies with **upcoming** screenings — add a cinema, a hall, a movie
> and a few screenings with a future `start_time` in the admin console.

### Kubernetes (minikube)

Every app is deployed with a single reusable Helm chart (`k8s/chart`) and a small per-service `values.yaml`.

Before you start:
- Secrets are not committed (`k8s/**/secret.yaml` is in `.gitignore`) — create the `secret.yaml` files
  (infra and apps) with your own keys.
- The chart uses locally built images (`imagePullPolicy: Never`) — build them inside minikube's Docker
  with the tags from each `values.yaml`, e.g. `docker build -t cinema-service:1.1 apps/cinema-service`.

```bash
minikube addons enable ingress
eval $(minikube docker-env)        # then build the images

kubectl apply -f k8s/namespace.yaml
kubectl apply -R -f k8s/infra/

# for each app: cinema, payment, ai, gateway, worker, frontend
# (apply its configmap.yaml / secret.yaml if the folder has them)
kubectl apply -f k8s/apps/cinema/configmap.yaml -f k8s/apps/cinema/secret.yaml
helm install cinema k8s/chart -n cinema -f k8s/apps/cinema/values.yaml

kubectl apply -f k8s/ingress.yaml
minikube tunnel                    # app available at http://localhost
```

The Helm release name must match the app folder name — the chart names the Service `<release>-service`,
which is how the apps find each other (e.g. `http://cinema-service:8001`).
Database migrations run automatically in an `initContainer` before the service starts.

### Tests

Every backend service has **100% line coverage**. Each service is tested independently from its own folder.
Integration tests start a real PostgreSQL with testcontainers, so Docker must be running.

```bash
cd apps/cinema-service
poetry install
poetry run pytest --cov
```

---

## ⚙️ CI/CD

```mermaid
flowchart LR
    push(["push / PR"]) --> lint["lint<br/>pre-commit: ruff, gitleaks, yaml"]
    push --> commits["commit messages<br/>Conventional Commits · PR only"]
    push --> test["tests<br/>matrix: 5 services"]
    lint --> build
    test --> build
    build["build and push<br/>matrix: 6 images · push only"] --> ghcr[("ghcr.io")]
    ghcr -. pull .-> k3s["k3s on VPS<br/>in progress"]
```

- **lint** — all pre-commit hooks on the whole repo
- **commits** — every commit in a PR must follow Conventional Commits
- **test** — pytest for each backend service in a matrix
- **build** — on push, Docker images for all 6 apps are pushed to GHCR, tagged with the commit SHA and `latest`

---

## 👤 Author

**Damian Kowalczyk** — [GitHub](https://github.com/damiankowalczykdk)
