# 🏆 World Cup 2026 Predictor

A Monte Carlo simulation engine that predicts the FIFA World Cup 2026 winner using an Elo rating system built from real historical match data — and compares model probabilities against Polymarket betting odds.

---

## 📁 Project Structure

```
world-cup-2026-predictor/
├── data/
│   ├── results.csv          # Historical international match results
│   ├── goalscorers.csv      # Goalscorer data per match
│   ├── shootouts.csv        # Penalty shootout results
│   └── former_names.csv     # Country name changes over time
├── charts/                  # Output charts (auto-generated)
├── wc2026_simulation.py     # 🎯 Main Monte Carlo simulation
├── elo_ratings.py           # Elo rating builder from historical data
├── win_pct_chart.py         # Bar chart: win % by team/continent
├── polymarket_vs_model.py   # Diverging bar: model vs Polymarket odds
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/world-cup-2026-predictor.git
cd world-cup-2026-predictor
pip install -r requirements.txt
```

### 2. Run the simulation

```bash
python wc2026_simulation.py
```

This runs **10,000 Monte Carlo simulations** of the full tournament and prints a ranked table of win probabilities.

### 3. Generate charts

```bash
# Win probability bar chart (colored by continent)
python win_pct_chart.py

# Model vs Polymarket diverging bar chart
python polymarket_vs_model.py
```

Charts are saved to the `charts/` folder.

---

## 🧠 How It Works

### Elo Rating System
- Loads match results from 2019 onwards (`data/results.csv`)
- Builds Elo ratings using a flat K-factor of 24
- Teams without recent history default to 1500

### Monte Carlo Simulation
1. **Group Stage** — 12 groups of 4, round-robin with draw probability
2. **Round of 32** — Snake-seeded mini-groups of 4, top team advances
3. **Knockout Bracket** — R16 → QF → SF → Final, Elo-based win probability
4. **10,000 simulations** — Aggregated win%, finalist%, semi-finalist% per team

### Polymarket Comparison
- Manually pulled Polymarket winner odds (%) for top contenders
- Gap = Model Win% − Polymarket%
- Positive gap → Polymarket OVERvalues the team (model is more skeptical)
- Negative gap → Polymarket UNDERvalues the team (model is more bullish)

---

## 📊 Sample Output

```
🏆 FIFA World Cup 2026 – Monte Carlo Simulation (10,000 sims)

   Team          Win    Win%   Final  Semis
   France        1821   18.21   ...    ...
   Brazil        1543   15.43   ...    ...
   Argentina     1312   13.12   ...    ...
   ...
```

---

## 📦 Data Sources

Historical match data from [Kaggle – International Football Results](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017).

---

## 📝 License

MIT — free to use, modify, and build on.
