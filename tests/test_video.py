from previewer import video
from previewer.utils import get_mime


def test_get_video_duration(sample_mp4):
    duration = video.get_video_duration(sample_mp4)
    assert 4 < duration < 6


def test_extract_images(sample_mp4):
    count = 0
    last_position = -1
    for frame, seconds in video.iter_video_frames(sample_mp4, 3):
        count += 1
        assert last_position < seconds
        last_position = seconds
        assert get_mime(frame) == "image/jpeg"
    assert count == 3


def test_parse_position():

    assert video.Position("0%").get_seconds(3600) == 0
    assert video.Position("100%").get_seconds(3600) == 3600
    assert video.Position("-0%").get_seconds(3600) == 3600
    assert video.Position("-100%").get_seconds(3600) == 0
    assert video.Position("10%").get_seconds(3600) == 360
    assert video.Position("-10%").get_seconds(3600) == 3240

    assert video.Position("12").get_seconds(3600) == 12
    assert video.Position("12.777").get_seconds(3600) == 12.777
    assert video.Position("120.777").get_seconds(3600) == 120.777
    assert video.Position("-12").get_seconds(3600) == 3588
    assert video.Position("-12.777").get_seconds(3600) == 3587.223
    assert video.Position("-120.777").get_seconds(3600) == 3479.223

    assert video.Position("0:00:12").get_seconds(7200) == 12
    assert video.Position("0:01:12").get_seconds(7200) == 72
    assert video.Position("1:10:12").get_seconds(7200) == 4212
    assert video.Position("1:10:12.500").get_seconds(7200) == 4212.5
    assert video.Position("-0:00:12").get_seconds(7200) == 7188
    assert video.Position("-0:01:12").get_seconds(7200) == 7128
    assert video.Position("-1:10:12").get_seconds(7200) == 2988
    assert video.Position("-1:10:12.500").get_seconds(7200) == 2987.5
