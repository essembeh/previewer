from re import fullmatch


def resolution_parse(value: str) -> tuple[int, int]:
    matcher = fullmatch(r"(?P<width>[0-9]+)(x(?P<height>[0-9]+))?", value)
    assert matcher is not None
    width, height = matcher.group("width"), matcher.group("height")
    assert width.isdigit()
    width = int(width)
    assert width > 0
    if height is not None:
        assert height.isdigit()
        height = int(height)
        assert height > 0
    return (width, height) if height is not None else (width, width)
