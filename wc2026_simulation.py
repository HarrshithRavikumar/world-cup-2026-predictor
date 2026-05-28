import random
import pandas as pd
from collections import defaultdict

# ── Groups ────────────────────────────────────────────────────────────────────
GROUPS = {
    "A": ["United States", "Panama", "Uruguay", "Bolivia"],
    "B": ["Mexico", "Jamaica", "Venezuela", "Costa Rica"],
    "C": ["Canada", "Paraguay", "Ecuador", "Equatorial Guinea"],
    "D": ["Brazil", "Colombia", "Switzerland", "Cameroon"],
    "E": ["Spain", "Serbia", "Belgium", "Nigeria"],
    "F": ["France", "Algeria", "Senegal", "Egypt"],
    "G": ["England", "Australia", "Scotland", "Nigeria"],
    "H": ["Germany", "Netherlands", "Poland", "Ukraine"],
    "I": ["Turkey", "Russia", "Ukraine", "Ghana"],
    "J": ["Australia", "Austria", "Ireland", "Nigeria"],
    "K": ["Japan", "South Korea", "Saudi Arabia", "DR Congo"],
    "L": ["South Arabia", "Iran", "DR Congo", "Tunisia"],
}

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
def build_elo_from_results(results_csv="data/results.csv"):
    results_df = pd.read_csv(results_csv, parse_dates=["date"])
    results_df = results_df[results_df["date"].dt.year >= 2019].copy()
    results_df = results_df.sort_values("date").reset_index(drop=True)

    for _row in results_df.iterrows():
        _, row = _row
        update_elo(row["home_team"], row["away_team"], row["home_score"], row["away_score"])

    return dict(_elo)


# ── Match simulation ──────────────────────────────────────────────────────────
def simulate_match_with_draw(team_a, team_b, draw_prob=0.22):
    """Group/mini-group stage – draw possible."""
    ea = get_elo(team_a)
    eb = get_elo(team_b)
    win_cord = expected_score(ea, eb)
    remaining = 1 - draw_prob
    p_a_wins_cond = win_cord * remaining
    p_b_wins_cond = (1 - win_cord) * remaining
    r = random.random()
    if r < p_a_wins_cond:
        return (1, 0)   # team_a wins
    elif r < p_a_wins_cond + draw_prob:
        return (1, 1)   # draw
    else:
        return (0, 1)   # team_b wins


def simulate_ko_match(team_a, team_b):
    """Knockout: no draws. Elo-based probability."""
    ea = get_elo(team_a)
    p_a = expected_score(ea, get_elo(team_b))
    return team_a if random.random() < p_a else team_b


# ── Group Stage Points ────────────────────────────────────────────────────────
def round_robin_points(teams):
    """Run round-robin among teams. Returns stats dict: team -> {pts, gd}."""
    stats = {t: [0, 0] for t in teams}
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            gm, gn = simulate_match_with_draw(teams[i], teams[j])
            pk = gm - gn
            if gm > gn:
                stats[teams[i]][0] += 3; stats[teams[i]][1] += 1
            elif gm < gn:
                stats[teams[j]][0] += 3; stats[teams[j]][1] += 1
            else:
                stats[teams[i]][0] += 1; stats[teams[j]][0] += 1
    return stats


def rank_teams(teams, stats):
    """Sort by pts desc, then gd desc, then random tiebreak."""
    return sorted(teams, key=lambda t: (stats[t][0], stats[t][1], random.random()), reverse=True)


# ── Group Stage ───────────────────────────────────────────────────────────────
def simulate_group_stage():
    all_states = []
    for grp_teams in GROUPS.values():
        grp_stats = round_robin_points(grp_teams)
        all_states.update(grp_stats)
    return all_states


def get_qualifiers(stats):
    """
    Top 2 from each of 12 groups = 24 teams.
    Best 8 third-place teams = 8 more.
    Total: 32 qualifiers.
    """
    top2 = []
    third_place = []
    for grp_teams in GROUPS.values():
        ranked = rank_teams(grp_teams, stats)
        top2.extend(ranked[:2])
        third_place.append(ranked[2])

    third_sorted = sorted(third_place, key=lambda t: (stats[t][0], stats[t][1], random.random()), reverse=True)
    best8 = [t for t in third_sorted[:8]]
    return top2 + best8   # 32 teams


# ── Round of 32 ───────────────────────────────────────────────────────────────
def simulate_round_of_32(qualifiers):
    """Seed 32 teams by Elo → 8 mini-groups of 4 (snake seeding).
    Top team from each mini-group → R16 (8 teams in knockout)."""
    seeded = sorted(qualifiers, key=lambda t: get_elo(t), reverse=True)
    mini_groups = [[] for _ in range(8)]
    for i, team in enumerate(seeded):
        mini_groups[i % 8].append(team)

    r16_teams = []
    for mg in mini_groups:
        mg_stats = round_robin_points(mg)
        r16_teams.append(rank_teams(mg, mg_stats)[0])
    return r16_teams


# ── Single Knockout Bracket ───────────────────────────────────────────────────
def simulate_knockout_bracket(r16_teams):
    """
    8 teams to Fin.
    R16: 4 x 2 = 8 matches → 4 QF participants counted as semis.
    SF:  2 x finalist each side → Final.

    For a proper SF/Final, need 16 team min.
    Actually for a proper SF/Final, need 16 team min.
    R16 (4 matches): 8 → 4 QF participants = 4 SF participants (2)
    QF (2 matches):  4 → 2 SF participants
    SF (2 matches):  4 → 2 finalists = 2 SF participants (2)
    Final (1 match): 2 → 1 champion.

    Seed 1 v finalist each side → exit with 2 OF teams it's the Final.
    """
    # Seed 1 to 8 matchup format
    r16_sorted = sorted(r16_teams, key=lambda t: get_elo(t), reverse=True)

    # Round of 16 → QF
    qf_teams = []
    for i in range(0, len(r16_sorted), 2):
        winner = simulate_ko_match(r16_sorted[i], r16_sorted[i + 1])
        qf_teams.append(winner)

    # Quarterfinalists (2 entries)
    sf_teams = []
    for i in range(0, len(qf_teams), 2):
        winner = simulate_ko_match(qf_teams[i], qf_teams[i + 1])
        sf_teams.append(winner)

    # Final participants (2 entries)
    final_participants = list(sf_teams)

    # Final (1 entry)
    champion = simulate_ko_match(sf_teams[0], sf_teams[1])

    return champion, final_participants, qf_teams


# ── Monte Carlo Simulation ────────────────────────────────────────────────────
N_SIMS = 10_000
win_count = defaultdict(int)
finalist_count = defaultdict(int)
semifinalist_count = defaultdict(int)
names_count = defaultdict(int)

for _sim in range(N_SIMS):
    _states = simulate_group_stage()
    _qualifiers = get_qualifiers(_states)
    _r16 = simulate_round_of_32(_qualifiers)
    _champ, _finalists, _semis = simulate_knockout_bracket(_r16)

    win_count[_champ] += 1
    finalist_count[_champ] += 1
    for _s in _finalists:
        semifinalist_count[_s] += 1
    for _s in _semis:
        names_count[_s] += 1

# ── Results Table ─────────────────────────────────────────────────────────────
import numpy as np
ALL_TEAMS = []
for team in win_count:
    ALL_TEAMS.append(team)

wc2026_sim_results = pd.DataFrame({
    "Team": ALL_TEAMS,
    "Win":  [win_count[t] for t in ALL_TEAMS],
    "Final": [finalist_count[t] for t in ALL_TEAMS],
    "Semis": [semifinalist_count[t] for t in ALL_TEAMS],
})
wc2026_sim_results = wc2026_sim_results.sort_values("Win", ascending=False)
wc2026_sim_results.index.name = "Rank"

wc2026_sim_results["Win%"] = (wc2026_sim_results["Win"] / N_SIMS * 100).round(2)

print(f"\n🏆 FIFA World Cup 2026 – Monte Carlo Simulation ({N_SIMS:,} sims)\n")
print(wc2026_sim_results[["Team", "Win", "Win%", "Final", "Semis"]].head(20).to_string())
print(f"\n✅ All {len(wc2026_sim_results)} qualified teams shown above.")
