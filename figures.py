"""
Draw every chart used in the slides and the README, in one consistent style.

Each chart is saved to figures/ as a "card": a white rounded panel with a soft
shadow on a transparent background, so it can be dropped straight onto a slide.
These are the only chart files in the project; the slides use exactly these.

Run:  python src/figures.py   (after clean_data.py)
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
Y = [str(y) for y in range(1990, 2020)]; YR = list(range(1990, 2020))
E, R = Y[:5], Y[-5:]
L = lambda n: pd.read_csv(CLEAN / f"{n}_wide.csv").set_index("Country")
pr, con, imp, rex = L("production")[Y], L("consumption")[Y], L("import")[Y], L("re_export")[Y]
M = 1e6

INK = "#1d1714"; MUTED = "#7a6f66"; GRID = "#ece6df"
GOLD = "#c8963e"; RED = "#b5352b"; GREEN = "#3e7b5a"; SLATE = "#5b6f86"; SAND = "#d9c3a5"; GREY = "#b9b0a6"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 15, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID,
    "grid.linewidth": 1, "lines.linewidth": 3, "xtick.major.size": 0, "ytick.major.size": 0,
})
SHORT = {"United States of America": "USA", "Russian Federation": "Russia", "United Kingdom": "UK"}
sh = lambda n: SHORT.get(n, n)


def card(fig, name, title, subtitle):
    """Draw the figure, then wrap it in a rounded white card with a soft shadow."""
    tmp = OUT / f"_{name}.png"
    fig.savefig(tmp, dpi=110, facecolor="white"); plt.close(fig)
    chart = Image.open(tmp).convert("RGBA")
    pad, head, rad, sh_off = 40, 104, 28, 18
    w, h = chart.width + pad * 2, chart.height + pad + head
    canvas = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([30, 30 + sh_off, 30 + w, 30 + h + sh_off // 2], rad, fill=(0, 0, 0, 120))
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(18)))
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle([0, 0, w - 1, h - 1], rad, fill=(255, 255, 255, 255))
    body.paste(chart, (pad, head), chart)
    d = ImageDraw.Draw(body)
    try:
        from PIL import ImageFont
        fb = ImageFont.truetype("DejaVuSans-Bold.ttf", 30); fr = ImageFont.truetype("DejaVuSans.ttf", 21)
    except OSError:
        fb = fr = None
    d.ellipse([pad, 40, pad + 16, 56], fill=GOLD)
    d.text((pad + 30, 30), title, fill=INK, font=fb)
    d.text((pad + 30, 68), subtitle, fill=MUTED, font=fr)
    canvas.alpha_composite(body, (30, 30))
    canvas.save(OUT / f"{name}.png"); tmp.unlink()
    print(f"  saved figures/{name}.png")


def endlabel(ax, x, y, text, color):
    ax.annotate(text, (x, y), xytext=(8, 0), textcoords="offset points", va="center", fontsize=15, fontweight="bold", color=color)


def bfmt(ax, unit="M"):
    ax.yaxis.set_major_formatter(lambda v, _: f"{v / 1000:g}B" if unit == "M" else f"{v:g}{unit}")


# 1. Vietnam rise
fig, ax = plt.subplots(figsize=(12, 6.2))
for c, col in [("Brazil", GREY), ("Viet Nam", RED), ("Colombia", GREEN)]:
    ax.plot(YR, pr.loc[c] / M, color=col); endlabel(ax, 2019, pr.loc[c, "2019"] / M, sh(c), col)
bfmt(ax); ax.set_xlim(1990, 2023.5); ax.set_ylim(0, None)
fig.tight_layout(); card(fig, "01_vietnam_rise", "Coffee production by crop year", "Brazil, Vietnam and Colombia, 1990-2019")

# 2. Concentration stacked area
share = pr.div(pr.sum(), axis=1) * 100
top = list(share["2019"].nlargest(5).index)
fig, ax = plt.subplots(figsize=(12, 6.2))
base = np.zeros(30)
for c, col in zip(top, [GOLD, RED, GREEN, SLATE, SAND]):
    ax.fill_between(YR, base, base + share.loc[c].values, color=col, label=sh(c), edgecolor="white", linewidth=1.2); base = base + share.loc[c].values
ax.fill_between(YR, base, 100, color="#f1ece6", label="All others")
ax.set_ylim(0, 100); ax.set_xlim(1990, 2019); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=14)
ax.grid(axis="x", visible=False)
fig.tight_layout(); card(fig, "02_production_concentration", "Share of world production", "Top 5 producers of 2019, 1990-2019")

# 3. USA share bars
s19 = (con["2019"] / con["2019"].sum() * 100).nlargest(8)[::-1]
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.barh([sh(n) for n in s19.index], s19.values, color=[RED if n == "United States of America" else GOLD for n in s19.index], height=0.62)
for i, v in enumerate(s19.values): ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=15, color=INK, fontweight="bold")
ax.set_xlim(0, 36); ax.grid(axis="y", visible=False); ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
fig.tight_layout(); card(fig, "03_usa_share", "Share of 2019 consumption", "35 importing countries, top 8")

# 4. Change in big markets
rc, ec = con[R].mean(axis=1), con[E].mean(axis=1)
t10 = rc.nlargest(10).index
ch = ((rc[t10] / ec[t10] - 1) * 100).sort_values()
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.barh([sh(n) for n in ch.index], ch.values, color=[RED if v < 0 else GREEN for v in ch.values], height=0.62)
for i, v in enumerate(ch.values): ax.text(v + (3 if v >= 0 else -3), i, f"{v:+.0f}%", va="center", ha="left" if v >= 0 else "right", fontsize=14, color=INK, fontweight="bold")
ax.axvline(0, color=MUTED, linewidth=1.2); ax.set_xlim(-50, 195); ax.grid(axis="y", visible=False)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%")
fig.tight_layout(); card(fig, "04_consumption_change", "Change in consumption", "10 largest markets, 1990-94 avg to 2015-19 avg")

# 5. Imports vs consumption vs re-exports
tot = pd.DataFrame({"Imports": imp.sum(), "Consumption": con.sum(), "Re-exports": rex.sum()}) / M
fig, ax = plt.subplots(figsize=(12, 6.2))
for c, col in [("Imports", GREY), ("Consumption", GOLD), ("Re-exports", RED)]:
    ax.plot(YR, tot[c], color=col); endlabel(ax, 2019, tot.loc["2019", c], c, col)
ax.fill_between(YR, tot["Re-exports"], color=RED, alpha=0.08)
bfmt(ax); ax.set_xlim(1990, 2024.5); ax.set_ylim(0, None)
fig.tight_layout(); card(fig, "05_imports_vs_consumption", "Imports, consumption and re-exports", "Total for 35 importing countries")

# 6. Re-export hubs
rs = (rex[R].sum(axis=1) / imp[R].sum(axis=1) * 100).dropna().nlargest(8)[::-1]
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.barh(rs.index, rs.values, color=[RED if v >= 60 else SAND for v in rs.values], height=0.62)
for i, v in enumerate(rs.values): ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=15, fontweight="bold", color=INK)
ax.set_xlim(0, 100); ax.grid(axis="y", visible=False); ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
fig.tight_layout(); card(fig, "06_re_export_hubs", "Share of imports re-exported", "2015-19, top 8 countries")

# 7. Model scatter
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_predict
d = pd.DataFrame({"c": rc / M, "i": imp[R].mean(axis=1) / M}).dropna()
p = cross_val_predict(LinearRegression(), d[["c"]], d["i"], cv=LeaveOneOut())
fig, ax = plt.subplots(figsize=(12, 6.2))
lim = max(d["i"].max(), p.max()) * 1.05
ax.plot([0, lim], [0, lim], color=GREY, linestyle="--", linewidth=2, label="Perfect prediction")
ax.scatter(d["i"], p, s=110, color=GOLD, edgecolor="white", linewidth=1.5, zorder=3)
for n in ["Germany", "United States of America", "Belgium", "Italy"]:
    k = list(d.index).index(n); ax.annotate(sh(n), (d["i"].iloc[k], p[k]), xytext=(10, -4), textcoords="offset points", fontsize=14, fontweight="bold", color=INK)
ax.set_xlabel("Actual imports, 2015-19 avg (M)"); ax.set_ylabel("Predicted (M)")
ax.legend(frameon=False, loc="upper left")
fig.tight_layout(); card(fig, "07_model_actual_vs_predicted", "Actual vs predicted imports", "Linear model, leave-one-out cross-validation")

# 8. History meets data: Brazil and Colombia with events
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.plot(YR, pr.loc["Brazil"] / M, color=GOLD); ax.plot(YR, pr.loc["Colombia"] / M, color=GREEN); ax.plot(YR, pr.loc["Viet Nam"] / M, color=RED)
endlabel(ax, 2019, pr.loc["Brazil", "2019"] / M, "Brazil", GOLD); endlabel(ax, 2019, pr.loc["Colombia", "2019"] / M, "Colombia", GREEN); endlabel(ax, 2019, pr.loc["Viet Nam", "2019"] / M, "Vietnam", RED)
for x0, x1, lab, yy in [(1994.6, 1995.4, "1994 frosts", 3700), (2000.6, 2002.4, "2001-02 price crash", 3700), (2008, 2012, "Colombia leaf rust", 3700)]:
    ax.axvspan(x0, x1, color="#f1ece6", zorder=0); ax.text((x0 + x1) / 2, yy, lab, ha="center", fontsize=13, color=MUTED, fontweight="bold")
ax.scatter([1995], [pr.loc["Brazil", "1995"] / M], s=120, color=GOLD, edgecolor="white", linewidth=2, zorder=4)
bfmt(ax); ax.set_xlim(1990, 2024); ax.set_ylim(0, 4100)
fig.tight_layout(); card(fig, "00_history_meets_data", "History meets the data", "Production with major events marked (events from history, values from the dataset)")

# 9. Sourcing options: growth of the 10 biggest producers of 2015-19
rp, ep = pr[R].mean(axis=1), pr[E].mean(axis=1)
t10 = rp.nlargest(10).index
grow = ((rp[t10] / ep[t10] - 1) * 100).sort_values()
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.barh([sh(n) for n in grow.index], grow.values, color=[RED if v < 0 else GOLD if n in ("Brazil", "Viet Nam") else GREEN for n, v in grow.items()], height=0.62)
for i, v in enumerate(grow.values): ax.text(v + (15 if v >= 0 else -15), i, f"{v:+.0f}%", va="center", ha="left" if v >= 0 else "right", fontsize=14, color=INK, fontweight="bold")
ax.axvline(0, color=MUTED, linewidth=1.2); ax.set_xlim(-150, 1400); ax.grid(axis="y", visible=False)
ax.xaxis.set_major_formatter(lambda v, _: f"{v:+.0f}%")
fig.tight_layout(); card(fig, "08_sourcing_options", "Change in production", "10 largest producers, 1990-94 avg to 2015-19 avg")

# 10. Mexico vs its neighbours
fig, ax = plt.subplots(figsize=(12, 6.2))
for c, col, lw in [("Mexico", RED, 3.6), ("Honduras", GREEN, 2.4), ("Guatemala", SLATE, 2.4), ("El Salvador", SAND, 2.4), ("Costa Rica", GREY, 2.4)]:
    ax.plot(YR, pr.loc[c] / M, color=col, linewidth=lw); endlabel(ax, 2019, pr.loc[c, "2019"] / M, c, col)
ax.scatter([1999, 2015], [pr.loc["Mexico", "1999"] / M, pr.loc["Mexico", "2015"] / M], s=110, color=RED, edgecolor="white", linewidth=2, zorder=4)
ax.annotate("Peak 1999", (1999, pr.loc["Mexico", "1999"] / M), xytext=(0, 12), textcoords="offset points", ha="center", fontsize=13, fontweight="bold", color=RED)
ax.annotate("Low 2015", (2015, pr.loc["Mexico", "2015"] / M), xytext=(0, -24), textcoords="offset points", ha="center", fontsize=13, fontweight="bold", color=RED)
ax.axvspan(2012, 2016, color="#f1ece6", zorder=0)
ax.text(2014, 455, "Leaf rust years", ha="center", fontsize=13, color=MUTED, fontweight="bold")
ax.set_xlim(1990, 2024.5); ax.set_ylim(0, 480); ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f}M")
fig.tight_layout(); card(fig, "09_mexico_neighbours", "Production: Mexico and Central America", "Millions, by crop year, 1990-2019")

# 11. Coffee kept at home by producers (production minus exports)
yy = ["2010", "2011", "2012", "2013", "2016", "2017", "2018"]  # years with Brazil export data
ex = L("export")[Y]
home = ((pr[yy].sum(axis=1) - ex.loc[pr.index, yy].sum(axis=1)) / len(yy) / M).nlargest(6)[::-1]
usa = con.loc["United States of America", yy].mean() / M
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.barh([sh(n) for n in home.index], home.values, color=[GOLD if n == "Brazil" else SAND for n in home.index], height=0.62)
for i, v in enumerate(home.values): ax.text(v + 15, i, f"{v:,.0f}M", va="center", fontsize=15, fontweight="bold", color=INK)
ax.axvline(usa, color=RED, linestyle="--", linewidth=2)
ax.text(usa - 20, 5.5, f"USA consumption {usa:,.0f}M", ha="right", fontsize=13, fontweight="bold", color=RED)
ax.set_xlim(0, 1750); ax.grid(axis="y", visible=False); ax.xaxis.set_major_formatter(lambda v, _: f"{v:,.0f}M")
fig.tight_layout(); card(fig, "10_kept_at_home", "Coffee producers keep at home", "Production minus exports, yearly average 2010-18 (years with full data)")

# 12. Supply stability of the 10 largest producers
cv = (pr.loc[t10, Y[10:]].pct_change(axis=1).std(axis=1) * 100).sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(12, 6.2))
ax.barh([sh(n) for n in cv.index], cv.values, color=[GREEN if v < 14 else GOLD if v < 20 else RED for v in cv.values], height=0.62)
for i, v in enumerate(cv.values): ax.text(v + 0.5, i, f"{v:.0f}%", va="center", fontsize=15, fontweight="bold", color=INK)
ax.set_xlim(0, 30); ax.grid(axis="y", visible=False); ax.xaxis.set_major_formatter(lambda v, _: f"{v:.0f}%")
fig.tight_layout(); card(fig, "11_supply_stability", "How much output swings year to year", "Typical yearly change in production, 2000-19, 10 largest producers (lower = steadier)")
