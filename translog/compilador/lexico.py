"""Analizador léxico: reconoce lexemas con los AFD (coincidencia más larga)."""
from dataclasses import dataclass

DELIMITADORES = set(" \t-:")


@dataclass
class Token:
    tipo: str
    lexema: str
    col: int


def tokenizar(linea, afds, prioridad):
    """afds: {nombre: AFD}; prioridad: nombres en orden. Devuelve lista de Token.
    Si ningún AFD reconoce el texto se emite un token ERROR con el lexema inválido."""
    toks, i = [], 0
    while i < len(linea):
        if linea[i] in " \t":
            i += 1
            continue
        mejor, tipo = 0, None
        for nombre in prioridad:
            n = afds[nombre].mas_largo(linea, i)
            if n > mejor:
                mejor, tipo = n, nombre
        if tipo:
            toks.append(Token(tipo, linea[i:i + mejor], i + 1))
            i += mejor
        else:
            j = i + 1
            while j < len(linea) and linea[j] not in DELIMITADORES:
                j += 1
            toks.append(Token("ERROR", linea[i:j], i + 1))
            i = j
    return toks
