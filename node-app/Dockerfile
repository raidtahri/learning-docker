# syntax=docker/dockerfile:1

############################################
# Stage 1 — Builder
############################################

# Use the full official Node image for installing dependencies.
FROM node:20 AS builder

# Set the working directory inside the image.
WORKDIR /app

# Copy dependency manifests first to maximize layer caching.
COPY package.json package-lock.json* ./

# Install production dependencies in a repeatable way (uses lockfile if present).
RUN npm install --omit=dev

# Copy the application source code after deps (better caching).
COPY index.js .

############################################
# Stage 2 — Runtime (Production)
############################################

# Use a distroless Node runtime for smaller, safer images.
FROM gcr.io/distroless/nodejs20-debian12 AS runtime

# Set the working directory inside the runtime image.
WORKDIR /app

# Copy only what we need at runtime: node_modules and app code.
COPY --from=builder /app/node_modules /app/node_modules
COPY --from=builder /app/index.js /app/index.js
COPY --from=builder /app/package.json /app/package.json

# Set environment variables for production defaults.
ENV PORT=3000 \
    APP_NAME=node-app \
    LOG_LEVEL=info \
    LOG_DIR=/var/log/node-app

# Expose the container port (documentation + tooling).
EXPOSE 3000

# Distroless images already include a non-root user named "nonroot".
# Switch to non-root for least privilege.
USER nonroot

# Health check without curl/wget: use Node to call the local endpoint.
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
  CMD ["node", "-e", "const http=require('http');const port=process.env.PORT||3000;const req=http.get({host:'127.0.0.1',port,path:'/health',timeout:2000},res=>process.exit(res.statusCode===200?0:1));req.on('error',()=>process.exit(1));req.on('timeout',()=>{req.destroy();process.exit(1);});"]

# Entrypoint defines the executable; CMD provides default args.
ENTRYPOINT ["node"]
CMD ["index.js"]

