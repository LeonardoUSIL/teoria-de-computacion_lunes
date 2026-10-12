"""Etapa 2 - ER -> AFND (Thompson) -> AFD (construcción de subconjuntos)."""
from dataclasses import dataclass


def fmt(chars):
    """{'0',...,'9'} -> '0-9'; {'1','3',...,'9'} -> '1,3-9'."""
    cs = sorted(chars, key=ord)
    partes, i = [], 0
    while i < len(cs):
        j = i
        while j + 1 < len(cs) and ord(cs[j + 1]) == ord(cs[j]) + 1:
            j += 1
        if j - i >= 2:
            partes.append(f"{cs[i]}-{cs[j]}")
        else:
            partes.extend(cs[i:j + 1])
        i = j + 1
    return ",".join(partes)


# ---------- 1. Expresión regular -> árbol sintáctico ----------
def parsear_er(er):
    pos = 0

    def peek():
        return er[pos] if pos < len(er) else None

    def eat():
        nonlocal pos
        c = er[pos]
        pos += 1
        return c

    def alt():
        ramas = [cat()]
        while peek() == "|":
            eat()
            ramas.append(cat())
        return ramas[0] if len(ramas) == 1 else ("alt", ramas)

    def cat():
        n = rep()
        while peek() not in (None, "|", ")"):
            n = ("cat", n, rep())
        return n

    def rep():
        n = atom()
        while peek() in ("*", "+", "?", "{"):
            c = eat()
            if c == "*":
                n = ("star", n)
            elif c == "+":
                n = ("plus", n)
            elif c == "?":
                n = ("opt", n)
            else:
                num = ""
                while peek() != "}":
                    num += eat()
                eat()
                n = ("rep", n, int(num))
        return n

    def atom():
        c = eat()
        if c == "(":
            n = alt()
            eat()
            return n
        if c == "[":
            s = set()
            while peek() != "]":
                a = eat()
                if peek() == "-" and er[pos + 1] != "]":
                    eat()
                    b = eat()
                    s |= {chr(x) for x in range(ord(a), ord(b) + 1)}
                else:
                    s.add(a)
            eat()
            return ("chr", frozenset(s))
        if c == "\\":
            c = eat()
        return ("chr", frozenset(c))

    return alt()


# ---------- 2. Thompson ----------
@dataclass
class AFND:
    n: int
    arcos: list      # (origen, simbolo | None, destino); None = epsilon
    inicio: int
    final: int


def thompson(ast):
    trans, cont = {}, [0]

    def nuevo():
        trans[cont[0]] = []
        cont[0] += 1
        return cont[0] - 1

    def arco(a, sym, b):
        trans[a].append((sym, b))

    def build(nd):
        t = nd[0]
        if t == "chr":
            i, f = nuevo(), nuevo()
            arco(i, nd[1], f)
            return i, f
        if t == "cat":
            i1, f1 = build(nd[1])
            i2, f2 = build(nd[2])
            trans[f1] += trans.pop(i2)      # f1 e i2 se fusionan (Aho)
            return i1, f2
        if t == "alt":
            i, f = nuevo(), nuevo()
            for r in nd[1]:
                ir, fr = build(r)
                arco(i, None, ir)
                arco(fr, None, f)
            return i, f
        if t == "rep":
            x = nd[1]
            for _ in range(nd[2] - 1):
                x = ("cat", x, nd[1])
            return build(x)
        i, f = nuevo(), nuevo()
        i1, f1 = build(nd[1])
        arco(i, None, i1)
        arco(f1, None, f)
        if t in ("star", "opt"):
            arco(i, None, f)
        if t in ("star", "plus"):
            arco(f1, None, i1)
        return i, f

    ini, fin = build(ast)
    # renumerar en BFS: q0 = inicial
    orden, vistos, cola = {}, {ini}, [ini]
    while cola:
        s = cola.pop(0)
        orden[s] = len(orden)
        for _, t in trans[s]:
            if t not in vistos:
                vistos.add(t)
                cola.append(t)
    arcos = [(orden[s], sym, orden[t]) for s in orden for sym, t in trans[s]]
    return AFND(len(orden), arcos, 0, orden[fin])


# ---------- 3. Subconjuntos ----------
@dataclass
class AFD:
    n: int
    atomos: list         # particiones del alfabeto (frozenset de caracteres)
    delta: dict          # (estado, indice_atomo) -> estado
    inicio: int
    finales: set
    subconjuntos: list   # estados del AFND que forman cada estado del AFD

    def __post_init__(self):
        self.atomo_de = {c: k for k, a in enumerate(self.atomos) for c in a}

    @property
    def alfabeto(self):
        return set().union(*self.atomos)

    def mas_largo(self, texto, pos):
        """Longitud de la cadena más larga aceptada desde pos (-1 si ninguna)."""
        est, mejor, i = self.inicio, -1, pos
        while i < len(texto):
            k = self.atomo_de.get(texto[i])
            if k is None or (est, k) not in self.delta:
                break
            est = self.delta[(est, k)]
            i += 1
            if est in self.finales:
                mejor = i - pos
        return mejor

    def arcos(self):
        """Arcos agrupados por (origen, destino) con la etiqueta fusionada."""
        agr = {}
        for (s, k), t in self.delta.items():
            agr.setdefault((s, t), set()).update(self.atomos[k])
        return [(s, fmt(c), t) for (s, t), c in sorted(agr.items())]

    def tabla(self):
        """Columnas = grupos de símbolos con idéntico comportamiento."""
        cols = {}
        for k, a in enumerate(self.atomos):
            firma = tuple(self.delta.get((s, k)) for s in range(self.n))
            cols.setdefault(firma, set()).update(a)
        orden = sorted(cols.items(), key=lambda kv: min(kv[1], key=ord))
        cab = [fmt(c) for _, c in orden]
        filas = [[firma[s] for firma, _ in orden] for s in range(self.n)]
        return cab, filas


def _cierre(trans, S):
    res, pila = set(S), list(S)
    while pila:
        s = pila.pop()
        for sym, t in trans[s]:
            if sym is None and t not in res:
                res.add(t)
                pila.append(t)
    return frozenset(res)


def a_afd(afnd):
    trans = {s: [] for s in range(afnd.n)}
    for s, sym, t in afnd.arcos:
        trans[s].append((sym, t))
    conjuntos = sorted({sym for l in trans.values() for sym, _ in l if sym}, key=fmt)
    grupos = {}
    for ch in set().union(*conjuntos):
        grupos.setdefault(tuple(ch in c for c in conjuntos), set()).add(ch)
    atomos = sorted((frozenset(g) for g in grupos.values()), key=lambda g: min(g, key=ord))

    ini = _cierre(trans, {afnd.inicio})
    ids, cola, delta = {ini: 0}, [ini], {}
    while cola:
        S = cola.pop(0)
        for k, a in enumerate(atomos):
            rep = next(iter(a))
            mov = {t for s in S for sym, t in trans[s] if sym and rep in sym}
            if not mov:
                continue
            T = _cierre(trans, mov)
            if T not in ids:
                ids[T] = len(ids)
                cola.append(T)
            delta[(ids[S], k)] = ids[T]
    finales = {i for S, i in ids.items() if afnd.final in S}
    subs = [sorted(S) for S, _ in sorted(ids.items(), key=lambda kv: kv[1])]
    return AFD(len(ids), atomos, delta, 0, finales, subs)


def construir(er):
    afnd = thompson(parsear_er(er))
    return afnd, a_afd(afnd)
