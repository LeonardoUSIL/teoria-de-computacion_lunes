"""Etapa 1 - Definición del lenguaje: tokens, lexemas y expresiones regulares.

Lenguaje de entrada: un código de guía de remisión por línea.
    Guia: GR-LIM-2026-000123
"""
from dataclasses import dataclass

SEDES = ["LIM", "CAL", "ATE", "SJL", "SMP", "VES"]   # sedes de TransLog (editable)


@dataclass(frozen=True)
class DefToken:
    nombre: str
    descripcion: str
    ejemplo: str
    er: str


# El orden define la prioridad cuando dos tokens reconocen la misma longitud.
TOKENS = [
    DefToken("GUIA", "Palabra clave que abre un registro de guía", "Guia", "Guia"),
    DefToken("DOS_PUNTOS", "Separador entre la palabra clave y el código", ":", ":"),
    DefToken("PREFIJO", "Prefijo del documento (Guía de Remisión)", "GR", "GR"),
    DefToken("GUION", "Separador entre los campos del código", "-", "-"),
    DefToken("SEDE", "Código de sede de tres letras", "LIM, CAL, ATE", "|".join(SEDES)),
    DefToken("ANIO", "Año de emisión de cuatro dígitos (20xx)", "2026", "20[0-9]{2}"),
    DefToken("CORRELATIVO", "Correlativo numérico de seis dígitos", "000123", "[0-9]{6}"),
]

POR_NOMBRE = {t.nombre: t for t in TOKENS}

# Gramática libre de contexto (Etapa 3)
PRODUCCIONES = [
    ("Archivo", "Linea Archivo | Linea"),
    ("Linea", "GUIA DOS_PUNTOS Codigo"),
    ("Codigo", "PREFIJO GUION SEDE GUION ANIO GUION CORRELATIVO"),
]
SECUENCIA = ["GUIA", "DOS_PUNTOS", "PREFIJO", "GUION", "SEDE", "GUION", "ANIO", "GUION", "CORRELATIVO"]

AYUDA = {
    "GUIA": "La línea debe iniciar con la palabra Guia.",
    "DOS_PUNTOS": "Falta el signo ':' después de Guia.",
    "PREFIJO": "El prefijo debe ser GR.",
    "GUION": "Los campos del código se separan con '-'.",
    "SEDE": "Sedes válidas: " + ", ".join(SEDES) + ".",
    "ANIO": "El año debe tener 4 dígitos (20xx).",
    "CORRELATIVO": "El correlativo debe tener 6 dígitos numéricos.",
}
