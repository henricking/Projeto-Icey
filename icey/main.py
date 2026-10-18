"""Ponto de entrada da Icey."""

import re

from icey import personality
from icey.brain import Cerebro

ENSINAR = re.compile(r"^(lembre|aprenda|anote)(?:\s+que|:)?\s+(.+)$", re.I | re.S)


def mostrar(trecho):
    print(trecho, end="", flush=True)


def comando(cerebro, texto):
    """Trata comandos de memória. Devolve True se tratou."""
    nome = personality.NOME
    if texto.lower() == "/perfil":
        itens = cerebro.perfil.todos()
        if not itens:
            print(f"{nome}: Ainda não sei nada sobre você.")
        for _, rotulo, valor, _ in itens:
            print(f"  {rotulo}: {valor}")
        return True
    if texto.lower() == "/memorias":
        itens = cerebro.memoria.listar()
        if not itens:
            print(f"{nome}: Ainda não guardei nada.")
        for id_, t, tipo in itens:
            marca = "*" if tipo == "fato" else " "
            print(f"{id_:>3}{marca} {t}")
        return True
    m = re.match(r"^/apagar\s+(.+)$", texto, re.I)
    if m:
        ok = cerebro.perfil.apagar(m.group(1))
        print(f"{nome}: {'Apagado.' if ok else 'Não achei isso no perfil.'}")
        return True
    m = re.match(r"^/esquecer\s+(\d+)$", texto, re.I)
    if m:
        ok = cerebro.memoria.apagar(int(m.group(1)))
        print(f"{nome}: {'Esquecido.' if ok else 'Não achei essa.'}")
        return True
    m = ENSINAR.match(texto)
    if m:
        conteudo = m.group(2).strip()
        achados = cerebro.perfil.aprender(conteudo)
        if achados:
            itens = ", ".join(f"{r[1]}: {r[2]}" for r in achados)
            print(f"{nome}: Anotado no seu perfil ({itens}).")
        else:
            cerebro.memoria.salvar(conteudo, "fato")
            print(f"{nome}: Anotado. Não vou esquecer.")
        return True
    return False


def main():
    cerebro = Cerebro()
    print(f"{personality.NOME}: {personality.saudacao()}")
    while True:
        try:
            texto = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if texto.lower() in ("sair", "tchau"):
            break
        if not texto:
            continue
        if comando(cerebro, texto):
            continue
        print(f"{personality.NOME}: ", end="", flush=True)
        resposta = cerebro.responder(texto, ao_receber=mostrar)
        if resposta is None:
            print(personality.erro_servidor())
        else:
            print()
    print(f"{personality.NOME}: {personality.despedida()}")


if __name__ == "__main__":
    main()
