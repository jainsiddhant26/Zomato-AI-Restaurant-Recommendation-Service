# Zomato AI Restaurant Recommendation Service — Architecture

## Overview

This document describes the architecture and phase-wise development plan for the **Zomato AI Restaurant Recommendation Service**. The service recommends restaurants based on **city** and **price** (approx cost for two people).

**Dataset:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

---

## Dataset Summary

| Column | Type | Description |
|--------|------|-------------|
| `url` | string | Zomato restaurant link |
| `address` | string | Full address |
| `name` | string | Restaurant name |
| `online_order` | Yes/No | Online ordering availability |
| `book_table` | Yes/No | Table booking availability |
| `rate` | string | Rating (e.g., "4.1/5") |
| `votes` | int | Number of reviews |
| `phone` | string | Contact number |
| `location` | string | Area within city (93 values) |
| `rest_type` | string | Restaurant type (e.g., Casual Dining, Cafe) |
| `dish_liked` | string | Popular dishes |
| `cuisines` | string | Cuisine types |
| `approx_cost(for two people)` | string | Price for two (e.g., "800", "300") |
| `reviews_list` | string | Customer reviews |
| `menu_item` | string | Menu items |
| `listed_in(type)` | string | Category (e.g., Buffet, Cafes) |
| `listed_in(city)` | string | City (30 values) |

**Scale:** ~51.7k rows · **Format:** Hugging Face Datasets / CSV

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     ZOMATO AI RESTAURANT RECOMMENDATION SERVICE              │
└─────────────────────────────────────────────────────────────────────────────┘

  STEP 1                    STEP 2                   STEP 3
  ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
  │ Load Data   │          │ User Input  │          │ Integrate   │
  │             │          │             │          │             │
  │ • Hugging   │          │ • City      │          │ • Connect   │
  │   Face API  │  ─────►  │ • Price     │  ─────►  │   inputs    │
  │ • Pandas    │          │ • Validation│          │ • Filter    │
  │ • Cache     │          │ • CLI/UI    │          │   pipeline  │
  └─────────────┘          └─────────────┘          └──────┬──────┘
                                                          │
  STEP 5                    STEP 4                        │
  ┌─────────────┐          ┌─────────────┐                │
  │ Display     │  ◄─────  │ Recommend   │  ◄─────────────┘
  │             │          │             │
  │ • Cards     │          │ • Filter by │
  │ • Table     │          │   city+price│
  │ • Console   │          │ • Rank by   │
  └─────────────┘          │   rating    │
                           └─────────────┘
```

---

## Phase-wise Development

### STEP 1 — Input the Zomato Data

**Objective:** Load and persist the Zomato dataset for use by the recommendation pipeline.

| Aspect | Details |
|--------|---------|
| **Source** | Hugging Face Datasets (`ManikaSaini/zomato-restaurant-recommendation`) |
| **Method** | `datasets.load_dataset("ManikaSaini/zomato-restaurant-recommendation")` |
| **Output** | DataFrame (Pandas / Polars) in memory or cached to disk |
| **Artifacts** | `data/zomato_data.parquet` or in-memory DataFrame |
| **Preprocessing** | • Normalize `approx_cost(for two people)` (remove commas, handle "500-1000")<br>• Parse `rate` to numeric (e.g., "4.1/5" → 4.1)<br>• Map `listed_in(city)` for city filter |

**Deliverables:**
- `load_data.py` — Load via Hugging Face, optional caching
- `preprocess.py` — Clean and normalize key columns
- Unit tests for load and preprocess

---

### STEP 2 — User Input

**Objective:** Collect and validate user inputs (city and price).

| Aspect | Details |
|--------|---------|
| **Inputs** | • **City** — Text (matches `listed_in(city)`) |
| | • **Price** — Approx cost for two (single value or max budget, e.g., 800) |
| **Validation** | • City must exist in dataset<br>• Price: numeric, optional range (min–max) |
| **Interface** | CLI (argparse / input prompts) or minimal web form (HTML + JS) |

**Deliverables:**
- `input_handler.py` — Parse and validate city, price
- `cli.py` — Command-line interface
- Optional: simple HTML form for future UI

**Example usage:**
```
python cli.py --city "Banashankari" --price 600
python cli.py --city Bangalore --price 800 --max-price 1000
```

---

### STEP 3 — Integrate

**Objective:** Connect data pipeline and user inputs into a single flow.

| Aspect | Details |
|--------|---------|
| **Flow** | Load Data → Validate Input → Filter by city and price |
| **Filtering** | • `listed_in(city)` ≈ user city (case-insensitive, fuzzy if needed)<br>• `approx_cost(for two people)` ≤ user price (or within range) |
| **Output** | Filtered DataFrame of candidate restaurants |

**Deliverables:**
- `pipeline.py` — Orchestrates load, preprocess, filter
- Integration tests: known city + price → expected restaurant count

**Logic:**
```python
# Pseudocode
df = load_and_preprocess_data()
candidates = df[
    (df["listed_in(city)"].str.contains(city, case=False)) &
    (df["approx_cost_clean"] <= price_max)
]
```

---

### STEP 4 — Recommendation

**Objective:** Rank filtered restaurants and return top recommendations.

| Aspect | Details |
|--------|---------|
| **Ranking** | • Primary: `rate` (parsed numeric)<br>• Secondary: `votes` (social proof) |
| **Algorithm** | Rule-based scoring or simple weighted score: `score = rating * log(1 + votes)` |
| **Output** | Top N restaurants (e.g., 10) with key fields |

**Deliverables:**
- `recommend.py` — Rank and return top N
- Config: `TOP_N`, `SCORE_WEIGHTS`

**Logic:**
```python
# Pseudocode
candidates["score"] = candidates["rate_num"] * np.log1p(candidates["votes"])
top = candidates.nlargest(TOP_N, "score")
```

---

### STEP 5 — Display to the User

**Objective:** Present recommendations in a clear, readable format.

| Aspect | Details |
|--------|---------|
| **Output modes** | • **Console** — Formatted table (tabulate / rich)<br>• **JSON** — For API / future integrations |
| **Displayed fields** | Name, Location, Cuisines, Rate, Votes, Price, Dish Liked |
| **Format** | Cards, table rows, or JSON array |

**Deliverables:**
- `display.py` — Console table and optional JSON export
- Optional: simple HTML template for web UI

**Example output:**
```
┌──────────────┬──────────────┬─────────────────┬───────┬───────┬───────┐
│ Name         │ Location     │ Cuisines        │ Rate  │ Votes │ Price │
├──────────────┼──────────────┼─────────────────┼───────┼───────┼───────┤
│ Onesta       │ Banashankari │ Pizza, Cafe     │ 4.6   │ 2556  │ 600   │
│ Jalsa        │ Banashankari │ North Indian    │ 4.1   │ 775   │ 800   │
└──────────────┴──────────────┴─────────────────┴───────┴───────┴───────┘
```

---

## Project Structure (Suggested)

```
Zomato-AI-Restaurant-Recommendation-Service/
├── ARCHITECTURE.md           # This file
├── requirements.txt
├── config.py                 # TOP_N, paths, etc.
├── src/
│   ├── load_data.py          # STEP 1
│   ├── preprocess.py         # STEP 1
│   ├── input_handler.py      # STEP 2
│   ├── cli.py                # STEP 2
│   ├── pipeline.py           # STEP 3
│   ├── recommend.py          # STEP 4
│   └── display.py            # STEP 5
├── data/                     # Cached data (gitignored)
└── tests/
    ├── test_load.py
    ├── test_input.py
    ├── test_pipeline.py
    ├── test_recommend.py
    └── test_display.py
```

---

## Dependencies (requirements.txt)

```
datasets>=2.14.0
pandas>=2.0.0
huggingface_hub>=0.17.0
tabulate>=0.9.0
```

---

## Execution Flow (End-to-End)

```
1. User runs: python cli.py --city Banashankari --price 800
2. input_handler validates city and price
3. pipeline loads data (from cache or Hugging Face), preprocesses, filters
4. recommend ranks filtered restaurants and selects top N
5. display prints table to console (or exports JSON)
```

---

## Future Enhancements (Out of Scope)

- Deployment (cloud, Docker, API)
- ML-based ranking (collaborative filtering, content-based)
- Cuisine / dish preferences as extra filters
- Web UI with search and filters
