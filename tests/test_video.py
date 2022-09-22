from previewer import video
from previewer.utils import get_mime


def test_get_video_duration(sample_mp4):
    duration = video.get_video_duration(sample_mp4)
    assert 4 < duration < 6


def test_extract_images(sample_mp4):
    count = 0
    last_position = 0
    for frame, seconds in video.iter_video_frames(sample_mp4, 3):
        count += 1
        assert last_position < seconds
        last_position = seconds
        assert get_mime(frame) == "image/jpeg"
    assert count == 3


def test_parse_position():
    for line in map(
        str.strip,
        """ 1234
            1234.1
            1234.12
            1234.123
            12:34
            12:34.1
            12:34.12
            12:34.123
            1:23:45
            1:23:45.1
            1:23:45.12
            1:23:45.123 """.splitlines(),
    ):
        assert video.position_to_seconds(line) > 0
