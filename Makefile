req: django_core/requirements.txt
	pip freeze > django_core/requirements.txt

.PHONY: up
up:
	docker-compose build
	docker-compose up

.PHONY: run
run: up	

.DEFAULT_GOAL := up
