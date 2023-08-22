from previewer.disposition import best_disposition_from_total


def test_best_disposition_from_total():
    assert best_disposition_from_total(12).columns == 4
    assert best_disposition_from_total(11).columns == 4
    assert best_disposition_from_total(40).columns == 7


def test_best_disposition_from_total2():
    for count in range(1, 1000):
        disp = best_disposition_from_total(count)
        assert 0 < disp.columns <= count
