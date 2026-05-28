import pandas as pd

# ── Load and filter results.csv to matches from 2019 onwards ─────────────────
results_df = pd.read_csv("data/results.csv", parse_dates=["date"])
results_df = results_df[results_df["date"].dt.year >= 2019].copy()
results_df = results_df.sort_values("date").reset_index(drop=True)

print(f"Total matches from 2019 onwards: {len(results_df)}")
print(f"Date range: {results_df['date'].min().date()} → {results_df['date'].max().date()}")

# ── Elo Rating System ─────────────────────────────────────────────────────────
N = 24          # Flat K-factor
DEFAULT_ELO = 1500
_elo = {}       # internal mocking dict (private)


def get_elo(team):
    return _elo.get(team, DEFAULT_ELO)


def expected_score(za, zb):
    return 1 / (1 + 10 ** ((zb - za) / 400))


def update_elo(home_team, away_team, home_goals, away_goals):
    za = get_elo(home_team)
    zb = get_elo(away_team)

    ea = expected_score(za, zb)
    eb = expected_score(zb, za)

    if home_goals > away_goals:
        sa, sb = 1.0, 0.0
    elif home_goals < away_goals:
        sa, sb = 0.0, 1.0
    else:
        sa, sb = 0.5, 0.5

    _elo[home_team] = za + N * (sa - ea)
    _elo[away_team] = zb + N * (sb - eb)


# ── Process matches chronologically ──────────────────────────────────────────
for _row in results_df.iterrows():
    _, row = _row
    update_elo(row["home_team"], row["away_team"], row["home_score"], row["away_score"])

# ── Final ratings dict (required output variable) ─────────────────────────────
elo_ratings = dict(_elo)

print(f"\n{len(elo_ratings)} total teams rated:")

# ── Build ranked table of top 32 teams ───────────────────────────────────────
_elo_series = pd.Series(elo_ratings, name="Elo Rating").round(1)
_elo_series.index.name = "Team"
_top32 = (
    _elo_series
    .sort_values(ascending=False)
    .head(32)
)
_top32 = pd.DataFrame(_top32)
_top32.index = _top32.index + 1   # 1-based rank
_top32.index.name = "Rank"

print("\n" + " " * 4 + f"{'Team':<28} {'Elo':>6}")
print("─" * 42)
for _rank, _r in _top32.iterrows():
    print(f"  {'Rank':>6} {_r['Team']:<28} {_r['Elo Rating']:>6.1f}")
