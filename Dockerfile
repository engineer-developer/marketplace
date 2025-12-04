FROM python:3.12.3

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV ENV_MODE=production

WORKDIR /app

RUN python -m pip install --upgrade pip

RUN pip install pipx

ENV PATH="/root/.local/bin:${PATH}"

RUN pipx install poetry

RUN poetry config virtualenvs.create false --local

COPY diploma-frontend/dist/ ./diploma-frontend/dist/

COPY pyproject.toml ./

RUN poetry install

COPY marketplace/ ./marketplace/

WORKDIR /app/marketplace

RUN python manage.py collectstatic --clear --no-input
