def compute_trend(years_ranks: list[tuple[int, int]]) -> tuple[str, float]:
    """years_ranks: [(year, rank), ...] in any order, rank lower = more popular.
    Compares the average rank of the earliest third of years vs the latest third.
    A lower (better) recent rank than earlier => rising; higher => falling.

    Used both to precompute each name's all-time trend at ingestion time and to
    recompute it on the fly scoped to whatever year range a request has filtered to.
    """
    if len(years_ranks) < 2:
        return "stable", 0.0

    ordered = sorted(years_ranks, key=lambda yr: yr[0])
    n = len(ordered)
    third = max(1, n // 3)
    early = ordered[:third]
    recent = ordered[-third:]
    early_avg = sum(r for _, r in early) / len(early)
    recent_avg = sum(r for _, r in recent) / len(recent)

    slope = early_avg - recent_avg  # positive => rank improved (rising popularity)
    if slope > early_avg * 0.1:
        return "rising", slope
    if slope < -early_avg * 0.1:
        return "falling", slope
    return "stable", slope
