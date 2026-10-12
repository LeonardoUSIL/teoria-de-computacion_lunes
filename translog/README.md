# Minicompilador de guías de remisión (TransLog Perú S.A.C.)

Flask, sin base de datos. Todo se procesa en memoria.

## Ejecutar
    pip install -r requirements.txt
    python app.py          # http://127.0.0.1:5000
    python -m unittest tests/test_compilador.py

## Estructura
    app.py                  rutas Flask
    compilador/tokens.py    Etapa 1: tokens, lexemas, ER, gramática
    compilador/automatas.py Etapa 2: ER -> AFND (Thompson) -> AFD (subconjuntos)
    compilador/graficos.py  gráficos SVG generados por código
    compilador/lexico.py    analizador léxico (coincidencia más larga con los AFD)
    compilador/sintactico.py analizador sintáctico y árbol de derivación
    templates/ static/      interfaz
    ejemplos/               archivo .txt de prueba

## Cambiar el lenguaje
Edita `compilador/tokens.py` (por ejemplo, agrega una sede a `SEDES`); los autómatas,
tablas y gráficos se regeneran solos.

## Publicar gratis (Vercel)
Sube la carpeta a GitHub e impórtala en Vercel: detecta `app.py` y `requirements.txt`.
