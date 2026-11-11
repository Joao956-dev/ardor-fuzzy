"""Gera as figuras dos slides 12 e 13 a partir de dados/estatisticas.json e dados/diario_2024.json."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(B, "dados", "diario_2024.json"), encoding="utf8"))
ST = json.load(open(os.path.join(B, "dados", "estatisticas.json"), encoding="utf8"))
COR = ["#2e7d4f", "#b8860b", "#d4621a", "#b3261e", "#6b2c7a"]
INK, MUT, BG = "#17313b", "#5c7078", "#ffffff"
plt.rcParams.update({"font.family": "Arial", "font.size": 20, "axes.edgecolor": MUT, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})
LIM = [0, 25, 45, 65, 82, 100]
MID = [(LIM[i] + LIM[i + 1]) / 2 for i in range(5)]
NOM = ["baixa", "moderada", "alta", "muito alta", "crítica"]

# --- f7: diário IQAr x carga ARDOR
x = [date.fromisoformat(d["data"]) for d in D]
fig, ax = plt.subplots(figsize=(16, 6.2), dpi=150); fig.patch.set_facecolor(BG)
for i in range(5):
    ax.axhspan(LIM[i], LIM[i + 1], color=COR[i], alpha=0.07, lw=0)
ax.step(x, [MID[d["n_iqar"]] for d in D], where="mid", color=MUT, lw=2.4, label="IQAr (só fumaça), nível")
ax.scatter(x, [d["carga"] for d in D], c=[COR[d["n_carga"]] for d in D], s=26, zorder=3, label="ARDOR carga ambiental (fumaça + calor)")
ax.set_ylim(0, 100); ax.set_xlim(x[0], x[-1])
ax.set_yticks(MID); ax.set_yticklabels(NOM)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=15)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.set_xticklabels(["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"])
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(loc="upper left", frameon=False, fontsize=19)
fig.tight_layout(); fig.savefig(os.path.join(B, "figuras", "f7_slide_iqar_x_ardor.png"), facecolor=BG); plt.close(fig)

# --- f8: horas seguras por mês (12 meses)
jn = ST["janela_segura_crianca_h"]; M = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
v = [jn[str(m)] for m in range(1, 13)]
fig, ax = plt.subplots(figsize=(16, 6.4), dpi=150); fig.patch.set_facecolor(BG)
cores = ["#c86135" if m >= 9 else "#258b89" for m in range(1, 13)]
b = ax.bar(M, v, color=cores, width=0.68)
for r, val in zip(b, v):
    ax.text(r.get_x() + r.get_width() / 2, val + 0.25, f"{val:.1f}".replace(".", ",") + " h", ha="center", va="bottom", fontsize=21, fontweight="bold", color=INK)
ax.set_ylim(0, 12.5); ax.set_ylabel("horas seguras por dia (7h–17h)", fontsize=20)
ax.set_yticks([0, 2, 4, 6, 8, 10])
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(B, "figuras", "f8_slide_horas_seguras.png"), facecolor=BG); plt.close(fig)
print("ok")
