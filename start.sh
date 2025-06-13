#!/usr/bin/env bash
echo "Running Prisma migrations..."
prisma generate
prisma migrate deploy

echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 10000
