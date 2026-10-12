"""Analizador sintáctico (descendente predictivo) para la gramática de la guía."""
from .tokens import SECUENCIA, AYUDA


def analizar(tokens):
    """Devuelve (arbol | None, fase_error | None, motivo | None)."""
    for i, esperado in enumerate(SECUENCIA):
        if i >= len(tokens):
            return None, "Sintáctico", f"Código incompleto: falta {esperado}. {AYUDA[esperado]}"
        t = tokens[i]
        if t.tipo == "ERROR":
            return None, "Léxico", f"{esperado} inválido: «{t.lexema}» (col. {t.col}). {AYUDA[esperado]}"
        if t.tipo != esperado:
            return None, "Sintáctico", (f"Se esperaba {esperado} y se encontró {t.tipo} «{t.lexema}» "
                                        f"(col. {t.col}). {AYUDA[esperado]}")
    if len(tokens) > len(SECUENCIA):
        extra = tokens[len(SECUENCIA)]
        return None, "Sintáctico", f"Texto sobrante después del código: «{extra.lexema}» (col. {extra.col})."
    hoja = lambda t: {"etq": t.tipo, "lex": t.lexema, "tipo": t.tipo}
    codigo = {"etq": "Codigo", "hijos": [hoja(t) for t in tokens[2:]]}
    return {"etq": "Linea", "hijos": [hoja(tokens[0]), hoja(tokens[1]), codigo]}, None, None
