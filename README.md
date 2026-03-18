# docker-mastery

A hands-on learning repository demonstrating Docker best practices across **Python (Flask)**, **Node.js (Express)**, and **Java (Spring Boot)** using **real, runnable mini-apps**.

This repo is intentionally small but “production-shaped”: multistage builds, small runtime images, non-root users, health checks, Compose orchestration, custom networks, named volumes, and environment management.

---

## Repo Overview

You will learn how to:

- Build images using **multistage Dockerfiles** (builder → runtime).
- Improve rebuild speed using **layer caching** (copy dependency manifests first).
- Run containers as a **non-root user**.
- Prefer **slim / distroless** runtime images to reduce attack surface.
- Use **HEALTHCHECK** to help orchestrators detect unhealthy containers.
- Orchestrate multiple services with **Docker Compose** using:
  - **custom bridge networks**
  - **environment variables**
  - **named volumes**

---

## Concepts Covered

- **Multistage builds**
- **Layer caching**
- **Non-root user**
- **Slim / distroless runtime images**
- **Health checks**
- **Named volumes**
- **Custom networks**
- **Environment management (env vars, defaults)**
- **Compose service dependencies (health-gated startup)**
- **Port mapping and inter-service networking**

---

## Project Structure

```text
docker-mastery/
├── README.md                        - Full learning guide + commands + concepts
│
├── python-app/
│   ├── app.py                       - Flask REST API (2 endpoints)
│   ├── requirements.txt             - Python dependencies
│   ├── Dockerfile                   - Multistage: builder + slim runtime
│   └── .dockerignore                - Reduce build context
│
├── node-app/
│   ├── index.js                     - Express REST API (2 endpoints)
│   ├── package.json                 - Node dependencies + start script
│   ├── Dockerfile                   - Multistage: node builder + distroless runtime
│   └── .dockerignore                - Reduce build context
│
├── java-app/
│   ├── src/main/java/App.java       - Spring Boot REST API (2 endpoints)
│   ├── pom.xml                      - Maven build definition
│   ├── Dockerfile                   - Multistage: maven builder + JRE runtime
│   └── .dockerignore                - Reduce build context
│
└── docker-compose.yml               - Runs all 3 apps on a shared custom network
```

---

## How to Run

### Run each app individually (Docker)

From the repository root:

#### Python (Flask)

```bash
docker build -t docker-mastery-python ./python-app
docker run --rm -p 5001:5000 -e APP_NAME=python-app -e LOG_LEVEL=INFO docker-mastery-python
```

Test:

```bash
curl -s http://localhost:5001/
curl -s http://localhost:5001/health
```

#### Node (Express)

```bash
docker build -t docker-mastery-node ./node-app
docker run --rm -p 3001:3000 -e APP_NAME=node-app -e LOG_LEVEL=info docker-mastery-node
```

Test:

```bash
curl -s http://localhost:3001/
curl -s http://localhost:3001/health
```

#### Java (Spring Boot)

```bash
docker build -t docker-mastery-java ./java-app
docker run --rm -p 8081:8080 -e APP_NAME=java-app docker-mastery-java
```

Test:

```bash
curl -s http://localhost:8081/
curl -s http://localhost:8081/health
```

---

### Run everything together (Docker Compose)

```bash
docker compose up --build
```

Test all three:

```bash
curl -s http://localhost:5001/
curl -s http://localhost:3001/
curl -s http://localhost:8081/
```

Stop:

```bash
docker compose down
```

If you want to remove the named volume too:

```bash
docker compose down -v
```

---

## Multistage Build Explained

ASCII diagram (common pattern used here):

```text
          (Stage 1: builder)                          (Stage 2: runtime)
┌──────────────────────────────────┐          ┌──────────────────────────────────┐
│ Full language image              │          │ Minimal runtime image            │
│ (python/node/maven)              │          │ (slim/distroless/JRE)            │
│                                  │          │                                  │
│ - copy dependency manifests      │          │ - copy only artifacts from builder│
│ - install deps / compile         │  COPY    │ - no build tools needed          │
│ - build artifacts produced       │  FROM    │ - run as non-root user           │
│                                  │ ───────▶ │ - healthcheck                    │
└──────────────────────────────────┘          └──────────────────────────────────┘
```

Key idea: **only the output you need** (deps/artifacts) crosses into the runtime stage.

---

## Image Size Comparison Table (Estimated)

These are realistic ballpark estimates (vary by dependencies and platform):

| App | Typical single-stage (full image) | Multistage runtime image |
|-----|----------------------------------:|--------------------------:|
| Python (Flask) | ~950MB–1.2GB | ~140MB–220MB |
| Node (Express) | ~900MB–1.1GB | ~60MB–120MB (distroless) |
| Java (Spring Boot) | ~900MB–1.3GB | ~180MB–300MB (JRE only) |

Why smaller matters: faster pulls, less CVE surface, quicker deploys, cheaper storage/bandwidth.

---

## Key Docker Concepts Glossary (10)

- **Image**: A packaged filesystem + metadata used to start containers.
- **Container**: A running instance of an image with its own process tree and filesystem layers.
- **Layer**: A filesystem diff created by each Dockerfile instruction (important for caching).
- **Build context**: Files sent to the Docker daemon during `docker build` (keep small with `.dockerignore`).
- **Multistage build**: Multiple `FROM` stages; copy artifacts from builder to runtime to shrink images.
- **Distroless**: Runtime images without package managers/shells; smaller and harder to exploit.
- **Non-root user**: Runs app with least privilege inside the container.
- **Health check**: Container-side command to report healthy/unhealthy state to the runtime/orchestrator.
- **Named volume**: Persistent storage managed by Docker, decoupled from container lifecycle.
- **Bridge network**: Default Docker networking driver for single-host container-to-container connectivity.

---
