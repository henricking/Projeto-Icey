"""Cérebro da Icey: conversa com o modelo local (llama-server)."""

import json
import urllib.request

from icey import personality
from icey.memory import Memoria, vale_guardar
from icey.perfil import Perfil

URL = "http://127.0.0.1:8080/v1/chat/completions"
MAX_MENSAGENS = 6


class Cerebro:
    def __init__(self, url=URL):
        self.url = url
        self.historico = []
        self.memoria = Memoria()
        self.perfil = Perfil()

    def _sistema(self, texto):
        sistema = personality.SYSTEM_PROMPT + (
            " Quem fala com você é o USUÁRIO, uma pessoa real. "
            "Quando ele diz 'eu' ou 'meu', fala dele mesmo, nunca de você."
        )
        fatos = self.perfil.como_texto()
        if fatos:
            sistema += "\n\nFatos confirmados sobre o usuário:\n" + fatos
        lembrancas = self.memoria.buscar(texto)
        if lembrancas:
            itens = "\n".join(f'- O usuário disse: "{m}"' for m in lembrancas)
            sistema += (
                "\n\nCoisas que o usuário disse antes. "
                "Use só se forem relevantes:\n" + itens
            )
        return sistema

    def responder(self, texto, ao_receber=None):
        """Devolve a resposta completa, ou None se o servidor falhar."""
        direta = self.perfil.responder_direto(texto)
        if direta:
            if ao_receber:
                ao_receber(direta)
            self.historico.append({"role": "user", "content": texto})
            self.historico.append({"role": "assistant", "content": direta})
            self.historico = self.historico[-MAX_MENSAGENS:]
            return direta

        aprendeu = self.perfil.aprender(texto)
        if aprendeu:
            itens = ", ".join(f"{r[1]}: {r[2]}" for r in aprendeu)
            resposta = f"Anotado no seu perfil ({itens})."
            if ao_receber:
                ao_receber(resposta)
            self.historico.append({"role": "user", "content": texto})
            self.historico.append({"role": "assistant", "content": resposta})
            self.historico = self.historico[-MAX_MENSAGENS:]
            return resposta
        sistema = self._sistema(texto)
        self.historico.append({"role": "user", "content": texto})
        mensagens = (
            [{"role": "system", "content": sistema}]
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
        if not aprendeu and vale_guardar(texto):
            self.memoria.salvar(texto, "conversa")
        return resposta
