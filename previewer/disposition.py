from math import ceil
from typing import NamedTuple

Candidate = NamedTuple(
    "Candidate", columns=int, rows=int, last_row_missing=int, ratio=float
)


def get_video_best_disposition(
    duration: float,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
) -> tuple[int, int]:
    if duration < 60:
        return 3, 9
    if duration < 180:
        return 4, 16
    if duration < 300:
        return 5, 25
    return 6, 36


def find_best_disposition(
    image_count: int,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
) -> int:
    all_candidates = [
        Candidate(
            columns=col,
            rows=ceil(image_count / col),
            last_row_missing=image_count - col * ceil(image_count / col),
            ratio=(col * resolution[0]) / (ceil(image_count / col) * resolution[1]),
        )
        for col in range(1, image_count + 1)
    ]
    # order by closest target ratio
    sorted_candidates = sorted(
        all_candidates, key=lambda c: abs(c.ratio - target_ratio)
    )
    # remove when ratio is too different
    best_candidates = [
        c
        for c in sorted_candidates
        if target_ratio * 0.75 < c.ratio < target_ratio * 1.25
    ]
    # remove when last row is too empty
    best_candidates = [
        c for c in best_candidates if c.last_row_missing > c.columns * 0.5
    ]
    # if a perfect disposition if found
    best = next(filter(lambda c: c.last_row_missing == 0, best_candidates), None)
    if best is None:
        if len(best_candidates) > 0:
            # in other case, simply return the first best
            best = best_candidates[0]
        else:
            # fallback, use the best or all combinations
            best = sorted_candidates[0]
    assert best is not None
    return best.columns
