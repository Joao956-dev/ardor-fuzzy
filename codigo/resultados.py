"""Roda o ARDOR sobre 2024 inteiro em Maraba-PA e gera estatisticas, figuras e dados para a web."""
import json, os, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm
import ardor as A

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(BASE, "figuras")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 150})
COR = ["#2e7d32", "#f9a825", "#ef6c00", "#c62828", "#6a1b9a"]
NOMES = ["Baixo", "Moderado", "Alto", "Muito alto", "Crítico"]

aq = json.load(open(os.path.join(BASE, "dados", "aq.json")))["hourly"]
wx = json.load(open(os.path.join(BASE, "dados", "wx.json")))["hourly"]
H = [(t, p, T, U) for t, p, T, U in zip(aq["time"], aq["pm2_5"], wx["temperature_2m"],
                                         wx["relative_humidity_2m"]) if None not in (p, T, U)]
print("horas validas:", len(H))

PERFIS = {"adulto": (1, 2), "crianca": (5, 6), "sensivel": (8.5, 5)}

# ------------------------------------------------------------ diario
dias = collections.OrderedDict()
for t, p, T, U in H:
    d = dias.setdefault(t[:10], {"pm": [], "tarde": []})
    d["pm"].append(p)
    if 10 <= int(t[11:13]) <= 16:
        d["tarde"].append((A.indice_calor_noaa(T, U), T, U))
D = []
for k, v in dias.items():
    pm = float(np.mean(v["pm"]))
    hi, T, U = max(v["tarde"])
    calor = A.FIS1.inferir({"T": T, "UR": U})
    carga = A.FIS2.inferir({"PM25": pm, "calor": calor})
    reg = {"data": k, "pm": round(pm, 1), "T": T, "UR": U, "ic": round(hi, 1), "calor": round(calor, 2),
           "carga": round(carga, 1), "n_iqar": A.nivel_iqar(pm), "n_ic": A.nivel_calor_noaa(hi)}
    for nome, (vu, es) in PERFIS.items():
        reg["r_" + nome] = round(A.FIS3.inferir({"carga": carga, "vuln": vu, "esforco": es}), 1)
    reg["n_carga"] = A.nivel_risco(carga)
    reg["n_so_fumaca"] = A.nivel_risco(A.FIS2.inferir({"PM25": pm, "calor": 0}))
    reg["n_so_calor"] = A.nivel_risco(A.FIS2.inferir({"PM25": 0, "calor": calor}))
    D.append(reg)

N = len(D)
st = {}
st["dias"] = N
st["pm_oms"] = sum(d["pm"] > 15 for d in D)
st["ic_cautela"] = sum(d["ic"] >= 32 for d in D)
st["ambos"] = sum(d["pm"] > 15 and d["ic"] >= 32 for d in D)
st["sinergia"] = sum(d["n_carga"] > max(d["n_so_fumaca"], d["n_so_calor"]) for d in D)
st["subestimados_iqar"] = sum(d["n_carga"] > d["n_iqar"] for d in D)
st["iqar_boa_mod_mas_carga_alta"] = sum(d["n_iqar"] <= 1 and d["n_carga"] >= 2 for d in D)
for nome in PERFIS:
    st["dist_" + nome] = [sum(A.nivel_risco(d["r_" + nome]) == i for d in D) for i in range(5)]
st["dist_iqar"] = [sum(d["n_iqar"] == i for d in D) for i in range(5)]
st["dist_carga"] = [sum(d["n_carga"] == i for d in D) for i in range(5)]
st["pm_mes"] = {}
for m in range(1, 13):
    ds = [d for d in D if int(d["data"][5:7]) == m]
    st["pm_mes"][m] = round(float(np.mean([d["pm"] for d in ds])), 1)
st["pior_dia"] = max(D, key=lambda d: d["carga"])

# ------------------------------------------------------------ validacao do FIS-1 contra o Heat Index
cal = np.array([A.FIS1.inferir({"T": T, "UR": U}) for _, _, T, U in H[::3]])
hic = np.array([A.indice_calor_noaa(T, U) for _, _, T, U in H[::3]])
st["r_pearson_fis1_hi"] = round(float(np.corrcoef(cal, hic)[0, 1]), 3)
rk = lambda a: np.argsort(np.argsort(a))
st["r_spearman_fis1_hi"] = round(float(np.corrcoef(rk(cal), rk(hic))[0, 1]), 3)

# ------------------------------------------------------------ horario (perfil crianca)
mapa = np.full((12, 24), np.nan)
acc = collections.defaultdict(list)
janela = collections.defaultdict(lambda: collections.defaultdict(int))
pm_roll = []
for i, (t, p, T, U) in enumerate(H):
    pm_roll.append(p)
    pm24 = float(np.mean(pm_roll[-24:]))
    r = A.avaliar(T, U, pm24, *PERFIS["crianca"])["risco"]
    m, h = int(t[5:7]), int(t[11:13])
    acc[(m, h)].append(r)
    if 7 <= h <= 17 and r < 45:
        janela[m][t[:10]] += 1
for (m, h), v in acc.items():
    mapa[m - 1, h] = np.mean(v)
st["janela_segura_crianca_h"] = {m: round(float(np.mean([janela[m].get(d["data"], 0) for d in D
                                                          if int(d["data"][5:7]) == m])), 1) for m in range(1, 13)}

# ------------------------------------------------------------ sensibilidade (erro de sensor)
def cat(d, fpm=1.0, dT=0.0):
    c = A.FIS1.inferir({"T": d["T"] + dT, "UR": d["UR"]})
    g = A.FIS2.inferir({"PM25": d["pm"] * fpm, "calor": c})
    return A.nivel_risco(A.FIS3.inferir({"carga": g, "vuln": 5, "esforco": 6}))
base = [cat(d) for d in D]
sens = {}
for rot, kw in [("PM -20%", {"fpm": .8}), ("PM +20%", {"fpm": 1.2}), ("T -1C", {"dT": -1}), ("T +1C", {"dT": 1})]:
    alt = [cat(d, **kw) for d in D]
    sens[rot] = {"iguais": round(100 * float(np.mean([a == b for a, b in zip(alt, base)])), 1),
                 "max_salto": int(max(abs(a - b) for a, b in zip(alt, base)))}
st["sensibilidade"] = sens

json.dump(st, open(os.path.join(BASE, "dados", "estatisticas.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump(D, open(os.path.join(BASE, "dados", "diario_2024.json"), "w", encoding="utf8"), ensure_ascii=False)
for k, v in st.items():
    print(k, v)

# ============================================================ FIGURAS
def salvar(nome):
    plt.tight_layout(); plt.savefig(os.path.join(FIG, nome), dpi=300, bbox_inches="tight"); plt.close()

# F1 arquitetura
fig, ax = plt.subplots(figsize=(7.2, 2.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
def caixa(x, y, w, h, txt, cor, fs=8):
    ax.add_patch(plt.Rectangle((x, y), w, h, fc=cor, ec="#333", lw=.8, zorder=2))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, zorder=3)
def seta(x1, y1, x2, y2):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="->", lw=1, color="#333"))
caixa(0, 3.0, 1.6, .7, "Temperatura", "#fff3e0"); caixa(0, 2.1, 1.6, .7, "Umidade", "#e3f2fd")
caixa(2.2, 2.3, 1.7, 1.2, "FIS-1\nEstresse\ntérmico\n(12 regras)", "#ffe0b2")
caixa(0, 1.0, 1.6, .7, "PM2.5 (fumaça)", "#eceff1")
caixa(4.5, 1.2, 1.7, 1.5, "FIS-2\nCarga\nambiental\n(20 regras)", "#ffccbc")
caixa(4.5, .05, 1.7, .55, "Vulnerab. / Esforço", "#e8f5e9", 7)
caixa(6.8, .6, 1.5, 1.6, "FIS-3\nRisco\npessoal\n(45 regras)", "#ef9a9a")
caixa(8.7, .9, 1.3, 1.0, "Risco 0-100\n+ conduta", "#c8e6c9")
seta(1.6, 3.35, 2.2, 3.1); seta(1.6, 2.45, 2.2, 2.7); seta(3.9, 2.9, 4.5, 2.3); seta(1.6, 1.35, 4.5, 1.6)
seta(6.2, 1.95, 6.8, 1.6); seta(6.2, .32, 6.8, .9); seta(8.3, 1.4, 8.7, 1.4)
salvar("f1_arquitetura.png")

# F2 funcoes de pertinencia
fig, axs = plt.subplots(2, 3, figsize=(7.2, 4.2))
for ax, (v, tit) in zip(axs.flat, [(A.T, "Temperatura (°C)"), (A.UR, "Umidade relativa (%)"), (A.PM, "PM2.5 24 h (µg/m³)"),
                                   (A.CALOR, "Estresse térmico (0-10)"), (A.CARGA, "Carga ambiental (0-100)"), (A.RISCO, "Risco pessoal (0-100)")]):
    for j, t in enumerate(v.termos):
        ax.plot(v.u, v.mf_u(t), lw=1.4, color=(COR + ["#1565c0"])[j % 6], label=t.replace("_", " "))
    ax.set_title(tit, fontsize=8.5); ax.set_ylim(0, 1.08); ax.legend(fontsize=6, frameon=False, loc="center right")
    if v is A.PM:
        for b in (15, 50, 75, 125):
            ax.axvline(b, ls=":", c="gray", lw=.7)
salvar("f2_pertinencia.png")

# F3 superficies de controle
fig = plt.figure(figsize=(7.2, 3.2))
for k, (fis, vx, vy, nx, ny, nz, lab) in enumerate([
        (A.FIS1, A.T, A.UR, "T", "UR", "Estresse térmico", ("T (°C)", "UR (%)")),
        (A.FIS2, A.PM, A.CALOR, "PM25", "calor", "Carga ambiental", ("PM2.5 (µg/m³)", "Estresse térmico"))]):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    xs = np.linspace(vx.lo, vx.hi if vx is not A.PM else 160, 31); ys = np.linspace(vy.lo, vy.hi, 31)
    X, Y = np.meshgrid(xs, ys)
    Z = np.vectorize(lambda a, b: fis.inferir({nx: a, ny: b}))(X, Y)
    ax.plot_surface(X, Y, Z, cmap=cm.inferno_r, lw=0, antialiased=True)
    ax.set_xlabel(lab[0], fontsize=7); ax.set_ylabel(lab[1], fontsize=7); ax.set_zlabel(nz, fontsize=7)
    ax.tick_params(labelsize=6); ax.view_init(28, -125)
salvar("f3_superficies.png")

# F4 serie temporal 2024
import datetime as dt
x = [dt.date.fromisoformat(d["data"]) for d in D]
fig, axs = plt.subplots(3, 1, figsize=(7.2, 4.6), sharex=True)
axs[0].plot(x, [d["pm"] for d in D], c="#546e7a", lw=.9); axs[0].axhline(15, c="#2e7d32", ls="--", lw=.8)
axs[0].axhline(50, c="#ef6c00", ls="--", lw=.8); axs[0].set_ylabel("PM2.5\n(µg/m³)")
axs[0].text(x[5], 17, "OMS 15", fontsize=6, color="#2e7d32")
axs[1].plot(x, [d["ic"] for d in D], c="#e65100", lw=.9); axs[1].axhline(32, c="gray", ls="--", lw=.8)
axs[1].axhline(41, c="#c62828", ls="--", lw=.8); axs[1].set_ylabel("Índice de\ncalor (°C)")
axs[2].scatter(x, [d["carga"] for d in D], c=[COR[d["n_carga"]] for d in D], s=5)
axs[2].plot(x, [d["n_iqar"] * 20 + 10 for d in D], c="k", lw=.6, alpha=.6, label="IQAr (nível×20)")
axs[2].set_ylabel("Carga\nARDOR"); axs[2].legend(fontsize=6, frameon=False, loc="upper left")
salvar("f4_serie_2024.png")

# F5 mapa hora x mes (crianca)
fig, ax = plt.subplots(figsize=(7.2, 2.8))
im = ax.imshow(mapa, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=100)
ax.set_yticks(range(12)); ax.set_yticklabels(["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"], fontsize=7)
ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels([f"{h}h" for h in range(0, 24, 2)], fontsize=7)
plt.colorbar(im, ax=ax, label="Risco médio (criança, ed. física)")
salvar("f5_mapa_hora_mes.png")

# F6 distribuicao de niveis
fig, ax = plt.subplots(figsize=(7.2, 2.6))
series = [("IQAr (só fumaça)", st["dist_iqar"]), ("ARDOR carga ambiental", st["dist_carga"]),
          ("ARDOR adulto, leve", st["dist_adulto"]), ("ARDOR criança, ed. física", st["dist_crianca"]),
          ("ARDOR sensível, ativ. moderada", st["dist_sensivel"])]
for i, (rot, dist) in enumerate(series):
    esq = 0
    for j, n in enumerate(dist):
        ax.barh(i, n, left=esq, color=COR[j], label=NOMES[j] if i == 0 else None); esq += n
ax.set_yticks(range(len(series))); ax.set_yticklabels([s[0] for s in series], fontsize=7)
ax.invert_yaxis(); ax.set_xlabel("dias de 2024"); ax.legend(ncol=5, fontsize=6, frameon=False, loc="lower center", bbox_to_anchor=(.5, 1))
salvar("f6_distribuicao.png")
print("figuras ok")
