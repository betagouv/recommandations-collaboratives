FROM python:3-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libproj-dev gdal-bin git

WORKDIR /piptmp

COPY requirements.txt requirements-dev.txt ./

RUN pip install -r requirements.txt -r requirements-dev.txt

WORKDIR /workspace

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
