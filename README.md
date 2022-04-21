# Python Pipreqs API

Powered by [FastAPI](https://github.com/tiangolo/fastapi) + [pipreqs](https://github.com/bndr/pipreqs).
Specifically, FastAPI runs the API server for receiving requests and pipreqs does the code requirements assessing.

Basic API to power bots / helpers to rid the world of Python projects without correct requirements!

Attempts to shallow `git clone` a given repo then run `pipreqs` on the codebase.
Returns the resulting `requirements.txt` contents!

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/gerardrbentley/pipreqs-api)

## Roadmap

- [ ] 🧪 Generation Options:
  - Strict / Unpinned / Compatible / Greater Than options
  - Alternate PyPi server
  - Use requirements data to make conda `environment.yml` or `pyproject.toml`
- [ ] 🤖 API Options:
  - Auto open Github Pull Request with updated requirements
  - Allow partial repo / branch urls instead of full git url
  - Safe way to allow zip fetch / analysis?
- [ ] 📺 Frontend:
  - Streamlit app for requesting repo(s)

## Local Run

### Update environment

- Copy or Rename `.env.example` as `.env.dev`

```sh
mv .env.example .env.dev
```

### Run with Docker

Requires [docker-compose](https://docs.docker.com/compose/install/) to be installed (this comes with Docker Desktop).

```sh
make run
# Open localhost:8000/health
```

#### Lint, Check, Test with Docker

```sh
# Linting
make lint
# Unit Testing
make test

# Display coverage report after test (uses local python, not docker)
make coverage
```

### Local Python environment

For code completion / linting / developing / etc.

```sh
make install
. ./venv/bin/activate
cd backend
```

## Features

- Development Containerization with [Docker](https://docs.docker.com/)
- Dependency installation with Pip
- Code formatting with [Black](https://black.readthedocs.io/en/stable/) and [isort](https://github.com/PyCQA/isort)
- Testing with [pytest](https://docs.pytest.org/en/6.2.x/getting-started.html)
