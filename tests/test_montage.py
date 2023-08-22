from previewer.disposition import find_best_disposition


def test_disposition():
    assert find_best_disposition(12) == 4
    assert find_best_disposition(11) == 4
    assert find_best_disposition(40) == 8


def test_disposition2():
    for count in range(1, 1000):
        col = find_best_disposition(count)
        assert 0 < col <= count
