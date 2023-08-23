from itertools import chain
from math import ceil
from typing import NamedTuple

Candidate = NamedTuple("Candidate", columns=int, rows=int, missing=int, ratio=float)

Disposition = NamedTuple("Disposition", columns=int, rows=int, images=int)


def best_disposition_from_video(
    duration: float,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
) -> Disposition:
    rows = 1
    if duration < 120:
        rows = 2
    elif duration < 300:
        rows = 3
    elif duration < 600:
        rows = 4
    else:
        rows = 5
    cols = ceil(rows * resolution[1] * target_ratio / resolution[0])
    return Disposition(columns=cols, rows=rows, images=cols * rows)


def best_disposition_from_columns(
    columns_count: int,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
) -> Disposition:
    # compute best disposition
    rows_count = ceil(columns_count * resolution[0] / target_ratio / resolution[1])
    return Disposition(
        columns=columns_count, rows=rows_count, images=rows_count * columns_count
    )


def best_disposition_from_total(
    images: int,
    resolution: tuple[int, int] = (1, 1),
    target_ratio: float = 4 / 3,
    acceptable_ratio: tuple[float, float] = (0.7, 1.6),
) -> Disposition:

    # Workaround for special cases
    if images <= 3:
        return Disposition(columns=images, rows=1, images=images)

    all_candidates = [
        Candidate(
            columns=col,
            rows=ceil(images / col),
            missing=col * ceil(images / col) - images,
            ratio=(col * resolution[0]) / (ceil(images / col) * resolution[1]),
        )
        for col in range(1, images + 1)
    ]

    # order by closest target ratio
    sorted_candidates = sorted(
        all_candidates, key=lambda c: abs(c.ratio - target_ratio)
    )

    # good candidates have not too much missing in last row
    good_candidates = [c for c in sorted_candidates if c.missing <= c.columns * 0.5]

    # perfect candidates have a good ratio
    perfect_candidates = sorted(
        [
            c
            for c in good_candidates
            if target_ratio * acceptable_ratio[0]
            < c.ratio
            < target_ratio * acceptable_ratio[1]
        ],
        key=lambda c: c.missing,
    )

    # fallback
    best = next(chain(perfect_candidates, good_candidates, sorted_candidates))
    return Disposition(columns=best.columns, rows=best.rows, images=images)


def _dump(item: list | Disposition | Candidate):
    if isinstance(item, list):
        for x in item:
            _dump(x)
    else:
        total = (
            item.images
            if isinstance(item, Disposition)
            else (item.rows * item.columns - item.missing)
        )
        ratio = (
            item.ratio if isinstance(item, Candidate) else (item.columns / item.rows)
        )
        print(
            f"\n==========[{total} images, {item.columns} columns, {item.rows} rows, ratio: {ratio}]=========="
        )
        for index in range(total):
            if index > 0 and index % item.columns == 0:
                print()
            print(" 📊", end="")
        print(f"\n--------------------")
