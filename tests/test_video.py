from previewer import video


def test_get_video_duration(sample_mp4):
    duration = video.get_video_duration(sample_mp4)
    assert 4 < duration < 6


def test_extract_images(sample_mp4, tmp_path):
    video.extract_images(sample_mp4, tmp_path, 12, "foo")
    count = 0
    for image in tmp_path.iterdir():
        count += 1
        assert image.name.startswith("foo")
    assert count == 12
