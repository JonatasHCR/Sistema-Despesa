#!/bin/sh

echo "Aguardando banco..."

# espera o postgres subir
until nc -z db 5432; do
  sleep 2
done

echo "Banco pronto!"

echo "Rodando migrations..."
alembic upgrade head

echo "Subindo API..."
uvicorn main:app --host 0.0.0.0 --port 8000