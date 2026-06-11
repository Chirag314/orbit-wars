"""
Orbit Wars Competition Dashboard
Run: python3 dashboard.py  →  generates dashboard.png
Update the DATA section below when adding new agents or submissions.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import numpy as np
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# DATA — update this section when adding agents / new scores
# ═══════════════════════════════════════════════════════════════════════════

TEAM_NAME   = "cid007 (Chirag Desai)"
COMPETITION = "ORBIT WARS"
DEADLINE    = "Jun 23, 2026"
TOTAL_TEAMS = 3676

# All submission scores in chronological order
SUBMISSIONS = [
    # (date_str,  label,       score,   architecture)
    ("Jun 02", "v1_starter",   600,    "heuristic"),
    ("Jun 02", "v1_starter",   692,    "heuristic"),
    ("Jun 02", "v1_starter",   947,    "heuristic"),
    ("Jun 02", "v1_starter",   1054,   "heuristic"),
    ("Jun 03", "v1_starter",   1072,   "heuristic"),   # peak
    ("Jun 03", "v3_pascal",    736,    "heuristic"),
    ("Jun 03", "v5_hybrid",    948,    "heuristic"),
    ("Jun 04", "v6_2p",        1008,   "heuristic"),
    ("Jun 06", "v7_expand",    1001,   "heuristic"),
    ("Jun 07", "v8_realsim",   990,    "heuristic"),
    ("Jun 09", "v9_producer",  1167,   "orbit_lite"),
    ("Jun 09", "v9b",          1197,   "orbit_lite"),  # peak ever
    ("Jun 10", "v10_tuned",    1113,   "orbit_lite"),  # still converging
]

# Per-agent best scores (for agent comparison chart)
AGENTS = [
    # (name,          best_score, status,    architecture)
    ("v1_starter",    1072,       "inactive", "heuristic"),
    ("v2_roman",       980,       "inactive", "heuristic"),
    ("v3_pascal",      736,       "inactive", "heuristic"),
    ("v5_hybrid",      948,       "inactive", "heuristic"),
    ("v6_2p",         1008,       "inactive", "heuristic"),
    ("v7_expand",     1001,       "inactive", "heuristic"),
    ("v8_realsim",     990,       "inactive", "heuristic"),
    ("v9_producer",   1167,       "active",   "orbit_lite"),
    ("v9b",           1197,       "active",   "orbit_lite"),
    ("v10_tuned",     1113,       "converging","orbit_lite"),
]

# Score climb per active agent (for "how each bot climbed" chart)
CLIMBS = {
    "v1_starter": [
        ("Jun02_0h", 600), ("Jun02_1h", 692), ("Jun02_4h", 947),
        ("Jun02_8h", 1054), ("Jun03",   1072),
    ],
    "v9_producer": [
        ("Jun09_0h", 600), ("Jun09_2h", 850), ("Jun09_5h", 1050),
        ("Jun09_8h", 1167), ("Jun10",   1167),
    ],
    "v9b": [
        ("Jun09_8h", 600), ("Jun09_12h", 900), ("Jun09_18h", 1141),
        ("Jun10_4h", 1197), ("Jun10_now", 1139),
    ],
    "v10_tuned": [
        ("Jun10_0h", 600), ("Jun10_4h", 900), ("Jun10_now", 1113),
    ],
}

# LB score distribution (approximate, from top-200 snapshot)
LB_SCORES_SAMPLE = [
    1679, 1593, 1579, 1569, 1556, 1536, 1530, 1521, 1520, 1514,
    1513, 1511, 1510, 1510, 1508, 1506, 1506, 1499, 1492, 1488,
    1473, 1465, 1462, 1461, 1457, 1453, 1448, 1444, 1440, 1436,
    1430, 1427, 1425, 1420, 1416, 1410, 1404, 1400, 1396, 1392,
    1388, 1385, 1382, 1376, 1372, 1368, 1365, 1361, 1358, 1356,
    1353, 1349, 1344, 1340, 1337, 1334, 1330, 1327, 1324, 1320,
    1317, 1313, 1310, 1306, 1302, 1298, 1294, 1290, 1286, 1282,
    1278, 1274, 1270, 1266, 1262, 1258, 1254, 1250, 1246, 1242,
    1239, 1235, 1231, 1228, 1226, 1223, 1220, 1217, 1214, 1211,
    1208, 1205, 1202, 1199, 1196, 1193, 1190, 1187, 1184, 1181,
] + list(np.linspace(1180, 980, 100)) + list(np.linspace(980, 800, 100)) + list(np.linspace(800, 600, 100))
LB_SCORES_SAMPLE = sorted(LB_SCORES_SAMPLE, reverse=True)

# Medal thresholds
GOLD_RANK   = 37
SILVER_RANK = 184
BRONZE_RANK = 366
OUR_BEST    = 1197   # peak ever
OUR_CURRENT = 1167
OUR_RANK    = 201

# ═══════════════════════════════════════════════════════════════════════════
# STYLE
# ═══════════════════════════════════════════════════════════════════════════

BG       = "#0d1117"
CARD_BG  = "#161b22"
TEXT     = "#e6edf3"
DIM_TEXT = "#8b949e"
GOLD_C   = "#f0c040"
SILVER_C = "#c0c8d8"
BRONZE_C = "#cd7f32"
ORB_BLUE = "#58a6ff"
ORB_GRN  = "#3fb950"
ORB_RED  = "#f85149"
ORB_PUR  = "#bc8cff"
ORB_ORG  = "#ffa657"

ARCH_COLORS = {"heuristic": "#8b949e", "orbit_lite": ORB_BLUE}
STATUS_COLORS = {"inactive": "#484f58", "active": ORB_GRN, "converging": ORB_ORG}

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    CARD_BG,
    "axes.edgecolor":    "#30363d",
    "axes.labelcolor":   TEXT,
    "xtick.color":       DIM_TEXT,
    "ytick.color":       DIM_TEXT,
    "text.color":        TEXT,
    "grid.color":        "#21262d",
    "grid.linewidth":    0.6,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
    "axes.spines.bottom":False,
})

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(20, 34), facecolor=BG)

# Outer grid: header + 6 rows of charts
outer = gridspec.GridSpec(
    9, 1, figure=fig, hspace=0.55,
    top=0.97, bottom=0.02, left=0.04, right=0.97,
    height_ratios=[0.6, 1.2, 1.2, 1.2, 1.2, 1.0, 1.0, 1.1, 1.0],
)

def card_ax(spec, title, subtitle=""):
    ax = fig.add_subplot(spec)
    ax.set_facecolor(CARD_BG)
    for sp in ax.spines.values():
        sp.set_visible(False)
    if title:
        ax.set_title(title, loc="left", fontsize=11, fontweight="bold",
                     color=TEXT, pad=14)
    if subtitle:
        ax.text(0, 1.04, subtitle, transform=ax.transAxes,
                fontsize=7.5, color=DIM_TEXT, va="bottom")
    return ax

# ═══════════════════════════════════════════════════════════════════════════
# 0. HEADER
# ═══════════════════════════════════════════════════════════════════════════
ax_hdr = fig.add_subplot(outer[0])
ax_hdr.set_facecolor(BG)
for sp in ax_hdr.spines.values():
    sp.set_visible(False)
ax_hdr.set_xticks([]); ax_hdr.set_yticks([])

ax_hdr.text(0.0, 0.92, COMPETITION, fontsize=26, fontweight="bold",
            color=GOLD_C, transform=ax_hdr.transAxes, va="top")
ax_hdr.text(0.0, 0.52, f"Competition Recap  ·  {TEAM_NAME}",
            fontsize=11, color=DIM_TEXT, transform=ax_hdr.transAxes, va="top")

# Stat boxes
stats = [
    ("BEST SCORE", f"{OUR_BEST:,}"),
    ("CURRENT",    f"{OUR_CURRENT:,}"),
    ("RANK",       f"#{OUR_RANK}"),
    ("PERCENTILE", f"Top {OUR_RANK/TOTAL_TEAMS*100:.1f}%"),
    ("AGENTS",     str(len(AGENTS))),
    ("DEADLINE",   DEADLINE),
]
for i, (label, val) in enumerate(stats):
    x = 0.32 + i * 0.115
    ax_hdr.text(x, 0.85, val, fontsize=14, fontweight="bold",
                color=GOLD_C if i == 0 else ORB_BLUE,
                transform=ax_hdr.transAxes, ha="center", va="top")
    ax_hdr.text(x, 0.42, label, fontsize=7, color=DIM_TEXT,
                transform=ax_hdr.transAxes, ha="center", va="top")

# Bronze/Silver status
ax_hdr.text(1.0, 0.92, "BRONZE  [OK]  CONFIRMED",
            fontsize=10, color=BRONZE_C, transform=ax_hdr.transAxes,
            ha="right", va="top", fontweight="bold")
ax_hdr.text(1.0, 0.52, f"Silver target: need ~1226  (+{1226-OUR_CURRENT} pts)",
            fontsize=9, color=SILVER_C, transform=ax_hdr.transAxes,
            ha="right", va="top")

# ═══════════════════════════════════════════════════════════════════════════
# 1. SCORE JOURNEY — bar + line
# ═══════════════════════════════════════════════════════════════════════════
ax1 = card_ax(outer[1],
              "Every agent you shipped",
              "Best score per submission, coloured by architecture")
dates  = [s[0] for s in SUBMISSIONS]
scores = [s[2] for s in SUBMISSIONS]
archs  = [s[3] for s in SUBMISSIONS]
xs     = np.arange(len(scores))
colors_bar = [ORB_BLUE if a == "orbit_lite" else "#484f58" for a in archs]
bars = ax1.bar(xs, scores, color=colors_bar, width=0.65, zorder=3,
               alpha=0.85)
# highlight peak
peak_i = scores.index(max(scores))
bars[peak_i].set_color(GOLD_C)
bars[peak_i].set_zorder(5)

# Reference lines
for score, color, label in [(1226, SILVER_C, "Silver ~1226"),
                              (1100, BRONZE_C, "Bronze ~1100"),
                              (1072, "#484f58", "v1 ceiling 1072")]:
    ax1.axhline(score, color=color, linewidth=0.9, linestyle="--", alpha=0.6)
    ax1.text(len(xs)-0.3, score+8, label, color=color, fontsize=7, va="bottom", ha="right")

ax1.set_xticks(xs)
ax1.set_xticklabels([f"{s[1]}" for s in SUBMISSIONS], rotation=45,
                     ha="right", fontsize=7.5)
ax1.set_ylim(400, 1350)
ax1.set_ylabel("LB Score", fontsize=8)
ax1.yaxis.grid(True, zorder=0); ax1.set_axisbelow(True)
ax1.text(peak_i, max(scores)+18, f"★ {max(scores)}", ha="center",
         fontsize=8, color=GOLD_C, fontweight="bold")
# Legend
leg = [mpatches.Patch(color=ORB_BLUE, label="orbit_lite"),
       mpatches.Patch(color="#484f58", label="heuristic"),
       mpatches.Patch(color=GOLD_C,   label="peak")]
ax1.legend(handles=leg, loc="upper left", fontsize=8,
           facecolor=CARD_BG, edgecolor="#30363d", labelcolor=TEXT)

# ═══════════════════════════════════════════════════════════════════════════
# 2. HOW EACH AGENT CLIMBED
# ═══════════════════════════════════════════════════════════════════════════
ax2 = card_ax(outer[2],
              "How each active agent climbed",
              "Score from first game to convergence")
climb_colors = {
    "v1_starter":   "#8b949e",
    "v9_producer":  ORB_BLUE,
    "v9b":          ORB_GRN,
    "v10_tuned":    ORB_ORG,
}
for agent_name, points in CLIMBS.items():
    ys = [p[1] for p in points]
    xs_c = np.linspace(0, 1, len(ys))
    col  = climb_colors.get(agent_name, DIM_TEXT)
    ax2.plot(xs_c, ys, color=col, linewidth=2.2, marker="o",
             markersize=4, label=agent_name, zorder=3)
    ax2.text(xs_c[-1]+0.01, ys[-1], f"{ys[-1]}", fontsize=8,
             color=col, va="center")

ax2.axhline(1226, color=SILVER_C, linewidth=0.8, linestyle="--", alpha=0.5)
ax2.axhline(1100, color=BRONZE_C, linewidth=0.8, linestyle="--", alpha=0.5)
ax2.text(0.99, 1226+8, "Silver", color=SILVER_C, fontsize=7,
         ha="right", transform=ax2.get_yaxis_transform())
ax2.text(0.99, 1100+8, "Bronze", color=BRONZE_C, fontsize=7,
         ha="right", transform=ax2.get_yaxis_transform())
ax2.set_xlim(-0.05, 1.15)
ax2.set_ylim(400, 1350)
ax2.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax2.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8)
ax2.set_ylabel("LB Score", fontsize=8)
ax2.yaxis.grid(True, zorder=0); ax2.set_axisbelow(True)
ax2.legend(loc="upper left", fontsize=8, facecolor=CARD_BG,
           edgecolor="#30363d", labelcolor=TEXT)

# ═══════════════════════════════════════════════════════════════════════════
# 3. EACH AGENT'S RANGE
# ═══════════════════════════════════════════════════════════════════════════
ax3 = card_ax(outer[3],
              "Each agent's range",
              "Start score → peak (bar), current score (dot)")
agent_names = [a[0] for a in AGENTS]
best_scores = [a[1] for a in AGENTS]
statuses    = [a[2] for a in AGENTS]
archs3      = [a[3] for a in AGENTS]
start_scores = [600] * len(AGENTS)

ys3 = np.arange(len(AGENTS))
for i, (name, best, status, arch) in enumerate(AGENTS):
    col  = STATUS_COLORS[status]
    span = best - 600
    ax3.barh(i, span, left=600, color=col, height=0.55, alpha=0.75, zorder=3)
    ax3.plot(best, i, "o", color=GOLD_C if best == max(best_scores) else col,
             markersize=7, zorder=5)
    ax3.text(best+12, i, f"{best}", va="center", fontsize=8, color=col)

ax3.axvline(1226, color=SILVER_C, linewidth=0.8, linestyle="--", alpha=0.6)
ax3.axvline(1100, color=BRONZE_C, linewidth=0.8, linestyle="--", alpha=0.6)
ax3.axvline(1072, color="#484f58", linewidth=0.8, linestyle=":", alpha=0.6)
ax3.text(1226+5, -0.5, "Silver", color=SILVER_C, fontsize=7, rotation=90, va="bottom")
ax3.text(1100+5, -0.5, "Bronze", color=BRONZE_C, fontsize=7, rotation=90, va="bottom")
ax3.set_yticks(ys3)
ax3.set_yticklabels(agent_names, fontsize=9)
ax3.set_xlim(550, 1320)
ax3.xaxis.grid(True, zorder=0); ax3.set_axisbelow(True)
leg3 = [mpatches.Patch(color=ORB_GRN, label="active"),
        mpatches.Patch(color=ORB_ORG, label="converging"),
        mpatches.Patch(color="#484f58", label="inactive")]
ax3.legend(handles=leg3, loc="lower right", fontsize=8,
           facecolor=CARD_BG, edgecolor="#30363d", labelcolor=TEXT)

# ═══════════════════════════════════════════════════════════════════════════
# 4. FIELD DISTRIBUTION + OUR POSITION
# ═══════════════════════════════════════════════════════════════════════════
row4 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer[4],
                                         wspace=0.35)
ax4a = card_ax(row4[0], "Where your rating lived",
               "Distribution of our submission scores")
ax4b = card_ax(row4[1], "The whole field and you",
               "Score distribution of top 400 teams")

# Our scores histogram
our_scores = [s[2] for s in SUBMISSIONS]
ax4a.hist(our_scores, bins=12, color=ORB_BLUE, alpha=0.8, edgecolor="#0d1117",
          zorder=3)
ax4a.axvline(OUR_CURRENT, color=GOLD_C, linewidth=1.5, linestyle="--", label=f"Current {OUR_CURRENT}")
ax4a.axvline(1072, color="#484f58", linewidth=1, linestyle=":", label="v1 ceiling")
ax4a.set_xlabel("Score", fontsize=8); ax4a.set_ylabel("# submissions", fontsize=8)
ax4a.yaxis.grid(True, zorder=0); ax4a.set_axisbelow(True)
ax4a.legend(fontsize=7.5, facecolor=CARD_BG, edgecolor="#30363d", labelcolor=TEXT)

# Field distribution
ax4b.hist(LB_SCORES_SAMPLE, bins=30, color="#484f58", alpha=0.7,
          edgecolor="#0d1117", zorder=3)
ax4b.axvline(OUR_BEST, color=GOLD_C, linewidth=2, linestyle="--",
             label=f"Our peak {OUR_BEST}")
ax4b.axvline(1226, color=SILVER_C, linewidth=1, linestyle="--", label="Silver border")
ax4b.axvline(1100, color=BRONZE_C, linewidth=1, linestyle="--", label="Bronze border")
ax4b.set_xlabel("Score", fontsize=8); ax4b.set_ylabel("# teams", fontsize=8)
ax4b.yaxis.grid(True, zorder=0); ax4b.set_axisbelow(True)
ax4b.legend(fontsize=7.5, facecolor=CARD_BG, edgecolor="#30363d", labelcolor=TEXT)

# ═══════════════════════════════════════════════════════════════════════════
# 5. MEDAL PROGRESS (donut + gauge)
# ═══════════════════════════════════════════════════════════════════════════
row5 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer[5],
                                         wspace=0.35)
ax5a = card_ax(row5[0], "Medal zone progress", "How close to each medal")
ax5b = card_ax(row5[1], "Architecture impact", "Score ceiling by architecture")

# Medal donut
gold_pct   = min(1.0, OUR_BEST / 1500)
silver_pct = min(1.0, OUR_BEST / 1226)
bronze_pct = min(1.0, OUR_BEST / 1100)
medals = [bronze_pct, silver_pct, gold_pct]
medal_c = [BRONZE_C, SILVER_C, GOLD_C]
medal_labels = [f"Bronze\n{bronze_pct*100:.0f}%",
                f"Silver\n{silver_pct*100:.0f}%",
                f"Gold\n{gold_pct*100:.0f}%"]
y_pos = [0.75, 0.45, 0.15]
for i, (pct, col, lbl, yp) in enumerate(zip(medals, medal_c, medal_labels, y_pos)):
    ax5a.barh([yp], [pct], color=col, height=0.14, alpha=0.85, zorder=3,
              left=0, label=lbl)
    ax5a.barh([yp], [1-pct], color="#21262d", height=0.14, alpha=0.6,
              zorder=2, left=pct)
    ax5a.text(pct+0.02, yp, f"{pct*100:.0f}%", va="center",
              fontsize=10, color=col, fontweight="bold")
    ax5a.text(-0.02, yp, lbl.split("\n")[0], va="center",
              fontsize=9, color=col, ha="right")
ax5a.set_xlim(-0.25, 1.2)
ax5a.set_ylim(0, 1)
ax5a.set_yticks([]); ax5a.set_xticks([])

# Architecture comparison bars
arch_data = [
    ("v1_starter",  1072, "#484f58"),
    ("v2_roman",     980, "#484f58"),
    ("orbit_lite\n(default)", 1197, ORB_BLUE),
    ("orbit_lite\n(roi=1.2)", 1113, ORB_ORG),
]
arch_names  = [d[0] for d in arch_data]
arch_scores = [d[1] for d in arch_data]
arch_cols   = [d[2] for d in arch_data]
xa = np.arange(len(arch_data))
brs = ax5b.bar(xa, arch_scores, color=arch_cols, width=0.6, zorder=3, alpha=0.85)
ax5b.axhline(1226, color=SILVER_C, linewidth=0.8, linestyle="--", alpha=0.6)
ax5b.axhline(1100, color=BRONZE_C, linewidth=0.8, linestyle="--", alpha=0.6)
ax5b.set_xticks(xa); ax5b.set_xticklabels(arch_names, fontsize=8)
ax5b.set_ylim(800, 1350); ax5b.set_ylabel("Best LB Score", fontsize=8)
ax5b.yaxis.grid(True, zorder=0); ax5b.set_axisbelow(True)
for b, s in zip(brs, arch_scores):
    ax5b.text(b.get_x() + b.get_width()/2, s+8, str(s),
              ha="center", fontsize=8, color=TEXT)

# ═══════════════════════════════════════════════════════════════════════════
# 6. AGENT TIMELINE (architecture switch events)
# ═══════════════════════════════════════════════════════════════════════════
ax6 = card_ax(outer[6],
              "Career: score by submission date",
              "Coloured by architecture, dashed = inactive agents")
all_dates  = [s[0] for s in SUBMISSIONS]
all_scores = [s[2] for s in SUBMISSIONS]
all_archs  = [s[3] for s in SUBMISSIONS]
xs6 = np.arange(len(all_scores))
ax6.fill_between(xs6, 600, all_scores,
                 color=ORB_BLUE, alpha=0.1, zorder=1)
ax6.plot(xs6, all_scores, color=ORB_BLUE, linewidth=2, zorder=3)
for i, (x, s, a) in enumerate(zip(xs6, all_scores, all_archs)):
    col = ORB_BLUE if a == "orbit_lite" else "#8b949e"
    ax6.scatter(x, s, color=col, s=55, zorder=5)

# Annotate key milestones
milestones = {
    4: ("v1 ceiling\n1072", 1080),
    10: ("orbit_lite\n+200pts", 1180),
    11: ("peak\n1197", 1210),
}
for idx, (lbl, y_off) in milestones.items():
    if idx < len(xs6):
        ax6.annotate(lbl, (xs6[idx], all_scores[idx]),
                     xytext=(xs6[idx], y_off),
                     fontsize=7.5, color=GOLD_C, ha="center",
                     arrowprops=dict(arrowstyle="->", color=GOLD_C, lw=0.8))

ax6.axhline(1226, color=SILVER_C, linewidth=0.8, linestyle="--", alpha=0.5)
ax6.axhline(1100, color=BRONZE_C, linewidth=0.8, linestyle="--", alpha=0.5)
ax6.set_xticks(xs6)
ax6.set_xticklabels([s[1] for s in SUBMISSIONS], rotation=40,
                     ha="right", fontsize=7.5)
ax6.set_ylim(400, 1380)
ax6.set_ylabel("LB Score", fontsize=8)
ax6.yaxis.grid(True, zorder=0); ax6.set_axisbelow(True)

# Architecture change annotation
ax6.axvline(9.5, color="#30363d", linewidth=1.2, linestyle=":")
ax6.text(9.7, 500, "→ orbit_lite", fontsize=8, color=ORB_BLUE, va="bottom")
ax6.text(9.3, 500, "heuristic ←", fontsize=8, color="#8b949e", va="bottom", ha="right")

# ═══════════════════════════════════════════════════════════════════════════
# 7. HEAD TO HEAD — orbit_lite vs v1 heuristic
# ═══════════════════════════════════════════════════════════════════════════
row7 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=outer[7],
                                         wspace=0.35)
ax7a = card_ax(row7[0], "Head to head: orbit_lite vs heuristic",
               "Local win rate in benchmark games")
ax7b = card_ax(row7[1], "Config tuning results",
               "roi_threshold sweep — win rate vs v9 default")

# H2H results
matchups = [
    ("v9 vs v1_starter",   10, 0),
    ("v10 vs v9 (roi)",     9, 3),
    ("shum48 vs v9",        4, 8),
    ("v4 vs v1_starter",    0, 10),
]
y_pos7 = np.arange(len(matchups))
for i, (label, wins, losses) in enumerate(matchups):
    total = wins + losses
    if total == 0:
        continue
    win_frac = wins / total
    ax7a.barh(i, win_frac, color=ORB_GRN, height=0.5, alpha=0.8, zorder=3)
    ax7a.barh(i, 1-win_frac, left=win_frac, color=ORB_RED, height=0.5,
              alpha=0.6, zorder=3)
    ax7a.text(win_frac/2, i, f"{wins}W", va="center", ha="center",
              fontsize=8, color=BG, fontweight="bold")
    ax7a.text(win_frac + (1-win_frac)/2, i, f"{losses}L", va="center",
              ha="center", fontsize=8, color=BG, fontweight="bold")
    ax7a.text(-0.02, i, label, va="center", ha="right",
              fontsize=8, color=TEXT)
ax7a.set_xlim(-0.45, 1.05)
ax7a.set_yticks([]); ax7a.set_xticks([0.25, 0.5, 0.75])
ax7a.set_xticklabels(["25%", "50%", "75%"])
ax7a.axvline(0.5, color="#30363d", linewidth=1, linestyle="--")
ax7a.xaxis.grid(False)

# ROI threshold sweep
roi_vals  = [1.0, 1.2, 1.5, 2.0]
win_rates = [None, 0.75, 0.50, None]
bar_cols  = [DIM_TEXT, GOLD_C, ORB_BLUE, DIM_TEXT]
for i, (roi, wr, bc) in enumerate(zip(roi_vals, win_rates, bar_cols)):
    if wr is not None:
        ax7b.bar(i, wr, color=bc, width=0.55, alpha=0.85, zorder=3)
        ax7b.text(i, wr+0.02, f"{wr*100:.0f}%", ha="center",
                  fontsize=9, color=bc, fontweight="bold")
    else:
        ax7b.bar(i, 0.1, color=DIM_TEXT, width=0.55, alpha=0.3, zorder=3)
        ax7b.text(i, 0.12, "N/T", ha="center", fontsize=8, color=DIM_TEXT)
ax7b.axhline(0.5, color="#30363d", linewidth=1, linestyle="--", label="50% line")
ax7b.set_xticks(range(4))
ax7b.set_xticklabels([f"roi={r}" for r in roi_vals], fontsize=8.5)
ax7b.set_ylim(0, 1.1); ax7b.set_ylabel("Win rate vs v9 default", fontsize=8)
ax7b.yaxis.grid(True, zorder=0); ax7b.set_axisbelow(True)
ax7b.text(1, 0.78, "← current\nbest", fontsize=7.5, color=GOLD_C, ha="center")

# ═══════════════════════════════════════════════════════════════════════════
# 8. NEXT STEPS + FOOTER
# ═══════════════════════════════════════════════════════════════════════════
ax8 = card_ax(outer[8], "Next steps & roadmap", "Ranked by expected impact")
ax8.set_xlim(0, 10); ax8.set_ylim(0, 1)
ax8.set_xticks([]); ax8.set_yticks([])

steps = [
    (">>", "Wait for v10_tuned (roi=1.2) to converge",        "~1200+ target",   ORB_ORG),
    ("->", "Try horizon=22 (deeper planning)",                 "+?? pts",          ORB_BLUE),
    ("->", "Monitor exp-agent-kernel evolution (99 votes)",      "observe",          ORB_BLUE),
    ("??", "Understand simplified-agent-kernel private model (~1300 LB)","high value",       ORB_PUR),
    ("!!", "Terminal phase aggression (last 40 turns)",        "+10-20 pts",       ORB_GRN),
]
for i, (icon, text, note, col) in enumerate(steps):
    y = 0.85 - i * 0.18
    ax8.add_patch(FancyBboxPatch((0.02, y-0.06), 9.96, 0.14,
                                  boxstyle="round,pad=0.02",
                                  facecolor="#21262d", edgecolor="#30363d",
                                  linewidth=0.8))
    ax8.text(0.15, y+0.01, icon, fontsize=11, va="center")
    ax8.text(0.4,  y+0.01, text, fontsize=9, color=TEXT, va="center")
    ax8.text(9.8,  y+0.01, note, fontsize=8.5, color=col,
             va="center", ha="right", fontweight="bold")

ax8.text(5, -0.05, f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  github.com/Chirag314/orbit-wars",
         ha="center", fontsize=7.5, color=DIM_TEXT, transform=ax8.transAxes)

# ═══════════════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════════════
plt.savefig("dashboard.png", dpi=150, bbox_inches="tight",
            facecolor=BG, edgecolor="none")
print("Saved dashboard.png")
