"""
Fantasy point calculation for the Israeli Euroleague fantasy game (ערוץ הספורט).

Scoring rules:
  Point scored       +1
  Rebound            +2
  Assist             +2
  Steal              +3
  Block              +3
  Foul drawn         +1
  Turnover           -2
  Missed shot (any)  -1
  Foul committed     -1
  Double-double      +10 bonus  (10+ in 2 of: pts/reb/ast/stl/blk)
  Triple-double      +20 bonus  (10+ in 3 of: pts/reb/ast/stl/blk)

Coach scoring:
  margin > 0  →  +5 + margin   (won by 'margin' points)
  margin < 0  →  -5 + margin   (lost by abs(margin) points, e.g. -10 → -15)
  margin == 0 is not expected but treated as 0 points
"""


def compute_fantasy_points(p: dict) -> float:
    """
    Compute fantasy points for one player's game stats.

    Expected keys in `p`:
      points, rebounds, assists, steals, blocks, fouls_drawn, fouls_committed,
      turnovers, fg2_made, fg2_attempted, fg3_made, fg3_attempted,
      ft_made, ft_attempted
    """
    missed = (
        (p.get("fg2_attempted", 0) - p.get("fg2_made", 0))
        + (p.get("fg3_attempted", 0) - p.get("fg3_made", 0))
        + (p.get("ft_attempted", 0) - p.get("ft_made", 0))
    )

    score = (
        p.get("points", 0) * 1
        + p.get("rebounds", 0) * 2
        + p.get("assists", 0) * 2
        + p.get("steals", 0) * 3
        + p.get("blocks", 0) * 3
        + p.get("fouls_drawn", 0) * 1
        + p.get("turnovers", 0) * -2
        + missed * -1
        + p.get("fouls_committed", 0) * -1
    )

    # Double-double / triple-double bonus
    # Categories: points, rebounds, assists, steals, blocks
    cats = [
        p.get("points", 0),
        p.get("rebounds", 0),
        p.get("assists", 0),
        p.get("steals", 0),
        p.get("blocks", 0),
    ]
    doubles = sum(1 for c in cats if c >= 10)
    if doubles >= 3:
        score += 20
    elif doubles >= 2:
        score += 10

    return float(score)


def compute_coach_fantasy_points(margin: int) -> float:
    """
    Compute fantasy points for a coach based on game margin.
      margin > 0  →  won by 'margin' points  →  +5 + margin
      margin < 0  →  lost by abs(margin)      →  -5 + margin (e.g. -10 → -15)
      margin == 0 →  0 points (draw, unlikely)
    """
    if margin > 0:
        return float(5 + margin)
    elif margin < 0:
        return float(-5 + margin)
    return 0.0
