"""Cérebro da Icey: conversa com o modelo local (llama-server)."""

import json
import urllib.request

from icey import personality

URL = "http://127.0.0.1:8080/v1/chat/completions"
MAX_MENSAGENS = 6


class Cerebro:
    def __init__(self, url=URL):
        self.url = url
        self.historico = []

    def responder(self, texto):
        """Devolve a resposta da Icey, ou None se o servidor falhar."""
        self.historico.append({"role": "user", "content": texto})
        mensagens = (
            [{"role": "system", "content": personality.SYSTEM_PROMPT}]
            + personality.EXEMPLOS
            + self.historico
        )
        corpo = json.dumps(
            {"messages": mensagens, "max_tokens": 100, "temperature": 0.45, "repeat_penalty": 1.08, "top_p": 0.85}
        ).encode("utf-8")
        pedido = urllib.request.Request(
            self.url, data=corpo, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(pedido, timeout=120) as r:
                dados = json.loads(r.read().decode("utf-8"))
            resposta = dados["choices"][0]["message"]["content"].strip()
        except (OSError, ValueError, KeyError, IndexError):
            self.historico.pop()
            return None
        self.historico.append({"role": "assistant", "content": resposta})
        self.historico = self.historico[-MAX_MENSAGENS:]
        return resposta
