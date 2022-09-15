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
