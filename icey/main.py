"""Ponto de entrada da Icey."""

from icey import personality
from icey.brain import Cerebro


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
        resposta = cerebro.responder(texto)
        if resposta is None:
            resposta = personality.erro_servidor()
        print(f"{personality.NOME}: {resposta}")
    print(f"{personality.NOME}: {personality.despedida()}")


if __name__ == "__main__":
    main()
