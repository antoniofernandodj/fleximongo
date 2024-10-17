run:
	docker compose down
	docker compose up -d
	uv run uvicorn app:app --reload --port 7000
