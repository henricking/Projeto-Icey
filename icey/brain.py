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

    def responder(self, texto, ao_receber=None):
        """Devolve a resposta completa, ou None se o servidor falhar.

        Se ao_receber for dado, é chamado a cada pedaço de texto recebido.
        """
        self.historico.append({"role": "user", "content": texto})
        mensagens = (
            [{"role": "system", "content": personality.SYSTEM_PROMPT}]
            + personality.EXEMPLOS
            + self.historico
        )
        corpo = json.dumps(
            {
                "messages": mensagens,
                "max_tokens": 100,
                "temperature": 0.45,
                "repeat_penalty": 1.08,
                "top_p": 0.85,
                "stream": True,
            }
        ).encode("utf-8")
        pedido = urllib.request.Request(
            self.url, data=corpo, headers={"Content-Type": "application/json"}
        )
        partes = []
        try:
            with urllib.request.urlopen(pedido, timeout=120) as r:
                for linha in r:
                    linha = linha.decode("utf-8").strip()
                    if not linha.startswith("data:"):
                        continue
                    dado = linha[5:].strip()
                    if dado == "[DONE]":
                        break
                    delta = json.loads(dado)["choices"][0]["delta"]
                    trecho = delta.get("content") or ""
                    if trecho:
                        partes.append(trecho)
                        if ao_receber:
                            ao_receber(trecho)
        except (OSError, ValueError, KeyError, IndexError):
            self.historico.pop()
            return None
        resposta = "".join(partes).strip()
        if not resposta:
            self.historico.pop()
            return None
        self.historico.append({"role": "assistant", "content": resposta})
        self.historico = self.historico[-MAX_MENSAGENS:]
        return resposta
