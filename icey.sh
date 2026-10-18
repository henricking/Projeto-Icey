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

# Tema da Icey: só vale enquanto ela estiver aberta.
tema_ligar() { printf '\033]11;#06181d\007\033]10;#d3e4e9\007'; }
tema_desligar() { printf '\033]111\007\033]110\007\033[0m'; }
ciano() { printf '\033[38;2;39;211;224m%s\033[0m\n' "$1"; }

limpar() {
  if [ -n "$PID" ]; then
    kill "$PID" 2>/dev/null
  fi
  tema_desligar
}
trap limpar EXIT
trap 'exit 130' INT TERM HUP

cd "$DIR" || exit 1
tema_ligar
clear
python -m icey.visual
echo

if ! curl -sf "$URL" >/dev/null 2>&1; then
  ciano "Ligando o cérebro da Icey..."
  llama-server -m "$MODELO" -c 1024 -t 4 --port 8080 \
    >"$HOME/llama-server.log" 2>&1 &
  PID=$!
  for i in $(seq 1 120); do
    curl -sf "$URL" >/dev/null 2>&1 && break
    if ! kill -0 "$PID" 2>/dev/null; then
      echo "O servidor caiu. Veja o arquivo ~/llama-server.log"
      PID=""
      exit 1
    fi
    sleep 1
  done
  ciano "Pronta."
  echo
fi

python -m icey.main
