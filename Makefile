backend-test:
	cd source/backend && pytest

backend-run:
	cd source/backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd source/frontend && npm run dev

up:
	docker compose up --build

up-stage1-light:
	docker compose -f docker-compose.yml -f docker-compose.stage1-light.yml up --build backend frontend

down-stage1-light:
	docker compose -f docker-compose.yml -f docker-compose.stage1-light.yml down

demo-stage1:
	$(MAKE) up-stage1-light
