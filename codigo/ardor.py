"""
ARDOR - Avaliacao de Risco Difuso para Ondas de calor e fumaca (Maraba-PA)
Motor fuzzy Mamdani hierarquico implementado do zero (numpy).

Hierarquia:
  FIS-1  Temperatura x Umidade            -> Estresse termico (0-10)
  FIS-2  PM2.5 x Estresse termico         -> Carga ambiental (0-100)
  FIS-3  Carga x Vulnerabilidade x Esforco -> Risco pessoal (0-100)

Operadores: AND = minimo, implicacao = minimo (corte), agregacao = maximo,
defuzzificacao = centroide.
Autores: Joao Vitor Barros e Luiz Antonio Machado - UNIFESSPA, 2026.
"""
import numpy as np


# ---------------------------------------------------------------- funcoes de pertinencia
def trap(x, a, b, c, d):
    """Trapezio (a<=b<=c<=d). a==b ou c==d geram ombros."""
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    if b > a:
        m = (x > a) & (x < b)
        y[m] = (x[m] - a) / (b - a)
    y[(x >= b) & (x <= c)] = 1.0
    if d > c:
        m = (x > c) & (x < d)
        y[m] = (d - x[m]) / (d - c)
    if a == b:
        y[x <= b] = 1.0  # ombro esquerdo
    if c == d:
        y[x >= c] = 1.0  # ombro direito
    return y


def tri(x, a, b, c):
    return trap(x, a, b, b, c)


class Var:
    """Variavel linguistica: universo + termos {nome: (tipo, params)}."""

    def __init__(self, nome, lo, hi, termos, n=501):
        self.nome, self.lo, self.hi = nome, lo, hi
        self.termos = termos
        self.u = np.linspace(lo, hi, n)

    def mf(self, termo, x):
        tipo, p = self.termos[termo]
        x = np.clip(x, self.lo, self.hi)
        return float(trap(np.array([x]), *p)[0]) if tipo == "trap" else float(tri(np.array([x]), *p)[0])

    def mf_u(self, termo):
        tipo, p = self.termos[termo]
        return trap(self.u, *p) if tipo == "trap" else tri(self.u, *p)

    def fuzzificar(self, x):
        return {t: self.mf(t, x) for t in self.termos}


class Mamdani:
    def __init__(self, entradas, saida, regras):
        self.entradas, self.saida, self.regras = entradas, saida, regras

    def inferir(self, valores, detalhar=False):
        graus = {v.nome: v.fuzzificar(valores[v.nome]) for v in self.entradas}
        agregado = np.zeros_like(self.saida.u)
        ativ = []
        for antecedentes, consequente in self.regras:
            forca = min(graus[var][termo] for var, termo in antecedentes.items())
            if forca > 0:
                agregado = np.maximum(agregado, np.minimum(forca, self.saida.mf_u(consequente)))
                ativ.append((forca, antecedentes, consequente))
        if agregado.sum() == 0:
            y = (self.saida.lo + self.saida.hi) / 2
        else:
            y = float((agregado * self.saida.u).sum() / agregado.sum())
        if detalhar:
            return y, graus, sorted(ativ, key=lambda r: -r[0]), agregado
        return y


# ---------------------------------------------------------------- FIS-1: estresse termico
T = Var("T", 15, 45, {
    "amena":       ("trap", (15, 15, 25, 29)),
    "quente":      ("tri",  (26, 30.5, 34)),
    "muito_quente": ("tri", (32, 35.5, 39)),
    "extrema":     ("trap", (37, 40, 45, 45)),
})
UR = Var("UR", 10, 100, {
    "seca":     ("trap", (10, 10, 30, 45)),
    "moderada": ("tri",  (35, 55, 75)),
    "umida":    ("trap", (65, 80, 100, 100)),
})
CALOR = Var("calor", 0, 10, {
    "baixo":    ("trap", (0, 0, 1.5, 3.5)),
    "moderado": ("tri",  (2, 4, 6)),
    "alto":     ("tri",  (4.5, 6.5, 8.5)),
    "extremo":  ("trap", (7, 9, 10, 10)),
})
_m1 = {  # linhas: T ; colunas: seca, moderada, umida
    "amena":        ("baixo",    "baixo",    "baixo"),
    "quente":       ("baixo",    "moderado", "alto"),
    "muito_quente": ("moderado", "alto",     "extremo"),
    "extrema":      ("alto",     "extremo",  "extremo"),
}
R1 = [({"T": t, "UR": u}, c) for t, linha in _m1.items() for u, c in zip(("seca", "moderada", "umida"), linha)]
FIS1 = Mamdani([T, UR], CALOR, R1)

# ---------------------------------------------------------------- FIS-2: carga ambiental
# Faixas de PM2.5 (media 24 h, ug/m3) ancoradas no IQAr do MMA (Res. CONAMA 506/2024, jan/2025);
# os pontos de cruzamento (grau 0,5) ficam nos limites oficiais 15 / 50 / 75 / 125.
PM = Var("PM25", 0, 200, {
    "boa":       ("trap", (0, 0, 10, 20)),      # IQAr N1: 0-15 (guia OMS 2021)
    "moderada":  ("trap", (10, 20, 40, 58)),    # N2: >15-50
    "ruim":      ("tri",  (42, 62, 82)),        # N3: >50-75
    "muito_ruim": ("tri", (68, 100, 132)),      # N4: >75-125
    "pessima":   ("trap", (112, 138, 200, 200)),  # N5: >125
})
CALOR_IN = Var("calor", 0, 10, CALOR.termos)
CARGA = Var("carga", 0, 100, {
    "baixa":     ("trap", (0, 0, 10, 25)),
    "moderada":  ("tri",  (15, 32, 50)),
    "alta":      ("tri",  (40, 55, 70)),
    "muito_alta": ("tri", (60, 75, 90)),
    "critica":   ("trap", (80, 92, 100, 100)),
})
_m2 = {  # linhas: PM ; colunas: calor baixo, moderado, alto, extremo  (sinergia nas diagonais)
    "boa":        ("baixa",      "baixa",      "moderada",   "alta"),
    "moderada":   ("moderada",   "moderada",   "alta",       "muito_alta"),
    "ruim":       ("alta",       "alta",       "muito_alta", "critica"),
    "muito_ruim": ("muito_alta", "muito_alta", "critica",    "critica"),
    "pessima":    ("critica",    "critica",    "critica",    "critica"),
}
R2 = [({"PM25": p, "calor": c}, s) for p, linha in _m2.items()
      for c, s in zip(("baixo", "moderado", "alto", "extremo"), linha)]
FIS2 = Mamdani([PM, CALOR_IN], CARGA, R2)

# ---------------------------------------------------------------- FIS-3: risco pessoal
CARGA_IN = Var("carga", 0, 100, CARGA.termos)
VULN = Var("vuln", 0, 10, {
    "baixa": ("trap", (0, 0, 2, 4)),      # adulto saudavel
    "media": ("tri",  (2.5, 5, 7.5)),     # crianca, idoso, gestante
    "alta":  ("trap", (6, 8, 10, 10)),    # asma, DPOC, cardiopata
})
ESF = Var("esforco", 0, 10, {
    "leve":     ("trap", (0, 0, 2, 4)),   # caminhar, ficar parado
    "moderado": ("tri",  (2.5, 5, 7.5)),  # educacao fisica, trabalho manual
    "intenso":  ("trap", (6, 8, 10, 10)), # corrida, futebol, roca, obra
})
RISCO = Var("risco", 0, 100, {
    "baixo":      ("trap", (0, 0, 12, 28)),
    "moderado":   ("tri",  (18, 35, 52)),
    "alto":       ("tri",  (42, 57, 72)),
    "muito_alto": ("tri",  (62, 76, 90)),
    "critico":    ("trap", (82, 92, 100, 100)),
})
NIVEIS = ["baixo", "moderado", "alto", "muito_alto", "critico"]
_cargas = ["baixa", "moderada", "alta", "muito_alta", "critica"]
_dv = {"baixa": 0, "media": 1, "alta": 1}
_de = {"leve": -1, "moderado": 0, "intenso": 1}
R3 = []
for i, cg in enumerate(_cargas):
    for v, dv in _dv.items():
        for e, de in _de.items():
            k = i + dv + de
            if v == "alta" and i >= 2:  # grupo sensivel sofre desproporcionalmente com carga alta
                k += 1
            if i == 0:          # ar limpo e sem calor: no maximo "moderado"
                k = min(k, 1)
            if i == 4:          # carga critica: nunca abaixo de "muito alto"
                k = max(k, 3)
            R3.append(({"carga": cg, "vuln": v, "esforco": e}, NIVEIS[int(np.clip(k, 0, 4))]))
FIS3 = Mamdani([CARGA_IN, VULN, ESF], RISCO, R3)

RECOMENDACAO = [
    (25, "Liberado", "Atividade normal. Mantenha a hidratacao."),
    (45, "Atencao", "Liberado com pausas a cada 20 min, agua e sombra."),
    (65, "Reduzir", "Diminua duracao e intensidade; prefira o inicio da manha."),
    (82, "Evitar", "Evite atividade ao ar livre; leve para ambiente fechado."),
    (101, "Suspender", "Suspenda a atividade; fique em local fechado, use mascara PFF2 se sair."),
]


def recomendar(r):
    for lim, rot, txt in RECOMENDACAO:
        if r < lim:
            return rot, txt


def avaliar(temp, ur, pm25, vuln, esforco):
    c = FIS1.inferir({"T": temp, "UR": ur})
    g = FIS2.inferir({"PM25": pm25, "calor": c})
    r = FIS3.inferir({"carga": g, "vuln": vuln, "esforco": esforco})
    return {"calor": c, "carga": g, "risco": r, "rec": recomendar(r)[0]}


# ---------------------------------------------------------------- referencias de comparacao
def indice_calor_noaa(t_c, ur):
    """Heat Index (Rothfusz/NWS) em graus C."""
    f = t_c * 9 / 5 + 32
    hi = 0.5 * (f + 61 + (f - 68) * 1.2 + ur * 0.094)
    if (hi + f) / 2 >= 80:
        hi = (-42.379 + 2.04901523 * f + 10.14333127 * ur - .22475541 * f * ur - .00683783 * f * f
              - .05481717 * ur * ur + .00122874 * f * f * ur + .00085282 * f * ur * ur
              - .00000199 * f * f * ur * ur)
    return (hi - 32) * 5 / 9


def nivel_calor_noaa(hi_c):  # 0 normal,1 cautela,2 cautela extrema,3 perigo,4 perigo extremo
    return int(np.searchsorted([27, 32, 41, 54], hi_c, side="right"))


def nivel_iqar(pm):  # 0 boa ... 4 pessima (faixas MP2,5 24 h do IQAr)
    return int(np.searchsorted([15, 50, 75, 125], pm, side="right"))


def nivel_risco(r):
    return int(np.searchsorted([25, 45, 65, 82], r, side="right"))


if __name__ == "__main__":
    print("Regras:", len(R1), "+", len(R2), "+", len(R3), "=", len(R1) + len(R2) + len(R3))
    for caso in [(30, 60, 10, 1, 2), (34, 60, 35, 5, 6), (36, 55, 35, 9, 8), (28, 80, 120, 5, 5)]:
        print(caso, avaliar(*caso))
