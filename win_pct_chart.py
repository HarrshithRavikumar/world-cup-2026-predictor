import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

# ── Continent mapping ─────────────────────────────────────────────────────────
CONTINENT_MAP = {
    # Europe
    "Spain":           "Europe",
    "France":          "Europe",
    "England":         "Europe",
    "Germany":         "Europe",
    "Portugal":        "Europe",
    "Netherlands":     "Europe",
    "Belgium":         "Europe",
    "Italy":           "Europe",
    "Switzerland":     "Europe",
    "Croatia":         "Europe",
    "Denmark":         "Europe",
    "Switzerland":     "Europe",
    "Serbia":          "Europe",
    "Poland":          "Europe",
    "Turkey":          "Europe",
    "Ukraine":         "Europe",
    "Austria":         "Europe",
    "Scotland":        "Europe",
    "Hungary":         "Europe",
    "Czech Republic":  "Europe",
    "Slovenia":        "Europe",
    "Albania":         "Europe",
    "Romania":         "Europe",
    "Greece":          "Europe",
    "Georgia":         "Europe",
    # South America
    "Argentina":       "South America",
    "Brazil":          "South America",
    "Uruguay":         "South America",
    "Colombia":        "South America",
    "Ecuador":         "South America",
    "Chile":           "South America",
    "Paraguay":        "South America",
    "Bolivia":         "South America",
    "Venezuela":       "South America",
    "Peru":            "South America",
    # Africa
    "Morocco":         "Africa",
    "Senegal":         "Africa",
    "Nigeria":         "Africa",
    "Cameroon":        "Africa",
    "Ghana":           "Africa",
    "Egypt":           "Africa",
    "Algeria":         "Africa",
    "Tunisia":         "Africa",
    "South Africa":    "Africa",
    "Mali":            "Africa",
    "DR Congo":        "Africa",
    "Ivory Coast":     "Africa",
    "Benin":           "Africa",
    # Asia
    "Japan":           "Asia",
    "South Korea":     "Asia",
    "Iran":            "Asia",
    "Saudi Arabia":    "Asia",
    "Qatar":           "Asia",
    "Australia":       "Asia",
    "Iraq":            "Asia",
    "Afghanistan":     "Asia",
    "Jordan":          "Asia",
    "China PR":        "Asia",
    "Indonesia":       "Asia",
    "Bahrain":         "Asia",
    # CONCACAF
    "United States":   "CONCACAF",
    "Mexico":          "CONCACAF",
    "Canada":          "CONCACAF",
    "Jamaica":         "CONCACAF",
    "Panama":          "CONCACAF",
    "Honduras":        "CONCACAF",
    "Costa Rica":      "CONCACAF",
    "Cuba":            "CONCACAF",
    # Oceania
    "New Zealand":     "Oceania",
}

# ── Continent colors (Zerve palette) ─────────────────────────────────────────
CONTINENT_COLORS = {
    "Europe":        "#A1C9F4",   # light blue
    "South America": "#FFB8B0",   # orange
    "Africa":        "#8DE5A1",   # green
    "Asia":          "#8FDBFF",   # teal
    "CONCACAF":      "#D0BBFF",   # lavender
    "Oceania":       "#FFFEA3",   # yellow
}

# ── Prepare data ──────────────────────────────────────────────────────────────
# NOTE: wc2026_sim_results must be imported or run wc2026_simulation.py first
try:
    from wc2026_simulation import wc2026_sim_results, N_SIMS
except ImportError:
    raise ImportError("Run wc2026_simulation.py first to generate wc2026_sim_results.")

chart_df = wc2026_sim_results.copy().reset_index(drop=True)
chart_df["Continent"] = chart_df["Team"].map(CONTINENT_MAP).fillna("Other")
chart_df["Color"] = chart_df["Continent"].map(CONTINENT_COLORS).fillna("#909090")
chart_df = chart_df.sort_values("Win%", ascending=True).reset_index(drop=True)

# ── Figure ────────────────────────────────────────────────────────────────────
BG        = "#323120"
TEXT      = "#F2E1d2"
SECONDARY = "#F09094"

fig, ax = plt.subplots(figsize=(12, 9))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

bars = ax.barh(
    chart_df["Team"],
    chart_df["Win%"],
    color=chart_df["Color"],
    height=0.65,
    edgecolor="none",
)

# ── Value labels on bars ──────────────────────────────────────────────────────
for bar, val in zip(bars, chart_df["Win%"]):
    ax.text(
        bar.get_width() + 0.08,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.2f}%",
        ha="left",
        color=TEXT,
        fontsize=7.5,
        fontweight="bold",
    )

# ── Axis styling ──────────────────────────────────────────────────────────────
ax.set_xlabel("Win Probability (%)", color=SECONDARY, fontsize=11, labelpad=10)
ax.set_title(
    f"FIFA World Cup 2026 – Who Wins? ({N_SIMS:,} Simulations)",
    color=TEXT,
    fontsize=14,
    fontweight="bold",
    pad=10,
)

ax.tick_params(colors=SECONDARY, labelsize=10)
for spine in ax.spines.values():
    spine.set_visible(False)

ax.xaxis.set_tick_params(colors=SECONDARY)
ax.set_xlim(0, chart_df["Win%"].max() * 1.22)
ax.xaxis.grid(True, color="#333348", linewidth=0.6, linestyle="--")
ax.xaxis.set_ticklabels(chart_df["Team"], color=TEXT, fontsize=10)

# ── Legend ────────────────────────────────────────────────────────────────────
present_continents = chart_df["Continent"].unique()
legend_handles = [
    mpatches.Patch(facecolor=CONTINENT_COLORS.get(c, "#909090"), label=c, edgecolor="none")
    for c in ["Europe", "South America", "Africa", "Asia", "CONCACAF", "Oceania"]
    if c in present_continents
]
legend = ax.legend(
    handles=legend_handles,
    title="Continent",
    title_fontsize=10,
    fontsize=9,
    loc="lower right",
    framealpha=0.15,
    edgecolor="#444",
    labelcolor=TEXT,
    facecolor="20%2e%",
)
legend.get_title().set_color(SECONDARY)

plt.tight_layout()
plt.savefig("charts/win_pct_chart.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.show()
print("✅ Saved: charts/win_pct_chart.png")
