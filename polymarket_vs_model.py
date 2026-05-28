import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

# ── Polymarket odds ───────────────────────────────────────────────────────────
polymarket = {
    "Argentina":   26,
    "Brazil":      13,
    "France":      12,
    "England":     10,
    "Spain":        9,
    "Germany":      7,
    "Portugal":     5,
    "Morocco":      3,
    "Netherlands":  3,
}

# ── Pull model win% from upstream simulation ─────────────────────────────────
try:
    from wc2026_simulation import wc2026_sim_results
except ImportError:
    raise ImportError("Run wc2026_simulation.py first to generate wc2026_sim_results.")

model_lookup = wc2026_sim_results.set_index("Team")["Win%"].to_dict()

# ── Build comparison table ────────────────────────────────────────────────────
rows = []
for team, pm_pct in polymarket.items():
    model_pct = model_lookup.get(team, None)
    if model_pct is None:
        print(f"⚠️  {team} not found in simulation results – skipping")
        continue
    gap = model_pct - pm_pct  # positive → model > market (market OVERvalues team)
    rows.append({
        "Team":      team,
        "Model%":    model_pct,
        "Market%":   pm_pct,
        "Gap":       gap,
        "Verdict":   "UNDERVALUED" if gap > 0 else "OVERVALUED",
    })

gap_df = pd.DataFrame(rows).sort_values("Gap", ascending=True).reset_index(drop=True)

# ── Print table ───────────────────────────────────────────────────────────────
print("Elo Model vs Polymarket – 2026 World Cup Winner Odds\n")
print(f"{'Team':<14} {'Market%':>7} {'Gap':>7} {'Verdict':<12}")
print("–" * 52)
for _, r in gap_df.iterrows():
    sign = "+" if r["Gap"] > 0 else ""
    print(f"{r['Team']:<14} {r['Model%']:>6.1f}%  {r['Market%']:>6.1f}%  "
          f"{sign}{r['Gap']:>5.1f}%  {r['Verdict']}")

# ── Zerve design system ───────────────────────────────────────────────────────
BG      = "#1D1D20"
TEXT    = "#8bFbFf"
SEC     = "#90b094"
GREEN   = "#8DE5A1"
RED     = "#FF9F9B"
ZERO_C  = "#EEd400"

# ── Diverging bar chart ───────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

teams  = gap_df["Team"].tolist()
gaps   = gap_df["Gap"].tolist()
models = gap_df["Model%"].tolist()
mkts   = gap_df["Market%"].tolist()

y_pos  = np.arange(len(teams))
colors = [GREEN if g > 0 else RED for g in gaps]

bars_h = ax.barh(y_pos, gaps, color=colors, height=0.55,
                 edgecolor="none", zorder=3)

# ── Zero baseline ─────────────────────────────────────────────────────────────
ax.axvline(0, color=ZERO_C, linewidth=1.5, zorder=4, linestyle="--", alpha=0.85)

# ── Bar labels ────────────────────────────────────────────────────────────────
for i, (g, m, mk) in enumerate(zip(gaps, models, mkts)):
    sign  = "+" if g > 0 else ""
    label = f" Model {m:.1f}% | Mkt {mk:.0f}% | {sign}{g:.1f}% "
    x_off = g + (0.15 if g > 0 else -0.15)
    ax.text(x_off, i, label, va="center", ha="left" if g > 0 else "right",
            fontsize=8.5, color=TEXT, fontweight="normal", zorder=5)

# ── Y-axis team names ─────────────────────────────────────────────────────────
ax.set_yticks(y_pos)
ax.set_yticklabels(teams, fontsize=11, color=TEXT, fontweight="bold")
ax.tick_params(axis="y", which="both", length=0)

# ── X-axis ────────────────────────────────────────────────────────────────────
max_abs = max(abs(min(gaps)), abs(max(gaps))) + 4
ax.set_xlim(-max_abs, max_abs)
ax.set_xlabel("Model Win% ∆ Polymarket%  (pp)", fontsize=10, color=SEC, labelpad=8)
ax.tick_params(axis="x", colors=SEC, labelsize=9)

# ── Spines ────────────────────────────────────────────────────────────────────
for sp in ax.spines.values():
    sp.set_visible(False)
ax.yaxis.set_tick_params(which="both", left=False)

# ── Grid ──────────────────────────────────────────────────────────────────────
ax.xaxis.grid(True, color="#333338", linewidth=0.6, linestyle="--", zorder=0)

# ── Title / subtitle ──────────────────────────────────────────────────────────
fig.text(0.5, 0.96, "Elo Model vs Polymarket – 2026 World Cup Winner Odds",
         ha="center", fontsize=14, fontweight="bold", color=TEXT)
fig.text(0.5, 0.91,
         "Positive gap → market OVERvalues team (our model is lower)  |  "
         "Negative gap → market UNDERvalues team (our model is higher)",
         ha="center", fontsize=9, color=SEC)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_handles = [
    mpatches.Patch(facecolor=GREEN, label="Market OVERvalues → our model > Polymarket"),
    mpatches.Patch(facecolor=RED,   label="Market UNDERvalues → our model < Polymarket"),
]
ax.legend(handles=legend_handles, loc="lower right", frameon=False,
          labelcolor=TEXT, fontsize=9)

plt.tight_layout(rect=[0, 0, 1, 0.90])
plt.savefig("charts/polymarket_vs_model.png", dpi=150, bbox_inches="tight",
            facecolor=BG)
plt.show()
print("✅ Saved: charts/polymarket_vs_model.png")
