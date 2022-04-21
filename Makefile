.PHONY: run lint test test-e2e install prod-install clean

run: docker-compose.yml
	docker-compose up --build

lint: docker-compose.yml
	docker-compose run backend python -m black . && python -m isort --profile=black . && python -m flake8 --config=./.flake8 .

test: docker-compose.yml
	docker-compose run backend python -m pytest

test-e2e: lint
	./venv/bin/python -m pytest -ra -v -m e2e ./tests

test-e2e-baseline: lint
	./venv/bin/python -m pytest -ra -v -m e2e --visual-baseline ./tests

coverage: install
	./venv/bin/python -m http.server --bind 127.0.0.1 --directory coverage

install: requirements.dev.txt
	python -m venv venv
	./venv/bin/pip install -r requirements.dev.txt

prod-install: requirements.txt
	python -m pip install -r requirements.txt

clean:
	rm -rf __pycache__
	rm -rf pytest_cache
	rm -rf venv
