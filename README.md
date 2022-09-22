![Github](https://img.shields.io/github/tag/essembeh/previewer.svg)
![PyPi](https://img.shields.io/pypi/v/previewer.svg)
![Python](https://img.shields.io/pypi/pyversions/previewer.svg)
![CI](https://github.com/essembeh/previewer/actions/workflows/poetry.yml/badge.svg)

# Previewer

Command line tool to generate montages/sequences from video clips or folders containing images.

_previewer_ is a collection of tools:

- `previewer montage`: to generate a single image with thumbnails (a _montage_) from a folder containing images or a video
- `previewer gif`: to generate a Gif (or mp4/webp/webm) with thumbnails from a folder containing images or a video
- `previewer video-thumbnailer`: to extract a given number of thumbnails from a video clip
- `previewer resize`: to change geometry (resize, crop, fit, fill) of images

# Install

Install dependencies

```sh
$ sudo apt update
$ sudo apt install imagemagick ffmpeg
```

Install the latest release of _previewer_ from [PyPI](https://pypi.org/project/previewer/)

```sh
$ pip3 install previewer
$ previewer-montage --help
```

Or install _previewer_ from the sources

```sh
$ pip3 install poetry
$ pip3 install git+https://github.com/essembeh/previewer
$ previewer --help
```

# Montage

`previewer montage` can create _preview_ image from a folder containing images or a video.

You can customize the generated image:

- change the background color
- change geometry (width, height, crop, fit or fill) of the thumbnails
- show or hide the a title
- show or hide image filenames
- adjust the space between thumbnails
- add a border, a shadow to thumbnails

Example:

```sh
$ previewer montage --size 120x120 --crop --fill --background SlateGray1 "Rick Astley - Never Gonna Give You Up (Official Music Video).mp4"
🎬 Generate montage from video ./Rick Astley - Never Gonna Give You Up (Official Music Video).mp4 using 36 thumbnails
🍺 Montage generated ./Rick Astley - Never Gonna Give You Up (Official Music Video).jpg
```

![Example of montage](images/montage.jpg)

# Sequence

`previewer gif` can generate sequences with images in a folder or extracted from a video.

You can customize the sequence:

- choose the format between _gif_, _mp4_, _webp_ or _webm_
- adjust _fps_ (frames per seconds), _delay_ between 2 frames ...
- when extrating frames from a video, you can either use a fixed number of frames to extract or compute it given a given _speed_
- change geometry (width, height, crop, fit or fill) of the frames

Example:

```sh
$ previewer gif --size 320x240 --crop --fill -n 20 "Rick Astley - Never Gonna Give You Up (Official Music Video).mp4"
🎬 Generate gif from video ./Rick Astley - Never Gonna Give You Up (Official Music Video).mp4 using 20 thumbnails
🍺 Sequence generated ./Rick Astley - Never Gonna Give You Up (Official Music Video).gif
```

![Example of sequence](images/sequence.gif)

```sh
$ previewer gif --start 3 --end 4 --fps 10 --aba --size 320x240 --crop --fill "Rick Astley - Never Gonna Give You Up (Official Music Video).mp4"
🎬 Generate gif from video ./Rick Astley - Never Gonna Give You Up (Official Music Video).mp4 using 10 thumbnails
🍺 Sequence generated ./Rick Astley - Never Gonna Give You Up (Official Music Video).gif
```

![Example of sequence with A-B-A loop](images/sequence-aba.gif)

# Thumbnailer

`previewer video-thumbnailer` can extract and resize/crop frames from a video

You can also:

- choose the frame count to extract
- select a start position and/or a end position in the video
- change geometry (width, height, crop, fit or fill) of the frames

Example:

```sh
$ previewer video-thumbnailer -n 20 "Rick Astley - Never Gonna Give You Up (Official Music Video).mp4"
Extract 20 thumbnails from ./Rick Astley - Never Gonna Give You Up (Official Music Video).mp4
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 01 (0:00:05).jpg (1920x1080) at position 0:00:05
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 02 (0:00:15).jpg (1920x1080) at position 0:00:15
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 03 (0:00:26).jpg (1920x1080) at position 0:00:26
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 04 (0:00:37).jpg (1920x1080) at position 0:00:37
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 05 (0:00:47).jpg (1920x1080) at position 0:00:47
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 06 (0:00:58).jpg (1920x1080) at position 0:00:58
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 07 (0:01:08).jpg (1920x1080) at position 0:01:08
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 08 (0:01:19).jpg (1920x1080) at position 0:01:19
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 09 (0:01:30).jpg (1920x1080) at position 0:01:30
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 10 (0:01:40).jpg (1920x1080) at position 0:01:40
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 11 (0:01:51).jpg (1920x1080) at position 0:01:51
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 12 (0:02:01).jpg (1920x1080) at position 0:02:01
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 13 (0:02:12).jpg (1920x1080) at position 0:02:12
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 14 (0:02:23).jpg (1920x1080) at position 0:02:23
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 15 (0:02:33).jpg (1920x1080) at position 0:02:33
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 16 (0:02:44).jpg (1920x1080) at position 0:02:44
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 17 (0:02:54).jpg (1920x1080) at position 0:02:54
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 18 (0:03:05).jpg (1920x1080) at position 0:03:05
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 19 (0:03:16).jpg (1920x1080) at position 0:03:16
  Rick Astley - Never Gonna Give You Up (Official Music Video)/frame 20 (0:03:26).jpg (1920x1080) at position 0:03:26
🍺 20 thumbnails extracted in Rick Astley - Never Gonna Give You Up (Official Music Video)/

```

![Example of thumbnailer](images/frames.png)
