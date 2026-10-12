"""Minicompilador de guías de remisión - TransLog Perú S.A.C. (Flask, sin base de datos)."""
from pathlib import Path

from flask import Flask, render_template, request, send_from_directory

from compilador import AUTOMATAS, PRODUCCIONES, TOKENS, compilar

BASE = Path(__file__).parent
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024          # 1 MB
EJEMPLO = (BASE / "ejemplos" / "guias_ejemplo.txt").read_text(encoding="utf-8")


def leer_texto(form, files):
    texto = form.get("contenido", "")
    archivo = files.get("archivo")
    if not texto.strip() and archivo and archivo.filename:
        datos = archivo.read()
        for cod in ("utf-8-sig", "latin-1"):
            try:
                return datos.decode(cod)
            except UnicodeDecodeError:
                continue
    return texto


@app.route("/", methods=["GET", "POST"])
def index():
    texto, resultado = EJEMPLO, None
    if request.method == "POST":
        texto = leer_texto(request.form, request.files)
        resultado = compilar(texto)
    return render_template("index.html", texto=texto, r=resultado, tokens=TOKENS,
                           automatas=AUTOMATAS, producciones=PRODUCCIONES)


@app.route("/ejemplo.txt")
def ejemplo():
    return send_from_directory(BASE / "ejemplos", "guias_ejemplo.txt", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
