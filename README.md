# Inferences from the Coffee Dataset

**Where should a coffee company build?** This project explores 30 years (1990-2019) of world coffee production and trade to find trends that help answer that question. Every inference comes only from the numbers in the data.

![Vietnam's rise](figures/01_vietnam_rise.png)

The charts below are the same files used in the slides (`slides/Coffee_Trends.pptx`), all drawn by `src/figures.py`.

## Key findings

1. **Vietnam's production grew 13x** (1990-94 average to 2015-19 average), from the #17 producer to #2. Its share of world output went from 1.4% to 18.5%.
2. **Production is concentrating.** The top 5 producers made 61% of world output in 1990 and 74% in 2019. Brazil and Vietnam alone make 54%.
3. **Mexico shrank.** Output fell 55% from its 1999 peak (373M) to its 2015 low (166M), then recovered to 239M. Public sources link this to the 1989 closure of Mexico's coffee institute and the end of export quotas, and to leaf rust from 2012 ([Sucafina](https://www.sucafina.com/na/origins/mexico), [Perfect Daily Grind](https://perfectdailygrind.com/?p=67157), [Naatik](https://naatikmexico.org/blog/the-history-of-coffee-in-mexico)). Honduras more than tripled over the same period.
4. **Supply stability differs.** India's output changes about 8% a year, Colombia's and Mexico's about 13%; Brazil, Indonesia and Peru swing 25-26% a year.
5. **Producers are markets too.** Brazil keeps about 1,378M a year (production minus exports, 2010-18), close to USA consumption of 1,435M. Ethiopia keeps 51% of its coffee.
6. **Most import growth is coffee passing through.** Imports of the 35 importing countries grew by 3.65B from 1990 to 2019; 2.29B of that (63%) was re-exported.
7. **Re-export hubs.** Belgium re-exports 78% of what it imports, Germany 61% and the Netherlands 60% (2015-19).
8. **The USA is 31% of importer consumption** (2019), three times Germany's 10%.
9. **Old and new markets.** Consumption fell in Germany (-12%) and the Netherlands (-24%), and rose in Russia (+168%), Poland (+92%) and Romania (+151%).
10. **Model**: consumption predicts imports with a leave-one-out R² of 0.66. The biggest misses are the re-export hubs.
11. **Market scorecard**: ranking markets equally on size, growth and stability (typical yearly change) puts the USA, Japan and Italy first.

| Chart | Shows |
|---|---|
| ![](figures/00_history_meets_data.png) | Production with historical events marked |
| ![](figures/02_production_concentration.png) | Top 5 producers' share of world output |
| ![](figures/09_mexico_neighbours.png) | Mexico and Central America |
| ![](figures/11_supply_stability.png) | Year-to-year swing of the 10 largest producers |
| ![](figures/10_kept_at_home.png) | Coffee kept at home by producers |
| ![](figures/03_usa_share.png) | Share of 2019 consumption |
| ![](figures/04_consumption_change.png) | Consumption change in the 10 largest markets |
| ![](figures/05_imports_vs_consumption.png) | Imports vs consumption vs re-exports |
| ![](figures/06_re_export_hubs.png) | Re-export hubs |
| ![](figures/07_model_actual_vs_predicted.png) | Model: actual vs predicted imports |
| ![](figures/08_sourcing_options.png) | Production change of the 10 largest producers |

## Call to action: four moves for a company starting out

1. **Launch in a large, steady market**: the USA, Japan or Italy (top-5 markets, +25% to +41%, changing only 2-4% a year).
2. **Add a growth market next**: Russia (+168%) or Poland (+92%), whose demand swings 16-17% a year.
3. **Source from two regions**: Brazil and Vietnam make 54% of all coffee and Brazil's crop swings about 25% a year; add a steady or rising origin such as Ethiopia, Colombia or Honduras.
4. **Distribute through a European hub**: Belgium, the Netherlands and Germany re-export 60-78% of their imports.

## Data

Source: Kaggle coffee dataset, 1990-2019 (add the dataset link here).

| File | Countries | Content |
|---|---|---|
| `Coffee_production.csv` | 55 | Production per crop year, with coffee type |
| `Coffee_export.csv` | 55 | Exports per year |
| `Coffee_import.csv` | 35 | Imports per year |
| `Coffee_importers_consumption.csv` | 35 | Consumption in importing countries |
| `Coffee_re_export.csv` | 35 | Re-exports per year |

Quantities are in the source file's units. Every value is a multiple of 60, which suggests 60-kg bags converted to kilograms.

### Data issues found and fixed (`src/clean_data.py`)

- Country names in the importer files had leading spaces.
- Production year headers had typos (`1990/20991`, `2009/200`), renamed to the crop year's start.
- Brazil's exports for 2014, 2015 and 2019 are `-2,147,483,648`, the smallest 32-bit integer. That's an overflow error in the source, so those values are marked missing.
- Zeros before a country starts reporting (Belgium and Luxembourg were reported together until 1998; Russia and the Baltic states start in 1992) are marked missing rather than treated as "no coffee".

## How to run

```bash
pip install -r requirements.txt
python src/clean_data.py   # raw -> data/clean/
python src/analysis.py     # prints every number in the README and slides
python src/models.py       # regression with leave-one-out cross-validation
python src/figures.py      # draws every chart in figures/ (used by the slides)
```

## Project structure

```
data/raw/        original CSVs
data/clean/      cleaned wide and long files, market scorecard
src/             cleaning, analysis, model and chart scripts
figures/         charts used in the README and slides (one source)
slides/          Coffee_Trends.pptx (the presentation)
explorer/        index.html, an interactive chart page
requirements.txt Python packages needed
```

## Interactive explorer

Open `explorer/index.html` in a browser to explore any country and any measure, with six story shortcuts.

## Credits

Historical context in the slides comes from general sources, not the dataset. Photos in the slides are AI-generated.

## Author

Mercy Olaosebikan
