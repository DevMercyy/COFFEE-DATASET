"""
Simple models on the importing countries, fixed from the original scripts.

What changed from the first version, and why:
  * The two files are joined on Country (pd.merge) instead of lining rows up
    by position, so a re-ordered file can't silently mismatch countries.
  * Recent averages (2015-19) are used instead of 30-year totals. Totals mix
    in years where a country wasn't reported (Belgium before 1999, etc.).
  * With only ~30 countries, a single 80/20 split tests on 6 or 7 points, so the
    score depends on which countries land in the test set. Leave-one-out
    cross-validation tests on every country once instead.
  * The "Actual vs Predicted" chart (drawn by figures.py) uses the y = x line
    (a perfect prediction), not the trend line from a different chart.
  * The LASSO in MERGED.py predicted Total_import from the yearly import
    columns it is the sum of, so its result was guaranteed and told us
    nothing. It has been removed.
  * No input() prompt, so the script runs start to finish.

Run:  python src/models.py   (after clean_data.py)
"""

from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import LeaveOneOut, cross_val_predict

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"
RECENT = [str(y) for y in range(2015, 2020)]
MILLION = 1e6


def recent_average(name, column):
    df = pd.read_csv(CLEAN / f"{name}_wide.csv")
    df[column] = df[RECENT].mean(axis=1) / MILLION
    return df[["Country", column]]


def main():
    data = (
        recent_average("consumption", "consumption")
        .merge(recent_average("import", "imports"), on="Country")
        .merge(recent_average("re_export", "re_exports"), on="Country")
        .dropna()
    )
    print(f"{len(data)} countries with 2015-19 data")

    # Question: how well does what a country drinks predict what it imports?
    X, y = data[["consumption"]], data["imports"]
    model = LinearRegression().fit(X, y)
    predicted = cross_val_predict(LinearRegression(), X, y, cv=LeaveOneOut())
    print(f"imports = {model.coef_[0]:.2f} x consumption + {model.intercept_:.1f}M")
    print(f"Leave-one-out R2: {r2_score(y, predicted):.3f}, MAE: {mean_absolute_error(y, predicted):.1f}M")

    data["predicted"] = predicted
    data["miss"] = data["imports"] - data["predicted"]
    print("Biggest misses (imports above what consumption predicts):")
    print(data.sort_values("miss", ascending=False)[["Country", "imports", "predicted", "miss"]].head(5).round(1).to_string(index=False))

    # The misses are the re-export hubs. Adding re-exports gives R2 of about 1,
    # but that is bookkeeping, not insight: in this dataset imports are (almost
    # exactly) consumption + re-exports, so this "model" just re-adds the parts.
    both = data[["consumption", "re_exports"]]
    predicted_both = cross_val_predict(LinearRegression(), both, y, cv=LeaveOneOut())
    print(f"With re-exports added, leave-one-out R2: {r2_score(y, predicted_both):.3f} "
          "(expected: imports = consumption + re-exports in this data)")



if __name__ == "__main__":
    main()
