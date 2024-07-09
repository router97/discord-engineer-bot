FROM python:3.12.4-slim

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "bot/main.py"]