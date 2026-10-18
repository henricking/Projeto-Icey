"""Memória local da Icey (SQLite). Tudo fica no celular."""

import math
import re
import sqlite3
import unicodedata
from pathlib import Path

CAMINHO = Path(__file__).resolve().parent.parent / "data" / "memoria.db"

PARADAS = {
    "que", "com", "para", "por", "uma", "uns", "umas", "dos", "das",
    "meu", "minha", "meus", "minhas", "seu", "sua", "nos", "nas",
    "eu", "voce", "ele", "ela", "como", "mais", "mas", "foi", "sao",
    "tem", "ter", "era", "esta", "esse", "essa", "isso", "aqui",
    "ali", "dia", "ainda", "muito", "tambem", "pra", "vai", "vou",
}


def _tokens(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    saida = set()
    for p in re.findall(r"[a-z0-9]+", texto):
        if p in PARADAS:
            continue
        if len(p) < 3 and not p.isdigit():
            continue
        if len(p) > 3 and p.endswith("s"):
            p = p[:-1]
        saida.add(p)
    return saida


def vale_guardar(texto):
    """Perguntas e frases curtas demais não viram memória."""
    texto = texto.strip()
    if texto.endswith("?") or texto.startswith("/"):
        return False
    return len(texto.split()) >= 3 and len(_tokens(texto)) >= 2


class Memoria:
    def __init__(self, caminho=CAMINHO):
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(caminho))
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS memorias ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "texto TEXT NOT NULL, tipo TEXT NOT NULL, "
            "criado_em TEXT DEFAULT CURRENT_TIMESTAMP)"
        )
        self.db.commit()

    def salvar(self, texto, tipo="conversa"):
        texto = texto.strip()
        if not texto:
            return None
        achou = self.db.execute(
            "SELECT id FROM memorias WHERE texto = ?", (texto,)
        ).fetchone()
        if achou:
            return None
        cur = self.db.execute(
            "INSERT INTO memorias (texto, tipo) VALUES (?, ?)", (texto, tipo)
        )
        self.db.commit()
        return cur.lastrowid

    def buscar(self, consulta, limite=3):
        q = _tokens(consulta)
        if not q:
            return []
        linhas = self.db.execute(
            "SELECT texto, tipo FROM memorias"
        ).fetchall()
        docs = [(texto, tipo, _tokens(texto)) for texto, tipo in linhas]
        n = len(docs)
        pontuados = []
        for texto, tipo, toks in docs:
            comuns = q & toks
            if not comuns:
                continue
            score = 0.0
            for t in comuns:
                freq = sum(1 for _, _, d in docs if t in d)
                score += math.log(1 + n / freq)
            if tipo == "fato":
                score *= 1.5
            pontuados.append((score, texto))
        pontuados.sort(reverse=True)
        return [texto for _, texto in pontuados[:limite]]

    def listar(self, limite=10):
        return self.db.execute(
            "SELECT id, texto, tipo FROM memorias "
            "ORDER BY id DESC LIMIT ?", (limite,)
        ).fetchall()

    def apagar(self, id_):
        cur = self.db.execute("DELETE FROM memorias WHERE id = ?", (id_,))
        self.db.commit()
        return cur.rowcount > 0
