FROM python:3.12.9-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

#RUN useradd --create-home django
#USER django

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn

COPY --chown=django:django . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "beauty_clinic.wsgi:application"]
