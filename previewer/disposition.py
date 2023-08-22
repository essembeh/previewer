from math import ceil
from typing import NamedTuple

Candidate = NamedTuple(
    "Candidate", columns=int, rows=int, last_row_missing=int, ratio=float
)

Disposition = NamedTuple("Disposition", columns=int, rows=int, images_count=int)


def best_disposition_from_video(
    duration: float,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
) -> Disposition:
    rows = 1
    if duration < 60:
        rows = 1
    elif duration < 180:
        rows = 2
    elif duration < 300:
        rows = 3
    elif duration < 600:
        rows = 4
    else:
        rows = 5
    cols = ceil(rows * resolution[1] * target_ratio / resolution[0])
    return Disposition(columns=cols, rows=rows, images_count=cols * rows)


def best_disposition_from_columns(
    columns_count: int,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
) -> Disposition:
    # compute best disposition
    rows_count = ceil(columns_count * resolution[0] / target_ratio / resolution[1])
    return Disposition(
        columns=columns_count, rows=rows_count, images_count=rows_count * columns_count
    )


def best_disposition_from_total(
    images_count: int,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
) -> Disposition:
    all_candidates = [
        Candidate(
            columns=col,
            rows=ceil(images_count / col),
            last_row_missing=images_count - col * ceil(images_count / col),
            ratio=(col * resolution[0]) / (ceil(images_count / col) * resolution[1]),
        )
        for col in range(1, images_count + 1)
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
    return Disposition(columns=best.columns, rows=best.rows, images_count=images_count)
