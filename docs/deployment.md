# Prahari AI - Zoho Catalyst AppSail Deployment Guide

This guide covers deploying the Prahari AI Backend (FastAPI) and Frontend (Next.js) to Zoho Catalyst AppSail.

## Prerequisites
1. Zoho Catalyst CLI installed (`npm install -g catalyst-cli`).
2. A Zoho Catalyst project created via the Catalyst Console.
3. Authenticated CLI session (`catalyst login`).

## Step 1: Backend Deployment
1. Navigate to the backend directory:
   ```bash
   cd prahari-backend
   ```
2. Initialize AppSail (if not already done):
   ```bash
   catalyst init
   # Select AppSail -> Python 3.12 -> Specify Build Command: `pip install -r requirements.txt`
   # Specify Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $X_ZOHO_CATALYST_LISTEN_PORT`
   ```
3. Set Production Environment Variables via the Catalyst Console (Postgres URI, Neo4j URI, Qdrant URL, JWT Secrets).
4. Deploy the backend:
   ```bash
   catalyst deploy
   ```

## Step 2: Frontend Deployment
1. Navigate to the frontend directory:
   ```bash
   cd prahari-frontend
   ```
2. Build the production application:
   ```bash
   npm run build
   ```
3. Initialize AppSail:
   ```bash
   catalyst init
   # Select AppSail -> Node.js 20 -> Specify Build Command: `npm install --legacy-peer-deps`
   # Specify Start Command: `npm start`
   ```
4. Configure `.env.production` to point to the AppSail backend URL.
5. Deploy the frontend:
   ```bash
   catalyst deploy
   ```

## Step 3: Infrastructure Verification
After deployment, verify:
- Catalyst Auth is correctly integrated.
- Catalyst Data Store and Stratus are accessible.
- Background tasks (Signals/Cron) are firing.
