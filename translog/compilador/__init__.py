"""Minicompilador de guías de remisión (TransLog Perú S.A.C.)."""
import time
from datetime import datetime

from .automatas import construir, fmt
from .graficos import svg_automata, svg_arbol
from .lexico import tokenizar
from .sintactico import analizar
from .tokens import TOKENS, POR_NOMBRE, PRODUCCIONES

PRIORIDAD = [t.nombre for t in TOKENS]


def _preparar():
    """Se ejecuta una sola vez: ER -> AFND -> AFD y sus gráficos para cada token."""
    res = {}
    for t in TOKENS:
        afnd, afd = construir(t.er)
        cab, filas = afd.tabla()
        res[t.nombre] = {
            "def": t, "afnd": afnd, "afd": afd,
            "svg_afnd": svg_automata(afnd.n, afnd.arcos and [(a, fmt(s) if s else "", b) for a, s, b in afnd.arcos],
                                     afnd.inicio, {afnd.final}, f"AFND de {t.nombre}", "p"),
            "svg_afd": svg_automata(afd.n, afd.arcos(), afd.inicio, afd.finales, f"AFD de {t.nombre}"),
            "tabla_cab": cab, "tabla_filas": filas,
            "quintupla": {
                "Q": "{" + ", ".join(f"q{i}" for i in range(afd.n)) + "}",
                "S": "{" + fmt(afd.alfabeto) + "}",
                "q0": f"q{afd.inicio}",
                "F": "{" + ", ".join(f"q{i}" for i in sorted(afd.finales)) + "}",
            },
            "subconjuntos": [(f"q{i}", "{" + ", ".join(f"p{s}" for s in sub) + "}") for i, sub in enumerate(afd.subconjuntos)],
            "n_afnd": afnd.n, "n_afd": afd.n,
        }
    return res


AUTOMATAS = _preparar()
AFDS = {n: a["afd"] for n, a in AUTOMATAS.items()}


def compilar(texto):
    t0 = time.perf_counter()
    lineas, usados, lexemas = [], set(), []
    for nro, crudo in enumerate(texto.splitlines(), 1):
        linea = crudo.strip()
        if not linea or linea.startswith("#"):
            continue
        toks = tokenizar(linea, AFDS, PRIORIDAD)
        arbol, fase, motivo = analizar(toks)
        for tk in toks:
            if tk.tipo != "ERROR":
                usados.add(tk.tipo)
                lexemas.append({"nro": nro, "token": tk.tipo, "lexema": tk.lexema, "col": tk.col})
        lineas.append({"nro": nro, "texto": linea, "tokens": toks, "valida": arbol is not None,
                       "fase": fase, "motivo": motivo,
                       "svg_arbol": svg_arbol(arbol) if arbol else None})
    validas = sum(l["valida"] for l in lineas)
    return {
        "lineas": lineas, "lexemas": lexemas,
        "usados": [n for n in PRIORIDAD if n in usados],
        "total": len(lineas), "validas": validas, "invalidas": len(lineas) - validas,
        "ms": (time.perf_counter() - t0) * 1000,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    }
