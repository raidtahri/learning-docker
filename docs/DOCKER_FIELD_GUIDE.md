# Docker Field Guide (DevOps)

> Practical reference for DevOps engineers working with Docker, Dockerfiles, and docker-compose.

---

## Section 1 — General Rules for Writing a Dockerfile

### 1. Always pin your base image version (never use `:latest`)

- **Why**: `:latest` can change under you and break builds.
- **Good**:

```dockerfile
FROM python:3.11.10-slim
```

- **Bad**:

```dockerfile
FROM python:latest
```

### 2. Order instructions from least to most frequently changed (layer caching)

- **Why**: Docker reuses cached layers. Place stable steps first.
- **Good**:

```dockerfile
FROM node:20
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
```

- **Bad**:

```dockerfile
FROM node:20
WORKDIR /app
COPY . .
RUN npm ci
```

### 3. Combine RUN commands with `&&` to reduce layers

- **Why**: Each `RUN` creates a layer. Combining reduces image size.
- **Good**:

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
```

- **Bad**:

```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*
```

### 4. Use `.dockerignore` to exclude unnecessary files

- **Why**: Reduces build context and prevents copying secrets or large folders.
- **Good**:

```
node_modules
.git
.env
```

### 5. Never store secrets or credentials in a Dockerfile

- **Why**: Dockerfiles are versioned and can leak sensitive data.
- **Good**: Pass secrets via runtime env vars or secret management.
- **Bad**:

```dockerfile
ENV DATABASE_PASSWORD=supersecret
```

### 6. Always use a non-root user for the runtime stage

- **Why**: Running as root is a security risk.
- **Good**:

```dockerfile
RUN useradd -m appuser
USER appuser
```

- **Bad**:

```dockerfile
USER root
```

### 7. Use `COPY` instead of `ADD` unless you specifically need `ADD`'s features

- **Why**: `ADD` has extra behavior (tar extraction, URLs) that can be surprising.
- **Good**:

```dockerfile
COPY . .
```

- **Bad**:

```dockerfile
ADD . .
```

### 8. Set `WORKDIR` explicitly — never rely on default directory

- **Why**: Makes paths predictable and avoids errors.
- **Good**:

```dockerfile
WORKDIR /app
```

- **Bad**:

```dockerfile
# No WORKDIR set, defaults to /
```

### 9. Use `ENTRYPOINT` for the binary, `CMD` for default arguments

- **Why**: Keeps intent clear and supports overrides.
- **Good**:

```dockerfile
ENTRYPOINT ["gunicorn", "app:app"]
CMD ["--bind", "0.0.0.0:8080"]
```

- **Bad**:

```dockerfile
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
```

### 10. Always add a `HEALTHCHECK` instruction in production images

- **Why**: Enables orchestrators to detect unhealthy containers.
- **Good**:

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD curl -f http://localhost:8080/health || exit 1
```

- **Bad**: No healthcheck at all.

---

## Section 2 — General Rules for Writing a `docker-compose.yml`

### 1. Always specify the image version or use `build:` context — never rely on implicit pulls

- **Why**: Implicit pulls can unexpectedly change behavior.
- **Example**:

```yaml
services:
  web:
    image: nginx:1.25-alpine
```

### 2. Use named volumes instead of anonymous volumes for persistent data

- **Why**: Anonymous volumes are hard to manage and can leak disk space.
- **Example**:

```yaml
services:
  db:
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```

### 3. Define a custom network — never rely on the default bridge network

- **Why**: Custom networks provide predictable DNS and isolation.
- **Example**:

```yaml
networks:
  app-net:

services:
  api:
    networks:
      - app-net
```

### 4. Use environment variables with `.env` file instead of hardcoding values

- **Why**: Keeps sensitive and env-specific values out of version control.
- **Example**:

```yaml
services:
  web:
    environment:
      - DATABASE_URL=${DATABASE_URL}
```

### 5. Use `depends_on` with healthcheck condition, not just service name

- **Why**: `depends_on` alone only waits for container start, not readiness.
- **Example**:

```yaml
services:
  web:
    depends_on:
      db:
        condition: service_healthy
```

### 6. Set resource limits (memory, CPU) for each service

- **Why**: Prevents a container from consuming all host resources.
- **Example**:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
```

### 7. Use `restart: unless-stopped` for production services

- **Why**: Ensures services recover after host restarts.
- **Example**:

```yaml
services:
  web:
    restart: unless-stopped
```

### 8. Separate concerns — one process per container

- **Why**: Simplifies scaling, monitoring, and restarts.
- **Example**: Don’t run cron + webserver in same container.

### 9. Always expose ports explicitly and document why

- **Why**: Makes service contract clear.
- **Example**:

```yaml
services:
  web:
    ports:
      - '8080:8080' # Public API port
```

### 10. Use profiles to separate dev and prod service groups

- **Why**: Keeps dev-only services (e.g., debuggers, mocks) out of prod.
- **Example**:

```yaml
services:
  debug:
    profiles: ['dev']
```

---

## Section 3 — Files to Expect Per Language

### Python App

| File                       | Purpose                          | Required for Docker? | Notes for DevOps                                  |
| -------------------------- | -------------------------------- | -------------------- | ------------------------------------------------- |
| `app.py`                   | Application entrypoint           | Yes                  | Ensure it reads env vars for config               |
| `requirements.txt`         | Dependency list                  | Yes (common)         | Pin versions for reproducible builds              |
| `Pipfile` / `Pipfile.lock` | Pipenv dependency management     | Optional             | Use only if project uses Pipenv                   |
| `pyproject.toml`           | Poetry / PEP 518 config          | Optional             | Use only if project uses Poetry or modern tooling |
| `.env`                     | Runtime environment vars         | Optional             | Never copy into image; use compose/env files      |
| `gunicorn.conf.py`         | Gunicorn config                  | Optional             | Often copied into image for prod web servers      |
| `.dockerignore`            | Exclude files from build context | Yes                  | Prevents sending dev files into build context     |

**What the DevOps engineer needs to understand about this app before writing the Dockerfile**

- Which dependency tool is used (pip, pipenv, poetry)
- Whether it’s a simple script or uses a WSGI server (gunicorn/uvicorn)
- Whether it needs compiled wheels (C extensions)

---

### Node.js App

| File                     | Purpose                     | Required for Docker? | Notes for DevOps                                                   |
| ------------------------ | --------------------------- | -------------------- | ------------------------------------------------------------------ |
| `index.js` / `server.js` | App entrypoint              | Yes                  | Confirm correct entrypoint in package.json                         |
| `package.json`           | Dependencies and scripts    | Yes                  | Must be copied for `npm ci`/`install`                              |
| `package-lock.json`      | Locked dependencies         | Yes                  | Ensures reproducible builds                                        |
| `.npmrc`                 | NPM config (registry, auth) | Optional             | If using private registry; keep out of image when containing creds |
| `.env`                   | Runtime environment vars    | Optional             | Do not bake into image                                             |
| `.nvmrc`                 | Node version hint           | Optional             | Helps local dev match runtime                                      |
| `.dockerignore`          | Exclude node_modules, etc.  | Yes                  | Critical for build performance                                     |

**What the DevOps engineer needs to understand about this app before writing the Dockerfile**

- Is it TypeScript, plain JS, or a frontend build?
- Does it require a build step (`npm run build`) or just run with `node`?
- Are there native dependencies that require build tools?

---

### Java App (Maven/Spring Boot)

| File                                        | Purpose                    | Required for Docker?     | Notes for DevOps                     |
| ------------------------------------------- | -------------------------- | ------------------------ | ------------------------------------ |
| `pom.xml`                                   | Maven build config         | Yes (Maven)              | Defines dependencies, plugins        |
| `src/main/java/`                            | Java source                | Yes                      | Needed for build stage               |
| `src/main/resources/application.properties` | Config                     | Optional                 | Externalize via env vars if possible |
| `target/*.jar`                              | Build artifact             | Yes (runtime)            | Used in runtime stage                |
| `.mvn/`                                     | Maven wrapper files        | Optional but recommended | Enables consistent Maven version     |
| `mvnw`                                      | Maven wrapper script       | Optional but recommended | Use in CI/build for reproducibility  |
| `.dockerignore`                             | Exclude target, .git, etc. | Yes                      | Keep build context small             |

**What the DevOps engineer needs to understand about this app before writing the Dockerfile**

- Whether it’s built with Maven or Gradle (determines build commands)
- Whether the jar is “fat”/“uber” or needs additional runtime setup
- How configuration is supplied (profiles, env vars, config server)

---

## Section 4 — Build Tools & Commands Per Language (Docker Context)

### 4.1 — Python Build Tools

Python has no compilation step — “building” means resolving and installing dependencies. The
distinction between pip, pipenv, and poetry matters because each tool uses different lock files and
installation commands. The DevOps engineer must recognize which tool the dev team uses before
writing the Dockerfile.

#### Table 1 — Python Build Tools Comparison

| Tool      | Config File      | Lock File        | Used When                                    |
| --------- | ---------------- | ---------------- | -------------------------------------------- |
| pip       | requirements.txt | n/a              | Simple apps / old projects                   |
| pipenv    | Pipfile          | Pipfile.lock     | Projects using Pipenv environment management |
| poetry    | pyproject.toml   | poetry.lock      | Modern projects using Poetry                 |
| pip-tools | requirements.in  | requirements.txt | Projects generating requirements from inputs |

#### Table 2 — Key pip Commands for Docker

| Command                                          | What It Does                  | Docker-Specific Note                                           |
| ------------------------------------------------ | ----------------------------- | -------------------------------------------------------------- |
| `pip install -r requirements.txt`                | Installs listed packages      | Use in Docker to install pinned deps                           |
| `pip install --no-cache-dir -r requirements.txt` | Installs without cache        | Prevents pip cache from bloating image                         |
| `pip install --no-deps`                          | Installs without dependencies | Useful when deps are preinstalled or in wheels                 |
| `pip freeze > requirements.txt`                  | Dumps installed packages      | Avoid in Dockerfile; use in local dev to lock deps             |
| `pip-compile requirements.in`                    | Generates pinned requirements | Run outside Docker; commit output                              |
| `pip install --upgrade pip`                      | Upgrades pip                  | Often in build stage, but keep layers minimal                  |
| `pip install gunicorn`                           | Installs gunicorn             | If not in requirements, add explicitly                         |
| `pip install -e .`                               | Editable install              | **Never use in Docker** — it links source, breaks immutability |

#### Docker Layer Caching Pattern for Python

```dockerfile
# Correct — cache the dependency layer separately
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .   ← app code copied AFTER deps installed

# Wrong — cache breaks on every code change
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
```

#### Requirements vs requirements-dev in multistage Dockerfile

- `requirements.txt`: runtime dependencies
- `requirements-dev.txt`: dev/test dependencies

In a multistage build, install both in the build stage (if needed for tests) and only keep runtime
deps in the final stage.

---

### 4.2 — Node.js Build Tools

Node has both a dependency manager (npm/yarn/pnpm) AND potentially a build step (webpack, vite, tsc)
depending on the project type. The DevOps engineer must distinguish between:

- raw Node API (no build step)
- TypeScript API (requires `tsc`)
- frontend app (requires `npm run build`) This distinction completely changes how the Dockerfile is
  written.

#### Table 1 — Node.js Build Tools Comparison

| Tool           | Config File  | Lock File         | Install Command                  | Used When                                  |
| -------------- | ------------ | ----------------- | -------------------------------- | ------------------------------------------ |
| npm            | package.json | package-lock.json | `npm ci`                         | Default Node package manager               |
| yarn (classic) | package.json | yarn.lock         | `yarn install --frozen-lockfile` | Projects using Yarn v1                     |
| yarn berry     | package.json | yarn.lock         | `yarn install --immutable`       | Yarn v2+ (Plug’n’Play)                     |
| pnpm           | package.json | pnpm-lock.yaml    | `pnpm install --frozen-lockfile` | Fast installs with content-addressed store |

#### Table 2 — Key npm/yarn Commands for Docker

| Command                          | What It Does                           | Docker-Specific Note                        |
| -------------------------------- | -------------------------------------- | ------------------------------------------- |
| `npm install`                    | Installs deps, may update package-lock | Not deterministic; avoid in Docker          |
| `npm ci`                         | Installs from lockfile                 | Mandatory in Docker for reproducible builds |
| `npm run build`                  | Runs build script                      | Needed if project has compile step          |
| `npm prune --production`         | Removes devDependencies                | Use in final stage to slim image            |
| `npm audit`                      | Checks vulnerabilities                 | Better run in CI, not in Docker build       |
| `yarn install --frozen-lockfile` | Yarn equivalent of `npm ci`            | Ensures lockfile matches                    |
| `pnpm install --frozen-lockfile` | pnpm equivalent                        | Ensures deterministic install               |

#### Table 3 — node_modules in Docker: Key Rules

| Rule                                                           | Explanation                           |
| -------------------------------------------------------------- | ------------------------------------- |
| Always add `node_modules` to `.dockerignore`                   | Prevents copying host deps into image |
| Never `COPY node_modules` from host into image                 | Host deps may not match Linux runtime |
| In multistage: copy `node_modules` from builder, not from host | Keeps consistent install              |
| dependencies vs devDependencies                                | Use only prod deps in runtime stage   |

#### Multistage Pattern for Node.js

##### Case A — Pure API (no build step)

```dockerfile
# Stage 1: builder
FROM node:20 AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .

# Stage 2: runtime
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app ./
USER node
CMD ["node", "index.js"]
```

##### Case B — TypeScript API or Frontend (with build step)

```dockerfile
# Stage 1: build
FROM node:20 AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN npm prune --production

# Stage 2: runtime
FROM gcr.io/distroless/nodejs:20
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER nonroot
ENTRYPOINT ["node", "dist/index.js"]
```

---

### 4.3 — Java Build Tools (Maven & Gradle)

Java MUST be compiled — the output is a `.jar` or `.war` file. Maven and Gradle are both common; the
DevOps engineer must identify which one the project uses by inspecting root files. The builder stage
is heavy (JDK + Maven/Gradle + downloaded deps) but the runtime stage only needs the JRE and the
`.jar` file. This is where multistage build has the BIGGEST impact on image size.

#### Table 1 — Identifying the Build Tool by File

| File Present in Repo | Build Tool             | Wrapper Script | What It Means for DevOps                                  |
| -------------------- | ---------------------- | -------------- | --------------------------------------------------------- |
| `pom.xml`            | Maven                  | `./mvnw`       | Use Maven commands; prefer wrapper for consistent version |
| `build.gradle`       | Gradle                 | `./gradlew`    | Use Gradle commands; wrapper ensures consistent version   |
| `build.gradle.kts`   | Gradle (Kotlin DSL)    | `./gradlew`    | Same as Gradle, Kotlin DSL                                |
| `.mvn/` directory    | Maven wrapper present  | `./mvnw`       | Enables builds without local Maven install                |
| `gradle/wrapper/`    | Gradle wrapper present | `./gradlew`    | Enables builds without local Gradle install               |

---

## Section 5 — Common Mistakes DevOps Engineers Make When Containerizing Apps

1. ❌ **Using `:latest` tag in base image**  
   💥 Builds break unpredictably when upstream changes.  
   ✅ Pin a specific version: `FROM node:20.5.0-alpine`.

2. ❌ **Running containers as root**  
   💥 Security risk; container can escape or be exploited.  
   ✅ Create and use a non-root user:

   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

3. ❌ **Copying entire project with `COPY . .` before installing dependencies**  
   💥 Breaks cache; rebuilds on any source change.  
   ✅ Install deps first:

   ```dockerfile
   COPY package.json package-lock.json ./
   RUN npm ci
   COPY . .
   ```

4. ❌ **Not using multistage builds for compiled languages**  
   💥 Image contains build tools and caches, ballooning size.  
   ✅ Use builder stage and copy only output to final image.

5. ❌ **Hardcoding environment variables like DB passwords in the Dockerfile**  
   💥 Secrets leak via image layers.  
   ✅ Use runtime env vars or secret management.

6. ❌ **Not adding a `.dockerignore` file (copying node_modules, .git, etc.)**  
   💥 Slows builds, increases context, and can leak sensitive files.  
   ✅ Add `.dockerignore` with `node_modules`, `.git`, `.env`, etc.

7. ❌ **Using `ADD` instead of `COPY` for local files**  
   💥 `ADD` can unexpectedly unpack tarballs or fetch URLs.  
   ✅ Use `COPY` unless you explicitly need `ADD` behavior.

8. ❌ **Installing dev dependencies in the production image**  
   💥 Larger image, potential security surface.  
   ✅ Install only production deps or prune dev deps.

9. ❌ **Not setting a `WORKDIR` and relying on root `/`**  
   💥 Commands run in unpredictable locations.  
   ✅ Set `WORKDIR /app`.

10. ❌ **Using `CMD` to run multiple processes instead of a process manager**  
    💥 Only one process is PID 1; others won’t be managed properly.  
    ✅ Use a process supervisor or separate containers per process.

11. ❌ **Not handling signals properly (PID 1 problem — not using exec form)**  
    💥 `SIGTERM` not propagated; container doesn’t stop cleanly.  
    ✅ Use exec form:

    ```dockerfile
    ENTRYPOINT ["gunicorn", "app:app"]
    ```

12. ❌ **Exposing the wrong port or forgetting to `EXPOSE` the port**  
    💥 Other services can’t connect; documentation mismatch.  
    ✅ `EXPOSE 8080` and document.

13. ❌ **Using `depends_on` in Compose without health check**  
    💥 Service starts before dependency is ready, causing failures.  
    ✅ Use `condition: service_healthy` with `healthcheck`.

14. ❌ **Not setting resource limits in Compose — container eats all host memory**  
    💥 Host becomes unstable.  
    ✅ Define limits under `deploy.resources.limits`.

15. ❌ **Building the image without pruning — disk fills up over time on the CI server**  
    💥 CI runners run out of disk space.  
    ✅ Run `docker system prune -af` or use `docker builder prune`.

---

## Section 6 — Quick Reference Cheat Sheet

### Dockerfile Instructions Table

| Instruction   | Purpose                          | Example                                           |
| ------------- | -------------------------------- | ------------------------------------------------- |
| `FROM`        | Base image                       | `FROM python:3.11.10-slim`                        |
| `WORKDIR`     | Set working directory            | `WORKDIR /app`                                    |
| `COPY`        | Copy files into image            | `COPY . .`                                        |
| `ADD`         | Copy + extract/tar/URL           | `ADD https://... /tmp/`                           |
| `RUN`         | Execute commands at build time   | `RUN apt-get update && apt-get install -y curl`   |
| `ENV`         | Set environment variable         | `ENV PORT=8080`                                   |
| `ARG`         | Build-time variable              | `ARG NODE_VERSION=20`                             |
| `EXPOSE`      | Document port                    | `EXPOSE 8080`                                     |
| `HEALTHCHECK` | Health probe for runtime         | `HEALTHCHECK CMD curl -f http://localhost/health` |
| `USER`        | Set user for subsequent commands | `USER appuser`                                    |
| `ENTRYPOINT`  | Container entrypoint             | `ENTRYPOINT ["node", "app.js"]`                   |
| `CMD`         | Default args for ENTRYPOINT      | `CMD ["--port", "8080"]`                          |
| `VOLUME`      | Declare mount point              | `VOLUME /data`                                    |
| `LABEL`       | Metadata                         | `LABEL maintainer="dev@org.com"`                  |

### Docker Compose Keys Table

| Key           | Purpose                      | Example                                       |
| ------------- | ---------------------------- | --------------------------------------------- |
| `build`       | Build context/args           | `build: .`                                    |
| `image`       | Image name/tag               | `image: myapp:1.0`                            |
| `ports`       | Map host<->container ports   | `ports: - "8080:8080"`                        |
| `volumes`     | Mount host paths/volumes     | `volumes: - db-data:/var/lib/postgresql/data` |
| `environment` | Set env vars                 | `environment: - DATABASE_URL=${DATABASE_URL}` |
| `env_file`    | Load env vars from file      | `env_file: .env`                              |
| `networks`    | Attach services to networks  | `networks: - app-net`                         |
| `depends_on`  | Service startup order        | `depends_on: - db`                            |
| `restart`     | Restart policy               | `restart: unless-stopped`                     |
| `healthcheck` | Define service health checks | `healthcheck: ...`                            |
| `profiles`    | Group services by profile    | `profiles: ["dev"]`                           |
| `deploy`      | Swarm deploy settings        | `deploy: ...`                                 |

---

This guide is intended as a practical field reference for containerizing applications reliably,
safely, and consistently.
