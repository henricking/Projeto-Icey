"""Ponto de entrada da Icey."""

import re

from icey import personality, visual
from icey.brain import Cerebro

ENSINAR = re.compile(r"^(lembre|aprenda|anote)(?:\s+que|:)?\s+(.+)$", re.I | re.S)


def mostrar(trecho):
    print(trecho, end="", flush=True)


def rotulo():
    return visual.cor(personality.NOME + ":", visual.CIANO, negrito=True)


def fala(texto):
    print(f"{rotulo()} {texto}")


def comando(cerebro, texto):
    """Trata comandos de memória. Devolve True se tratou."""
    if texto.lower() == "/perfil":
        itens = cerebro.perfil.todos()
        if not itens:
            fala("Ainda não sei nada sobre você.")
        for _, nome_item, valor, _ in itens:
            print(f"  {nome_item}: {valor}")
        return True
    if texto.lower() == "/memorias":
        itens = cerebro.memoria.listar()
        if not itens:
            fala("Ainda não guardei nada.")
        for id_, t, tipo in itens:
            marca = "*" if tipo == "fato" else " "
            print(f"{id_:>3}{marca} {t}")
        return True
    m = re.match(r"^/apagar\s+(.+)$", texto, re.I)
    if m:
        ok = cerebro.perfil.apagar(m.group(1))
        fala("Apagado." if ok else "Não achei isso no perfil.")
        return True
    m = re.match(r"^/esquecer\s+(\d+)$", texto, re.I)
    if m:
        ok = cerebro.memoria.apagar(int(m.group(1)))
        fala("Esquecido." if ok else "Não achei essa.")
        return True
    m = ENSINAR.match(texto)
    if m:
        conteudo = m.group(2).strip()
        achados = cerebro.perfil.aprender(conteudo)
        if achados:
            itens = ", ".join(f"{r[1]}: {r[2]}" for r in achados)
            fala(f"Anotado no seu perfil ({itens}).")
        else:
            cerebro.memoria.salvar(conteudo, "fato")
            fala("Anotado. Não vou esquecer.")
        return True
    return False


def main():
    cerebro = Cerebro()
    fala(personality.saudacao())
    while True:
        try:
            texto = input(visual.prompt_usuario()).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if texto.lower() in ("sair", "tchau"):
            break
        if not texto:
            continue
        if comando(cerebro, texto):
            continue
        print(rotulo() + " ", end="", flush=True)
        resposta = cerebro.responder(texto, ao_receber=mostrar)
        if resposta is None:
            print(personality.erro_servidor())
        else:
            print()
    fala(personality.despedida())


if __name__ == "__main__":
    main()
