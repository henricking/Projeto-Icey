"""Ponto de entrada da Icey."""

from icey import personality


def main():
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
        print(f"{personality.NOME}: {personality.sem_resposta()}")
    print(f"{personality.NOME}: {personality.despedida()}")


if __name__ == "__main__":
    main()
