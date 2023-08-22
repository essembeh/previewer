from previewer.collectors import iter_video_frames
from previewer.mime import get_mime
from previewer.video import (
    Position,
    get_video_duration,
    get_video_metadata,
    get_video_resolution,
)


def test_get_video_duration(clip):
    duration = get_video_duration(clip)
    assert 3 < duration < 5


def test_get_video_resolution(clip):
    resolution = get_video_resolution(clip)
    assert resolution == (1280, 720)


def test_extract_images(clip):
    count = 0
    last_position = -1
    for frame, seconds in iter_video_frames(clip, 3):
        count += 1
        assert last_position < seconds
        last_position = seconds
        assert get_mime(frame) == "image/jpeg"
    assert count == 3


def test_metadata(clip):
    metadata = get_video_metadata(clip)

    assert float(metadata["format"]["duration"]) == get_video_duration(clip)


def test_parse_position():

    assert Position("0%").get_seconds(3600) == 0
    assert Position("100%").get_seconds(3600) == 3600
    assert Position("-0%").get_seconds(3600) == 3600
    assert Position("-100%").get_seconds(3600) == 0
    assert Position("10%").get_seconds(3600) == 360
    assert Position("-10%").get_seconds(3600) == 3240

    assert Position("12").get_seconds(3600) == 12
    assert Position("12.777").get_seconds(3600) == 12.777
    assert Position("120.777").get_seconds(3600) == 120.777
    assert Position("-12").get_seconds(3600) == 3588
    assert Position("-12.777").get_seconds(3600) == 3587.223
    assert Position("-120.777").get_seconds(3600) == 3479.223

    assert Position("0:00:12").get_seconds(7200) == 12
    assert Position("0:01:12").get_seconds(7200) == 72
    assert Position("1:10:12").get_seconds(7200) == 4212
    assert Position("1:10:12.500").get_seconds(7200) == 4212.5
    assert Position("-0:00:12").get_seconds(7200) == 7188
    assert Position("-0:01:12").get_seconds(7200) == 7128
    assert Position("-1:10:12").get_seconds(7200) == 2988
    assert Position("-1:10:12.500").get_seconds(7200) == 2987.5
