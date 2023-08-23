from previewer.disposition import _dump, best_disposition_from_total


def test_best_disposition_from_total():
    assert best_disposition_from_total(12).columns == 4
    assert best_disposition_from_total(11).columns == 4
    assert best_disposition_from_total(40).columns == 8


def test_best_disposition_from_total_range_1_20():
    for count, rows in {
        1: 1,
        2: 1,
        3: 1,
        4: 2,
        5: 2,
        6: 2,
        7: 2,
        8: 2,
        9: 3,
        10: 3,
        11: 3,
        12: 3,
        13: 3,
        14: 3,
        15: 3,
        16: 4,
        17: 3,
        18: 3,
        19: 4,
        20: 4,
    }.items():
        disp = best_disposition_from_total(
            count, resolution=(640, 480), target_ratio=16 / 9
        )
        _dump(disp)
        assert disp.rows == rows


def test_best_disposition_from_total_range_21_100():
    for count in range(21, 100):
        disp = best_disposition_from_total(
            count, resolution=(640, 480), target_ratio=16 / 9
        )
        _dump(disp)
        assert 3 <= disp.rows < 10
