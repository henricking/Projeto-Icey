"""Ponto de entrada da Icey."""

from icey import personality
from icey.brain import Cerebro


def mostrar(trecho):
    print(trecho, end="", flush=True)


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
        print(f"{personality.NOME}: ", end="", flush=True)
        resposta = cerebro.responder(texto, ao_receber=mostrar)
        if resposta is None:
            print(personality.erro_servidor())
        else:
            print()
    print(f"{personality.NOME}: {personality.despedida()}")


if __name__ == "__main__":
    main()
