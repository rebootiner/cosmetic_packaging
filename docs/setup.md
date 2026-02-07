# Setup Guide (TASK-001)

## 1) Prerequisites
- Docker + Docker Compose
- Python 3.11 (optional for local backend run)
- Node 20+ (optional for local frontend run)

## 2) Project structure
- `source/backend` : FastAPI
- `source/frontend` : React (Vite)

## 3) Run backend + DB with Docker
```bash
cp .env.example .env.local
# (optional) edit values

docker compose up --build
```

Backend health check:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/db
```

## 4) Run backend tests (TDD baseline)
```bash
cd source/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## 5) Run frontend local
```bash
cd source/frontend
npm install
npm run dev
```

## 6) Done criteria for TASK-001
- local bootstrap works
- backend health endpoints work
- backend test suite passes
