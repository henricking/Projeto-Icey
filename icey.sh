#!/data/data/com.termux/files/usr/bin/bash
# Liga o cérebro da Icey, abre a conversa e desliga ao sair.

DIR="$(dirname "$(readlink -f "$0")")"
MODELO="${ICEY_MODELO:-$HOME/modelos/qwen2.5-1.5b.gguf}"
URL="http://127.0.0.1:8080/health"
PID=""

if [ ! -f "$MODELO" ]; then
  echo "Modelo não encontrado: $MODELO"
  exit 1
fi

if ! curl -sf "$URL" >/dev/null 2>&1; then
  echo "Ligando o cérebro da Icey..."
  llama-server -m "$MODELO" -c 1024 -t 4 --port 8080 \
    >"$HOME/llama-server.log" 2>&1 &
  PID=$!
  for i in $(seq 1 120); do
    curl -sf "$URL" >/dev/null 2>&1 && break
    if ! kill -0 "$PID" 2>/dev/null; then
      echo "O servidor caiu. Veja o arquivo ~/llama-server.log"
      exit 1
    fi
    sleep 1
  done
fi

cd "$DIR" && python -m icey.main

if [ -n "$PID" ]; then
  kill "$PID" 2>/dev/null
fi
