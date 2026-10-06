"""
Coffee trade trends, 1990-2019.

Reads the cleaned files made by clean_data.py and prints the key numbers behind
every finding. The charts are drawn by figures.py, so the slides, the README and
this script all share one set of numbers and one set of charts.

Every claim in the README and the slides comes from a number printed here.
"Early" means the 1990-94 average and "recent" means the 2015-19 average,
so one unusual year cannot drive a result.

Run:  python src/clean_data.py, then python src/analysis.py
"""

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"

YEARS = [str(y) for y in range(1990, 2020)]
EARLY = [str(y) for y in range(1990, 1995)]
RECENT = [str(y) for y in range(2015, 2020)]

MILLION = 1e6
BILLION = 1e9


def load(name):
    return pd.read_csv(CLEAN / f"{name}_wide.csv").set_index("Country")


def main():
    production = load("production")
    exports = load("export")
    imports = load("import")
    consumption = load("consumption")
    re_exports = load("re_export")
    findings = {}

    # ------------------------------------------------------------------
    # 1. World production grew and became more concentrated
    # ------------------------------------------------------------------
    prod = production[YEARS]
    world = prod.sum()
    share = prod.div(world, axis=1) * 100
    top5_1990 = share["1990"].nlargest(5)
    top5_2019 = share["2019"].nlargest(5)
    growth = (world[RECENT].mean() / world[EARLY].mean() - 1) * 100
    print("\n1. Production")
    print(f"  World production 1990: {world['1990'] / BILLION:.2f}B, 2019: {world['2019'] / BILLION:.2f}B")
    print(f"  Growth, 1990-94 avg to 2015-19 avg: {growth:.0f}%")
    print(f"  Top 5 share 1990: {top5_1990.sum():.1f}% {list(top5_1990.index)}")
    print(f"  Top 5 share 2019: {top5_2019.sum():.1f}% {list(top5_2019.index)}")
    findings["production"] = {
        "world_1990": world["1990"], "world_2019": world["2019"], "growth_pct": growth,
        "top5_share_1990": top5_1990.sum(), "top5_share_2019": top5_2019.sum(),
    }

    # 2. Vietnam's rise, Colombia standing still, and rising origins
    focus = ["Brazil", "Viet Nam", "Colombia", "Indonesia", "Ethiopia", "Honduras", "Uganda", "Peru"]
    for country in focus:
        early, recent = prod.loc[country, EARLY].mean(), prod.loc[country, RECENT].mean()
        rank_1990 = int(prod["1990"].rank(ascending=False)[country])
        rank_2019 = int(prod["2019"].rank(ascending=False)[country])
        print(f"  {country}: {early / MILLION:.0f}M -> {recent / MILLION:.0f}M "
              f"({recent / early:.1f}x), share {share.loc[country, '1990']:.1f}% -> "
              f"{share.loc[country, '2019']:.1f}%, rank {rank_1990} -> {rank_2019}")



    print(f"  Brazil + Vietnam share of 2019 output: {share.loc[['Brazil', 'Viet Nam'], '2019'].sum():.1f}%")

    # Events visible in the data (history slides)
    brazil, colombia = prod.loc["Brazil"] / MILLION, prod.loc["Colombia"] / MILLION
    print(f"  Brazil 1995 crop: {brazil['1995']:.0f}M ({(brazil['1995'] / brazil['1994'] - 1) * 100:.0f}% vs 1994), "
          f"lowest year: {brazil.idxmin()}")
    print(f"  Colombia: 2007 {colombia['2007']:.0f}M, 2011 {colombia['2011']:.0f}M, 2019 {colombia['2019']:.0f}M")
    biggest_drop = (prod.pct_change(axis=1) * 100).loc[["Brazil", "Viet Nam", "Colombia"]].min(axis=1)
    print("  Largest one-year production drop:", biggest_drop.round(0).to_dict())

    # ------------------------------------------------------------------
    # 3. Importing countries: what is drunk vs what passes through
    # ------------------------------------------------------------------
    imp, con, rex = imports[YEARS], consumption[YEARS], re_exports[YEARS]
    totals = pd.DataFrame({"Imports": imp.sum(), "Consumption": con.sum(), "Re-exports": rex.sum()})
    import_gain = totals.loc["2019", "Imports"] - totals.loc["1990", "Imports"]
    rex_gain = totals.loc["2019", "Re-exports"] - totals.loc["1990", "Re-exports"]
    con_gain = totals.loc["2019", "Consumption"] - totals.loc["1990", "Consumption"]
    print("\n3. Importing countries (35)")
    print(totals.loc[["1990", "2000", "2010", "2019"]].div(BILLION).round(2))
    print(f"  Import gain 1990-2019: {import_gain / BILLION:.2f}B, of which re-exports "
          f"{rex_gain / BILLION:.2f}B ({rex_gain / import_gain * 100:.0f}%), consumption {con_gain / BILLION:.2f}B")
    findings["importers"] = {
        "import_gain": import_gain, "re_export_gain": rex_gain, "consumption_gain": con_gain,
    }


    # Re-export share, recent years
    rex_share = (rex[RECENT].sum(axis=1) / imp[RECENT].sum(axis=1) * 100).dropna().sort_values()
    print("  Re-export share of imports, 2015-19 (top 6):")
    print(rex_share.tail(6).round(1).to_string())
    top12 = rex_share.tail(12)

    # ------------------------------------------------------------------
    # 4. Which markets grew, which shrank
    # ------------------------------------------------------------------
    early_con = con[EARLY].mean(axis=1)
    recent_con = con[RECENT].mean(axis=1)
    # Only countries reported in at least 3 of 1990-94 and in 2015-19.
    # Belgium and Luxembourg were reported together until 1998, so they drop
    # out; states that start reporting in 1992 or 1993 (Russia, Baltics,
    # Croatia, Slovakia...) are compared on the years they have.
    full = (con[EARLY].notna().sum(axis=1) >= 3) & con[RECENT].notna().all(axis=1)
    change = ((recent_con / early_con - 1) * 100)[full].sort_values()
    print("\n4. Consumption change, 1990-94 avg to 2015-19 avg (countries reported in 3+ of 1990-94)")
    print(change.round(1).to_string())


    share_2019 = (con["2019"] / con["2019"].sum() * 100).sort_values(ascending=False)
    print("  Consumption share 2019 (top 6):")
    print(share_2019.head(6).round(1).to_string())
    findings["consumption_share_2019"] = share_2019.head(10).round(2).to_dict()

    # ------------------------------------------------------------------
    # 5. Market scorecard (the original question: where to build?)
    # ------------------------------------------------------------------
    # Stability = typical size of the year-to-year change, 2000-19
    # (standard deviation of the yearly % change; lower = steadier)
    stability = con[[str(y) for y in range(2000, 2020)]]
    variation = stability.pct_change(axis=1).std(axis=1) * 100
    card = pd.DataFrame({
        "consumption_2015_19": recent_con / MILLION,
        "change_pct": (recent_con / early_con - 1) * 100,
        "variation_pct": variation,
    })[full].dropna()
    # Rank each measure (1 = best) and average them, equal weights
    card["size_rank"] = card["consumption_2015_19"].rank(ascending=False)
    card["growth_rank"] = card["change_pct"].rank(ascending=False)
    card["stability_rank"] = card["variation_pct"].rank()
    card["score"] = card[["size_rank", "growth_rank", "stability_rank"]].mean(axis=1)
    card = card.sort_values("score")
    print("\n5. Market scorecard (lower score = better; equal weights on size, growth, stability)")
    print(card.round(1).head(10).to_string())
    card.round(2).to_csv(CLEAN / "market_scorecard.csv")

    # Supply stability of the 10 largest producers (same measure)
    top_producers = prod[RECENT].mean(axis=1).nlargest(10).index
    swing = prod.loc[top_producers, [str(y) for y in range(2000, 2020)]].pct_change(axis=1).std(axis=1) * 100
    print("\n  Producer year-to-year swing, 2000-19 (lower = steadier):")
    print(swing.round(1).sort_values().to_string())

    # Coffee kept at home by producers: production minus exports, years with
    # Brazil export data (2014, 2015 and 2019 are missing for Brazil)
    full_years = ["2010", "2011", "2012", "2013", "2016", "2017", "2018"]
    home = (prod[full_years].sum(axis=1) - exports.loc[prod.index, full_years].sum(axis=1)) / len(full_years)
    kept = (home / prod[full_years].mean(axis=1) * 100)
    print("\n  Kept at home (production - exports), yearly avg 2010-18:")
    print(pd.DataFrame({"million": home / MILLION, "pct_of_output": kept}).loc[home.nlargest(6).index].round(0).to_string())
    print(f"  USA consumption, same years: {con.loc['United States of America', full_years].mean() / MILLION:.0f}M")

    # Mexico
    mex = prod.loc["Mexico"] / MILLION
    print(f"\n  Mexico: peak {mex.idxmax()} {mex.max():.0f}M, low {mex.idxmin()} {mex.min():.0f}M "
          f"({(mex.min() / mex.max() - 1) * 100:.0f}% from peak), 2019 {mex['2019']:.0f}M")

    # Data-driven market segments: thirds of recent consumption
    segments = pd.qcut(recent_con[full], 3, labels=["Small", "Medium", "Large"])
    cuts = recent_con[full].quantile([1 / 3, 2 / 3]) / MILLION
    print(f"  Segment cut-offs (2015-19 avg consumption): {cuts.iloc[0]:.0f}M and {cuts.iloc[1]:.0f}M")
    print(segments.value_counts().to_string())

    # ------------------------------------------------------------------
    # 6. Data quality note: Brazil export overflow
    # ------------------------------------------------------------------
    missing = exports.loc["Brazil", YEARS]
    print("\n6. Brazil export years missing after cleaning:", list(missing[missing.isna()].index))

    # Save series for the interactive explorer
    explorer = {
        "years": list(range(1990, 2020)),
        "production": prod.round(0).where(prod.notna(), None).to_dict("index"),
        "consumption": con.round(0).where(con.notna(), None).to_dict("index"),
        "imports": imp.round(0).where(imp.notna(), None).to_dict("index"),
        "re_exports": rex.round(0).where(rex.notna(), None).to_dict("index"),
        "exports": exports[YEARS].round(0).where(exports[YEARS].notna(), None).to_dict("index"),
        "coffee_type": production["Coffee_type"].to_dict(),
    }
    with open(CLEAN / "explorer_data.json", "w") as f:
        json.dump(explorer, f)
    with open(CLEAN / "findings.json", "w") as f:
        json.dump(findings, f, indent=2, default=float)
    print("\nSaved data/clean/explorer_data.json and findings.json")


if __name__ == "__main__":
    main()
