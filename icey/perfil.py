"""Perfil do usuário: fatos guardados em terceira pessoa (SQLite)."""

import re
import sqlite3
import unicodedata
from pathlib import Path

CAMINHO = Path(__file__).resolve().parent.parent / "data" / "memoria.db"


def _norm(texto):
    texto = unicodedata.normalize("NFD", texto.lower().strip())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def _clausulas(texto):
    partes = re.split(
        r"[,.;!]+|\s+e\s+(?=tenho\b|sou\b|meu\b|minha\b|me\b)",
        texto,
        flags=re.I,
    )
    return [p.strip() for p in partes if p and p.strip()]


def _extrair(clausula):
    """Devolve (chave, rotulo, valor, feminino) ou None."""
    c = clausula.strip()
    m = re.match(
        r"^(?:eu\s+)?(?:me\s+chamo|meu\s+nome\s+[eé])\s+(\S+)", c, re.I
    )
    if m:
        return ("nome", "nome", m.group(1).capitalize(), 0)
    m = re.match(r"^(?:eu\s+)?tenho\s+(\d{1,3})\s+anos?$", c, re.I)
    if m:
        return ("idade", "idade", m.group(1) + " anos", 0)
    m = re.match(
        r"^(?:eu\s+)?sou\s+(?:o\s+|a\s+)?(?:seu|sua)\s+(\S+)$", c, re.I
    )
    if m:
        return ("papel", "papel", m.group(1).lower() + " da Icey", 0)
    m = re.match(
        r"^(meu|minha)\s+(\S+(?:\s+\S+)?)\s+(?:se\s+chama|[eé]|s[aã]o)\s+(.+)$",
        c,
        re.I,
    )
    if m:
        rotulo = m.group(2).lower()
        valor = re.sub(r"^dia\s+", "", m.group(3).strip(), flags=re.I)
        fem = 1 if m.group(1).lower() == "minha" else 0
        return (_norm(rotulo), rotulo, valor, fem)
    return None


class Perfil:
    def __init__(self, caminho=CAMINHO):
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(caminho))
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS perfil ("
            "chave TEXT PRIMARY KEY, rotulo TEXT NOT NULL, "
            "valor TEXT NOT NULL, fem INTEGER DEFAULT 0)"
        )
        self.db.commit()

    def definir(self, chave, rotulo, valor, fem=0):
        self.db.execute(
            "INSERT OR REPLACE INTO perfil (chave, rotulo, valor, fem) "
            "VALUES (?, ?, ?, ?)",
            (chave, rotulo, valor, fem),
        )
        self.db.commit()

    def aprender(self, texto):
        """Extrai fatos de uma frase e guarda. Devolve a lista aprendida."""
        texto = texto.strip()
        if texto.endswith("?"):
            return []
        achados = []
        for c in _clausulas(texto):
            r = _extrair(c)
            if r:
                self.definir(*r)
                achados.append(r)
        return achados

    def todos(self):
        return self.db.execute(
            "SELECT chave, rotulo, valor, fem FROM perfil ORDER BY chave"
        ).fetchall()

    def apagar(self, nome):
        cur = self.db.execute(
            "DELETE FROM perfil WHERE chave = ?", (_norm(nome),)
        )
        self.db.commit()
        return cur.rowcount > 0

    def como_texto(self):
        return "\n".join(
            f"- {rotulo.capitalize()} do usuário: {valor}"
            for _, rotulo, valor, _ in self.todos()
        )

    def _dizer(self, chave):
        r = self.db.execute(
            "SELECT rotulo, valor, fem FROM perfil WHERE chave = ?", (chave,)
        ).fetchone()
        if not r:
            return "Ainda não sei isso. Pode me contar?"
        rotulo, valor, fem = r
        if chave == "nome":
            return f"Seu nome é {valor}."
        if chave == "idade":
            return f"Você tem {valor}."
        return f"{'Sua' if fem else 'Seu'} {rotulo} é {valor}."

    def responder_direto(self, texto):
        """Responde perguntas simples sobre o usuário, sem usar o modelo."""
        t = _norm(texto).strip().rstrip("?!. ").strip()
        if "," in t:
            t = t.split(",")[-1].strip()
        if len(t.split()) <= 8 and re.search(
            r"\bquem\s+(?:eu\s+sou|sou\s+eu|sou)\b", t
        ):
            nome = self.db.execute(
                "SELECT valor FROM perfil WHERE chave = 'nome'"
            ).fetchone()
            if not nome:
                return "Ainda não sei seu nome. Pode me contar?"
            papel = self.db.execute(
                "SELECT valor FROM perfil WHERE chave = 'papel'"
            ).fetchone()
            extra = f", {papel[0]}" if papel else ""
            return f"Você é {nome[0]}{extra}."
        if re.fullmatch(
            r"quantos\s+anos\s+(?:eu\s+)?tenho"
            r"|(?:eu\s+)?tenho\s+quantos\s+anos"
            r"|qual\s+(?:e\s+)?a\s+minha\s+idade",
            t,
        ):
            return self._dizer("idade")
        for padrao in (
            r"qual\s+(?:e\s+)?o\s+nome\s+d[oa]\s+(?:meu|minha)\s+(.+)",
            r"como\s+se\s+chama\s+(?:o\s+|a\s+)?(?:meu|minha)\s+(.+)",
            r"(?:qual|quais)\s+(?:e\s+|sao\s+)?(?:o\s+|a\s+|os\s+|as\s+)?"
            r"(?:meu|minha|meus|minhas)\s+(.+)",
            r"quando\s+e\s+(?:o\s+)?(?:meu|minha)\s+(.+)",
        ):
            m = re.fullmatch(padrao, t)
            if m:
                return self._dizer(m.group(1).strip())
        return None
