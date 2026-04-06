FROM python:3.12.12-slim

WORKDIR /backend

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .

COPY alembic ./alembic

COPY . .

EXPOSE 8000

COPY migrations.sh .

RUN chmod +x migrations.sh

CMD ["./migrations.sh"]