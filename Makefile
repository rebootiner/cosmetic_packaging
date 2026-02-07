backend-test:
	cd source/backend && pytest

backend-run:
	cd source/backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd source/frontend && npm run dev

up:
	docker compose up --build
