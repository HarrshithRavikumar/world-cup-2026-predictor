import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict

st.set_page_config(page_title="WC 2026 Predictor", page_icon="🏆", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600&display=swap');
html, body, [class*="css"] { background-color: #0f0f0f; color: #f0ede6; }
h1, h2, h3 { font-family: 'Bebas Neue', sans-serif; letter-spacing: 2px; }
.stButton>button {
    background: linear-gradient(135deg, #c8a84b, #f0d060);
    color: #0f0f0f; font-family: 'Bebas Neue', sans-serif;
    font-size: 1.2rem; letter-spacing: 2px; border: none;
    padding: 0.6rem 2.5rem; border-radius: 2px; width: 100%;
}
.stButton>button:hover { opacity: 0.85; }
.metric-card {
    background: #1a1a1a; border-left: 3px solid #c8a84b;
    padding: 1rem 1.2rem; border-radius: 2px; margin-bottom: 0.5rem;
}
.metric-card .rank { font-size: 0.75rem; color: #888; letter-spacing: 1px; }
.metric-card .team { font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; letter-spacing: 1px; }
.metric-card .pct  { font-size: 1.1rem; color: #c8a84b; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── CONFIRMED WC 2026 Groups (Draw: Dec 5, 2025) ──────────────────────────────
GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

CONTINENT_MAP = {
    "Mexico": "CONCACAF", "Canada": "CONCACAF", "United States": "CONCACAF",
    "Haiti": "CONCACAF", "Curacao": "CONCACAF", "Panama": "CONCACAF",
    "Costa Rica": "CONCACAF",
    "Brazil": "South America", "Argentina": "South America", "Colombia": "South America",
    "Uruguay": "South America", "Ecuador": "South America", "Paraguay": "South America",
    "Spain": "Europe", "France": "Europe", "England": "Europe", "Germany": "Europe",
    "Netherlands": "Europe", "Portugal": "Europe", "Belgium": "Europe",
    "Croatia": "Europe", "Switzerland": "Europe", "Sweden": "Europe",
    "Scotland": "Europe", "Norway": "Europe", "Austria": "Europe",
    "Czechia": "Europe", "Bosnia and Herzegovina": "Europe", "Turkey": "Europe",
    "Morocco": "Africa", "Senegal": "Africa", "Ivory Coast": "Africa",
    "South Africa": "Africa", "Egypt": "Africa", "Tunisia": "Africa",
    "Ghana": "Africa", "DR Congo": "Africa", "Cape Verde": "Africa",
    "Algeria": "Africa",
    "Japan": "Asia", "South Korea": "Asia", "Iran": "Asia",
    "Saudi Arabia": "Asia", "Australia": "Asia", "Qatar": "Asia",
    "Iraq": "Asia", "Jordan": "Asia", "Uzbekistan": "Asia", "New Zealand": "Asia",
}

CONTINENT_COLORS = {
    "Europe": "#A1C9F4", "South America": "#FFB8B0", "Africa": "#8DE5A1",
    "Asia": "#8FDBFF", "CONCACAF": "#D0BBFF", "Other": "#888888",
}

POLYMARKET = {
    "Argentina": 26, "Brazil": 13, "France": 12, "England": 10,
    "Spain": 9, "Germany": 7, "Portugal": 5, "Morocco": 3, "Netherlands": 3,
}

DEFAULT_ELO = 1500
N_K = 24

@st.cache_data
def build_elo():
    df = pd.read_csv("data/results.csv", parse_dates=["date"])
    df = df[df["date"].dt.year >= 2019].sort_values("date")
    elo = {}
    def get(t): return elo.get(t, DEFAULT_ELO)
    def exp(a, b): return 1 / (1 + 10 ** ((b - a) / 400))
    for _, row in df.iterrows():
        za, zb = get(row.home_team), get(row.away_team)
        ea = exp(za, zb)
        if row.home_score > row.away_score:   sa, sb = 1.0, 0.0
        elif row.home_score < row.away_score: sa, sb = 0.0, 1.0
        else:                                  sa, sb = 0.5, 0.5
        elo[row.home_team] = za + N_K * (sa - ea)
        elo[row.away_team] = zb + N_K * (sb - (1 - ea))
    return elo

def run_simulation(n_sims, elo):
    def get(t): return elo.get(t, DEFAULT_ELO)
    def exp(a, b): return 1 / (1 + 10 ** ((b - a) / 400))
    def match_draw(a, b, dp=0.22):
        p = exp(get(a), get(b)) * (1 - dp)
        r = random.random()
        if r < p: return (1, 0)
        elif r < p + dp: return (1, 1)
        else: return (0, 1)
    def ko(a, b): return a if random.random() < exp(get(a), get(b)) else b
    def rr(teams):
        stats = {t: [0, 0] for t in teams}
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                gm, gn = match_draw(teams[i], teams[j])
                if gm > gn:   stats[teams[i]][0] += 3; stats[teams[i]][1] += 1
                elif gm < gn: stats[teams[j]][0] += 3; stats[teams[j]][1] += 1
                else:         stats[teams[i]][0] += 1; stats[teams[j]][0] += 1
        return stats
    def rank(teams, stats):
        return sorted(teams, key=lambda t: (stats[t][0], stats[t][1], random.random()), reverse=True)

    win_count = defaultdict(int)
    final_count = defaultdict(int)
    semi_count = defaultdict(int)

    for _ in range(n_sims):
        all_stats = {}
        for grp in GROUPS.values():
            all_stats.update(rr(grp))
        top2, third = [], []
        for grp in GROUPS.values():
            r = rank(grp, all_stats)
            top2.extend(r[:2]); third.append(r[2])
        best8 = sorted(third, key=lambda t: (all_stats[t][0], all_stats[t][1], random.random()), reverse=True)[:8]
        qualifiers = top2 + best8
        seeded = sorted(qualifiers, key=lambda t: get(t), reverse=True)
        mgs = [[] for _ in range(8)]
        for i, t in enumerate(seeded): mgs[i % 8].append(t)
        r16 = [rank(mg, rr(mg))[0] for mg in mgs]
        r16s = sorted(r16, key=lambda t: get(t), reverse=True)
        qf = [ko(r16s[i], r16s[i+1]) for i in range(0, len(r16s), 2)]
        sf = [ko(qf[i], qf[i+1]) for i in range(0, len(qf), 2)]
        champ = ko(sf[0], sf[1])
        win_count[champ] += 1
        for t in sf: final_count[t] += 1
        for t in qf: semi_count[t] += 1

    all_teams = list(win_count.keys())
    df = pd.DataFrame({
        "Team": all_teams,
        "Win":  [win_count[t] for t in all_teams],
        "Final": [final_count[t] for t in all_teams],
        "Semis": [semi_count[t] for t in all_teams],
    })
    df["Win%"]   = (df["Win"]   / n_sims * 100).round(2)
    df["Final%"] = (df["Final"] / n_sims * 100).round(2)
    df["Semi%"]  = (df["Semis"] / n_sims * 100).round(2)
    df = df.sort_values("Win%", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def make_win_chart(df):
    BG, TEXT, SEC = "#0f0f0f", "#f0ede6", "#c8a84b"
    chart_df = df.copy().sort_values("Win%", ascending=True)
    chart_df["Color"] = chart_df["Team"].map(lambda t: CONTINENT_COLORS.get(CONTINENT_MAP.get(t, "Other"), "#888"))
    fig, ax = plt.subplots(figsize=(10, max(6, len(chart_df) * 0.35)))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    bars = ax.barh(chart_df["Team"], chart_df["Win%"], color=chart_df["Color"], height=0.6, edgecolor="none")
    for bar, val in zip(bars, chart_df["Win%"]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"{val:.1f}%", va="center", color=TEXT, fontsize=7.5, fontweight="bold")
    ax.set_xlabel("Win Probability (%)", color=SEC, fontsize=10)
    ax.set_title("🏆 Who Wins WC 2026?", color=TEXT, fontsize=14, fontweight="bold", pad=10)
    ax.tick_params(colors=TEXT, labelsize=8)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.xaxis.grid(True, color="#222", linewidth=0.5, linestyle="--")
    ax.set_xlim(0, chart_df["Win%"].max() * 1.25)
    handles = [mpatches.Patch(facecolor=c, label=k, edgecolor="none")
               for k, c in CONTINENT_COLORS.items() if k != "Other"]
    ax.legend(handles=handles, loc="lower right", frameon=False, labelcolor=TEXT, fontsize=8)
    plt.tight_layout()
    return fig

def make_polymarket_chart(df):
    BG, TEXT, SEC = "#0f0f0f", "#f0ede6", "#888"
    GREEN, RED, GOLD = "#8DE5A1", "#FF9F9B", "#c8a84b"
    model_lu = df.set_index("Team")["Win%"].to_dict()
    rows = []
    for team, pm in POLYMARKET.items():
        mp = model_lu.get(team)
        if mp is None: continue
        rows.append({"Team": team, "Model%": mp, "Market%": pm, "Gap": mp - pm})
    gdf = pd.DataFrame(rows).sort_values("Gap", ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    colors = [GREEN if g > 0 else RED for g in gdf["Gap"]]
    y = np.arange(len(gdf))
    ax.barh(y, gdf["Gap"], color=colors, height=0.55, edgecolor="none", zorder=3)
    ax.axvline(0, color=GOLD, linewidth=1.5, linestyle="--", alpha=0.8, zorder=4)
    for i, (_, row) in enumerate(gdf.iterrows()):
        sign = "+" if row["Gap"] > 0 else ""
        label = f" {row['Model%']:.1f}% model | {row['Market%']:.0f}% mkt | {sign}{row['Gap']:.1f}pp "
        x = row["Gap"] + (0.15 if row["Gap"] > 0 else -0.15)
        ax.text(x, i, label, va="center", ha="left" if row["Gap"] > 0 else "right", fontsize=8, color=TEXT)
    ax.set_yticks(y); ax.set_yticklabels(gdf["Team"], color=TEXT, fontsize=10, fontweight="bold")
    ax.tick_params(axis="y", length=0); ax.tick_params(axis="x", colors=SEC, labelsize=8)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.xaxis.grid(True, color="#222", linewidth=0.5, linestyle="--", zorder=0)
    max_abs = max(abs(gdf["Gap"].min()), abs(gdf["Gap"].max())) + 4
    ax.set_xlim(-max_abs, max_abs)
    ax.set_xlabel("Model Win% − Polymarket%  (pp)", color=SEC, fontsize=9)
    ax.set_title("Elo Model vs Polymarket Odds", color=TEXT, fontsize=13, fontweight="bold")
    handles = [mpatches.Patch(facecolor=GREEN, label="Market OVERvalues (model lower)"),
               mpatches.Patch(facecolor=RED,   label="Market UNDERvalues (model higher)")]
    ax.legend(handles=handles, frameon=False, labelcolor=TEXT, fontsize=8, loc="lower right")
    plt.tight_layout()
    return fig

def make_groups_table():
    rows = []
    for grp, teams in GROUPS.items():
        for t in teams:
            rows.append({"Group": f"Group {grp}", "Team": t,
                         "Confederation": CONTINENT_MAP.get(t, "Other")})
    return pd.DataFrame(rows)

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("# 🏆 FIFA WORLD CUP 2026 PREDICTOR")
st.markdown("##### Monte Carlo simulation · Elo ratings · 48 confirmed teams")
st.divider()

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### ⚙️ Settings")
    n_sims = st.slider("Simulations", min_value=1000, max_value=50000, value=10000, step=1000)
    st.caption("More sims = more accurate, but slower")
    run = st.button("▶  RUN SIMULATION")
    st.divider()
    st.markdown("### 🗂️ Groups")
    st.dataframe(make_groups_table(), use_container_width=True, height=500, hide_index=True)

with col2:
    if run or "results" in st.session_state:
        if run:
            with st.spinner("Building Elo ratings from match history..."):
                elo = build_elo()
            with st.spinner(f"Running {n_sims:,} simulations..."):
                results = run_simulation(n_sims, elo)
            st.session_state["results"] = results
            st.session_state["elo"] = elo
        else:
            results = st.session_state["results"]
            elo = st.session_state["elo"]

        st.markdown("### 🥇 Top Contenders")
        p1, p2, p3 = st.columns(3)
        for col, (i, emoji) in zip([p1, p2, p3], [(0,"🥇"),(1,"🥈"),(2,"🥉")]):
            row = results.iloc[i]
            col.markdown(f"""
            <div class="metric-card">
                <div class="rank">{emoji} #{i+1}</div>
                <div class="team">{row['Team']}</div>
                <div class="pct">{row['Win%']:.1f}% to win</div>
                <div style="font-size:0.8rem;color:#888">Final: {row['Final%']:.1f}%  |  Semis: {row['Semi%']:.1f}%</div>
            </div>""", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Win Chart", "📈 vs Polymarket", "📋 Full Table", "🎯 Elo Ratings"])

        with tab1:
            st.pyplot(make_win_chart(results))
        with tab2:
            st.pyplot(make_polymarket_chart(results))
        with tab3:
            st.dataframe(
                results[["Team", "Win%", "Final%", "Semi%"]].style.background_gradient(subset=["Win%"], cmap="YlOrRd"),
                use_container_width=True, height=500,
            )
        with tab4:
            elo_df = pd.Series(elo, name="Elo Rating").sort_values(ascending=False).head(50).round(1)
            elo_df.index.name = "Team"
            st.dataframe(elo_df.reset_index(), use_container_width=True, height=500)
    else:
        st.info("👈 Set your simulation count and hit **RUN SIMULATION** to get started.")
