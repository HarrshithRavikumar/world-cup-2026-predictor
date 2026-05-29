# 🏆 World Cup 2026 Predictor

A Monte Carlo simulation engine that predicts the **FIFA World Cup 2026** winner using an Elo rating system trained on real international match data since 2019 — with a live web app and Polymarket odds comparison built in.

> **Live app →** [world-cup-2026-predictor.streamlit.app](https://world-cup-2026-predictor-k5u84j9ept7g9fvghwycws.streamlit.app)  
> **Tournament dates:** June 11 – July 19, 2026 · USA, Canada, Mexico

---

## 📸 Preview

| Win Probability Chart | Model vs Polymarket |
|---|---|
| Teams ranked by simulated win % | Where the market is over/undervaluing teams |

---

## 🧠 How It Works

### 1. Elo Rating System
- Loads all international match results from **2019 onwards** (`data/results.csv`)
- Processes ~5,000+ matches chronologically to build current ratings
- Uses a flat K-factor of **24** and a starting rating of **1500**
- Teams not in the dataset default to 1500

### 2. Monte Carlo Simulation (10,000 runs by default)

Each simulation runs the full tournament:

| Stage | Format |
|---|---|
| **Group Stage** | 12 groups × 4 teams, full round-robin. Draw probability: 22% |
| **Round of 32** | Top 2 per group + 8 best 3rd-place teams = 32 teams |
| **Knockout (R16 → Final)** | Single-elimination, Elo win probability, no draws |

After 10,000 runs, each team's **win%, finalist%, and semi-finalist%** is calculated.

### 3. Polymarket Comparison
Model win probabilities are compared against live Polymarket betting odds. A positive gap means the market overvalues a team relative to the model; negative means the model is more bullish.

---

## 🗂️ Confirmed WC 2026 Groups

*(Draw held December 5, 2025 — Kennedy Center, Washington D.C.)*

| Group | Teams |
|---|---|
| **A** | Mexico · South Africa · South Korea · Czechia |
| **B** | Canada · Bosnia and Herzegovina · Qatar · Switzerland |
| **C** | Brazil · Morocco · Haiti · Scotland |
| **D** | United States · Paraguay · Australia · Turkey |
| **E** | Germany · Curacao · Ivory Coast · Ecuador |
| **F** | Netherlands · Japan · Sweden · Tunisia |
| **G** | Belgium · Egypt · Iran · New Zealand |
| **H** | Spain · Cape Verde · Saudi Arabia · Uruguay |
| **I** | France · Senegal · Iraq · Norway |
| **J** | Argentina · Algeria · Austria · Jordan |
| **K** | Portugal · DR Congo · Uzbekistan · Colombia |
| **L** | England · Croatia · Ghana · Panama |

---

## 📁 Project Structure

```
world-cup-2026-predictor/
├── app.py                   # 🌐 Streamlit web app (run this to deploy)
├── wc2026_simulation.py     # 🎯 Standalone Monte Carlo simulation
├── elo_ratings.py           # 📊 Elo builder — prints top 32 rated teams
├── win_pct_chart.py         # 📈 Win probability bar chart (by continent)
├── polymarket_vs_model.py   # ⚖️  Diverging bar: model vs Polymarket odds
├── requirements.txt
├── data/
│   ├── results.csv          # Historical international match results (1872–)
│   ├── goalscorers.csv      # Goalscorer data per match
│   ├── shootouts.csv        # Penalty shootout outcomes
│   └── former_names.csv     # Country name changes over time
└── charts/                  # Output folder for saved PNGs
```

---

## 🚀 Quick Start

### Run locally

```bash
# Clone
git clone https://github.com/harrshithravikumar/world-cup-2026-predictor.git
cd world-cup-2026-predictor

# Install dependencies
pip install -r requirements.txt

# Launch the web app
streamlit run app.py
```

### Run just the simulation (no UI)

```bash
python wc2026_simulation.py
```

### Generate standalone charts

```bash
python win_pct_chart.py          # Win % by team
python polymarket_vs_model.py    # Model vs Polymarket
python elo_ratings.py            # Print Elo ratings table
```

---

## 📦 Dependencies

```
streamlit >= 1.32
matplotlib >= 3.7
pandas >= 2.0
numpy >= 1.24
```

---

## 📊 Data Sources

- **Match results:** [Kaggle — International Football Results 1872–present](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017) (Mart Jürisoo)
- **WC 2026 groups:** Official FIFA draw, December 5, 2025
- **Polymarket odds:** Manually pulled from polymarket.com

---

## ⚠️ Limitations

- Elo ratings don't account for squad injuries, form streaks, or tactical matchups
- Group draw is fixed to the confirmed Dec 2025 draw — no re-draw simulation
- Polymarket odds are a snapshot and change daily
- The simulation uses simplified tiebreaker logic (points → goal difference → random)

---

---

## 📝 License

MIT — free to use, fork, and build on.

---

*Built with Python, Streamlit, and Matplotlib. Simulation engine uses Elo ratings trained on 5,000+ international matches since 2019.*
