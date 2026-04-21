#!/bin/bash

PORT=8000

PID=$(lsof -ti:$PORT)

if [ ! -z "$PID" ]; then
    echo "🔴 Porta $PORT em uso pelo processo $PID"
    echo "⛔ Finalizando processo..."
    kill -9 $PID
    sleep 2
fi

echo "🟢 Iniciando Django..."
pdm run python src/manage.py runserver 0.0.0.0:8000