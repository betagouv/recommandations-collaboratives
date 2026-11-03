FROM python:3-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libproj-dev gdal-bin git

WORKDIR /piptmp

COPY pyproject.toml ./

RUN uv sync --no-dev

WORKDIR /workspace

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
