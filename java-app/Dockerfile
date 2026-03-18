# syntax=docker/dockerfile:1

############################################
# Stage 1 — Builder
############################################

# Use Maven + JDK to compile the application.
FROM maven:3.9-eclipse-temurin-17 AS builder

# Set the working directory inside the image.
WORKDIR /app

# Copy Maven descriptor first to maximize layer caching.
COPY pom.xml .

# Pre-fetch dependencies (improves subsequent build performance).
RUN mvn -q -e -DskipTests dependency:go-offline

# Copy the source code after dependencies.
COPY src ./src

# Build a runnable Spring Boot jar.
RUN mvn -q -DskipTests package

############################################
# Stage 2 — Runtime (Production)
############################################

# Use a smaller JRE-only image for runtime.
FROM eclipse-temurin:17-jre-alpine AS runtime

# Set the working directory inside the runtime image.
WORKDIR /app

# Create a non-root user and group for least privilege.
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy only the built jar from the builder stage.
COPY --from=builder /app/target/*.jar /app/app.jar

# Set environment variables for production defaults.
ENV PORT=8080 \
    APP_NAME=java-app \
    JAVA_OPTS="-XX:MaxRAMPercentage=75.0 -XX:+UseContainerSupport"

# Expose the container port (documentation + tooling).
EXPOSE 8080

# Healthcheck uses busybox wget (present on Alpine) to probe the endpoint.
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=3 \
  CMD wget -qO- "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1 || exit 1

# Switch to the non-root user.
USER appuser

# Entrypoint defines the executable; CMD provides default args.
ENTRYPOINT ["sh", "-c"]
CMD ["exec java $JAVA_OPTS -Dserver.port=$PORT -Dapp.name=$APP_NAME -jar /app/app.jar"]

