"""Gráficos SVG generados por código (no son imágenes): autómatas y árbol de derivación."""
import itertools
import math
from html import escape

R, DX, DY, M = 19, 92, 58, 28
_ids = itertools.count()


def _capas(n, arcos, inicio):
    ady = {i: [] for i in range(n)}
    for a, _, b in arcos:
        if b not in ady[a]:
            ady[a].append(b)
    estado, orden, back = {}, [], set()

    def dfs(u):
        estado[u] = 1
        for v in ady[u]:
            if estado.get(v) == 1:
                back.add((u, v))
            elif v not in estado:
                dfs(v)
        estado[u] = 2
        orden.append(u)

    dfs(inicio)
    capa = {u: 0 for u in orden}
    for u in reversed(orden):
        for v in ady[u]:
            if (u, v) not in back:
                capa[v] = max(capa[v], capa[u] + 1)
    return capa


def svg_automata(n, arcos, inicio, finales, titulo, pref="q"):
    """arcos: lista de (origen, etiqueta, destino). Etiqueta None/'' = epsilon."""
    uid = f"m{next(_ids)}"
    capa = _capas(n, arcos, inicio)
    por_capa = {}
    for u, c in capa.items():
        por_capa.setdefault(c, []).append(u)
    y = {}
    for c in sorted(por_capa):
        def clave(u):
            ys = [y[a] for a, _, b in arcos if b == u and a in y and capa[a] < c]
            return sum(ys) / len(ys) if ys else 0
        nodos = sorted(por_capa[c], key=clave)
        for i, u in enumerate(nodos):
            y[u] = (i - (len(nodos) - 1) / 2) * DY
    ymin, ymax = min(y.values()), max(y.values())
    pos = {u: (M + 20 + capa[u] * DX, M + (y[u] - ymin)) for u in y}
    W = M * 2 + 20 + max(capa.values()) * DX
    H = M * 2 + (ymax - ymin) + 30

    agrupados = {}
    for a, lab, b in arcos:
        agrupados.setdefault((a, b), []).append(lab or "ε")
    partes = [f'<svg class="grafo" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{escape(titulo)}" '
              f'width="{W:.0f}" height="{H:.0f}"><defs><marker id="{uid}" viewBox="0 0 10 10" refX="9" refY="5" '
              f'markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="g-flecha"/>'
              f'</marker></defs>']
    # flecha de entrada
    x0, y0 = pos[inicio]
    partes.append(f'<line class="g-arco" x1="{x0 - R - 24}" y1="{y0}" x2="{x0 - R}" y2="{y0}" marker-end="url(#{uid})"/>')
    for (a, b), labs in agrupados.items():
        lab = escape(", ".join(labs))
        xa, ya = pos[a]
        xb, yb = pos[b]
        if a == b:
            partes.append(f'<path class="g-arco" d="M{xa - 9},{ya - R + 2} C{xa - 30},{ya - R - 38} {xa + 30},{ya - R - 38} {xa + 9},{ya - R + 2}" marker-end="url(#{uid})"/>')
            partes.append(f'<text class="g-lbl" x="{xa}" y="{ya - R - 28}">{lab}</text>')
            continue
        dx, dy = xb - xa, yb - ya
        d = math.hypot(dx, dy)
        ux, uy = dx / d, dy / d
        sx, sy, ex, ey = xa + ux * R, ya + uy * R, xb - ux * R, yb - uy * R
        largo = abs(capa[b] - capa[a]) != 1 or ((b, a) in agrupados)
        if not largo:
            partes.append(f'<line class="g-arco" x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" marker-end="url(#{uid})"/>')
            lx, ly = (sx + ex) / 2 - uy * 9, (sy + ey) / 2 + ux * 9
        else:
            off = -(26 + 8 * abs(capa[b] - capa[a]))
            cx, cy = (xa + xb) / 2 - uy * off, (ya + yb) / 2 + ux * off
            partes.append(f'<path class="g-arco" d="M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}" marker-end="url(#{uid})"/>')
            lx, ly = (xa + xb) / 2 + (cx - (xa + xb) / 2) / 2, (ya + yb) / 2 + (cy - (ya + yb) / 2) / 2
        partes.append(f'<text class="g-lbl" x="{lx:.1f}" y="{ly:.1f}">{lab}</text>')
    for u, (x, yy) in pos.items():
        fin = u in finales
        if fin:
            partes.append(f'<circle class="g-nodo g-fin" cx="{x}" cy="{yy:.1f}" r="{R + 4}"/>')
        partes.append(f'<circle class="g-nodo{" g-ini" if u == inicio else ""}" cx="{x}" cy="{yy:.1f}" r="{R}"/>')
        partes.append(f'<text class="g-q" x="{x}" y="{yy + 4:.1f}">{pref}{u}</text>')
    partes.append("</svg>")
    return "".join(partes)


# ---------- árbol de derivación ----------
BW, BH, GX, GY = 104, 40, 14, 62


def svg_arbol(raiz):
    """raiz: dict {'etq', 'lex' (opcional), 'tipo' (opcional, token), 'hijos': [...]}"""
    nodos, cont = [], itertools.count()

    def pos(nd, prof):
        if not nd.get("hijos"):
            x = next(cont) * (BW + GX)
        else:
            xs = [pos(h, prof + 1) for h in nd["hijos"]]
            x = sum(xs) / len(xs)
        nd["_x"], nd["_y"] = x, prof * GY
        nodos.append(nd)
        return x

    pos(raiz, 0)
    W = max(n["_x"] for n in nodos) + BW + 2 * 10
    H = max(n["_y"] for n in nodos) + BH + 2 * 10
    p = [f'<svg class="grafo arbol" viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Árbol de derivación" width="{W:.0f}" height="{H:.0f}">']

    def lineas(nd):
        for h in nd.get("hijos", []):
            p.append(f'<line class="g-arco" x1="{nd["_x"] + BW / 2 + 10:.1f}" y1="{nd["_y"] + BH + 10}" '
                     f'x2="{h["_x"] + BW / 2 + 10:.1f}" y2="{h["_y"] + 10}"/>')
            lineas(h)

    lineas(raiz)
    for nd in nodos:
        x, yy = nd["_x"] + 10, nd["_y"] + 10
        clase = f'a-hoja t-{nd["tipo"]}' if nd.get("tipo") else "a-nt"
        p.append(f'<rect class="{clase}" x="{x:.1f}" y="{yy}" width="{BW}" height="{BH}" rx="6"/>')
        if nd.get("lex") is not None:
            p.append(f'<text class="a-t1" x="{x + BW / 2:.1f}" y="{yy + 16}">{escape(nd["etq"])}</text>')
            p.append(f'<text class="a-t2" x="{x + BW / 2:.1f}" y="{yy + 32}">«{escape(nd["lex"])}»</text>')
        else:
            p.append(f'<text class="a-t1" x="{x + BW / 2:.1f}" y="{yy + 24}">{escape(nd["etq"])}</text>')
    p.append("</svg>")
    return "".join(p)
