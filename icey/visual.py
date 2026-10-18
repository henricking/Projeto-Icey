"""Identidade visual da Icey: rosto em pixel art e cores no terminal."""

import os
import shutil
import sys

RESET = "\033[0m"
CIANO = (39, 211, 224)
PRATA = (199, 210, 216)
CINZA = (120, 135, 145)

# Rosto 24x24 pixels. Cada linha de texto do terminal mostra 2 linhas
# do desenho (meio bloco), então a arte ocupa 24 colunas x 12 linhas.
ARTE = [
    "......CC........CC......",
    "......CCC......CCC......",
    "....hHHHHHHHHHHHHHHh....",
    "...hHHHHHHHHHHHHHHHHh...",
    "..hHHHHHHHHHHHHHHHHHHh..",
    ".hHHHHHHHHHHHHHHHHHHHHh.",
    "hHHHHHHHHHHHHHHHHHHHHHHh",
    "hHHHHHHHHHHHHHHHHHHHHHHh",
    "hHHHHHHHHSSSSSSHHHHHHHHh",
    "hHHHHHHHSSSSSSSSHHHHHHHh",
    "hHHHHHHSSSSSSSSSSHHHHHHh",
    "hHHHHHSccccSSccccSHHHHHh",
    "hHHHHHSCCCCSSCCCCSHHHHHh",
    "hHHHHHSCcWCSSCcWCSHHHHHh",
    "hHHHHHSSCCSSSSCCSSHHHHHh",
    "hHHHHHSSSSSSSSSSSSHHHHHh",
    "hHHHHHSSSSSSKKSSSSHHHHHh",
    "..hHHHHSSSSSSSSSSHHHHh..",
    "...hHHHBBBBBBBBBBHHHh...",
    "....hHBBBBBBBBBBBBHh....",
    "..KKKKKBBCBBBBCBBKKKKK..",
    "..KKKKKKBBBCCBBBKKKKKK..",
    ".KKKKKKKKKKKKKKKKKKKKKK.",
    "KKKKKKKKKKKKKKKKKKKKKKKK",
]

PALETA = {
    "H": (201, 211, 218),
    "h": (143, 160, 173),
    "S": (242, 220, 207),
    "C": (39, 211, 224),
    "c": (14, 143, 160),
    "K": (27, 38, 46),
    "W": (255, 255, 255),
    "B": (58, 71, 80),
}


def cor_ativa():
    if os.environ.get("ICEY_COR") == "1":
        return True
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _fg(c):
    return f"\033[38;2;{c[0]};{c[1]};{c[2]}m"


def _bg(c):
    return f"\033[48;2;{c[0]};{c[1]};{c[2]}m"


def cor(texto, rgb, negrito=False):
    """Pinta o texto, se o terminal aceitar cores."""
    if not cor_ativa():
        return texto
    negro = "\033[1m" if negrito else ""
    return f"{negro}{_fg(rgb)}{texto}{RESET}"


def prompt_usuario():
    """Prompt 'Você:' colorido, seguro para o input()."""
    if not cor_ativa():
        return "Você: "
    return f"\001{_fg(PRATA)}\002Você:\001{RESET}\002 "


def rosto():
    """Devolve as linhas do rosto, usando meio bloco (2 pixels por linha)."""
    linhas = []
    for y in range(0, len(ARTE), 2):
        cima, baixo = ARTE[y], ARTE[y + 1]
        linha = ""
        for a, b in zip(cima, baixo):
            ca, cb = PALETA.get(a), PALETA.get(b)
            if ca is None and cb is None:
                linha += " "
            elif cb is None:
                linha += _fg(ca) + "\u2580" + RESET
            elif ca is None:
                linha += _fg(cb) + "\u2584" + RESET
            elif ca == cb:
                linha += _fg(ca) + "\u2588" + RESET
            else:
                linha += _fg(ca) + _bg(cb) + "\u2580" + RESET
        linhas.append(linha)
    return linhas


def banner(versao="0.1"):
    colunas = shutil.get_terminal_size((46, 24)).columns
    titulo = "I C E Y"
    sub = f"assistente offline  v{versao}"
    if not cor_ativa():
        return f"{titulo}\n{sub}"
    margem = " " * max(0, (colunas - len(ARTE[0])) // 2)
    saida = [margem + l for l in rosto()]
    saida.append("")
    saida.append(" " * max(0, (colunas - len(titulo)) // 2)
                 + cor(titulo, CIANO, negrito=True))
    saida.append(" " * max(0, (colunas - len(sub)) // 2) + cor(sub, CINZA))
    return "\n".join(saida)


if __name__ == "__main__":
    print(banner())
