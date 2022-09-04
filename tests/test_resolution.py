from previewer.resolution import Resolution


def test_resolution_int():
    res = Resolution(200)
    assert res.width == res.x == 200
    assert res.height == res.y == 200
    assert str(res) == "200x200"


def test_resolution_int_int():
    res = Resolution(300, 200)
    assert res.width == res.x == 300
    assert res.height == res.y == 200
    assert str(res) == "300x200"


def test_resolution_str1():
    res = Resolution("200")
    assert res.width == res.x == 200
    assert res.height == res.y == 200
    assert str(res) == "200x200"


def test_resolution_str2():
    res = Resolution("300x200")
    assert res.width == res.x == 300
    assert res.height == res.y == 200
    assert str(res) == "300x200"


def test_equal():
    assert Resolution("200x300") == Resolution(200, 300)
    assert Resolution("200x300") != Resolution(200, 301)
    assert Resolution("200x300") != Resolution(201, 300)
    assert Resolution("200x300") != Resolution(201, 301)
