![Github](https://img.shields.io/github/tag/essembeh/previewer.svg)
![PyPi](https://img.shields.io/pypi/v/previewer.svg)
![Python](https://img.shields.io/pypi/pyversions/previewer.svg)
![CI](https://github.com/essembeh/previewer/actions/workflows/poetry.yml/badge.svg)

# Previewer

Command line tools to generate previews from video clips or folders containing images.

_previewer_ is a collection of tools:

- `previewer-montage`: to generate a single image with thumbnails from a _folder_ containing images or a video clip
- `previewer-video-thumbnailer`: to extract a given number of thumbnails from a video clip
- `previewer-folder-thumbnailer`: to generate thumbnails (resized and cropped images) from a folder containing larger images

# Install

Install dependencies

```sh
$ sudo apt update
$ sudo apt install imagemagick mediainfo ffmpeg
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
$ previewer-montage --help
```

# Usage: `previewer-montage`

```sh
$ previewer-montage --help
usage: previewer-montage [-h] [--version] [--verbose] [--polaroid | --no-polaroid] [--shadow | --no-shadow] [--auto_orient | --no-auto_orient] [--title | --no-title] [--filenames | --no-filenames]
                         [-B BACKGROUND] [-C COLUMNS] [-R ROWS] [--size SIZE] [--offset OFFSET] [-r] [-o OUTPUT] [--suffix SUFFIX]
                         folder_or_video [folder_or_video ...]

extract thumbnails from video

positional arguments:
  folder_or_video       folder containing images or video file

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --verbose             print more information
  --polaroid, --no-polaroid
                        use polaroid style
  --shadow, --no-shadow
                        add shadow to thumbnails
  --auto_orient, --no-auto_orient
                        auto orient thumbnails
  --title, --no-title   add file/folder name as preview title (default: True)
  --filenames, --no-filenames
                        add filenames under thumbnails (ignored for videos)
  -B BACKGROUND, --background BACKGROUND
                        montage background color, list of colors: https://imagemagick.org/script/color.php
  -C COLUMNS, --columns COLUMNS
                        preview columns count (default is 6)
  -R ROWS, --rows ROWS  preview rows count
  --size SIZE           thumbnail size (default is 256x256)
  --offset OFFSET       thumbnail offset (default is 10)
  -r, --recursive       list images recursively (only for images folders)
  -o OUTPUT, --output OUTPUT
                        output folder (default is current folder)
  --suffix SUFFIX       preview filename suffix (default is ' preview')

```

# Usage: `previewer-video-thumbnailer`

```sh
$ previewer-video-thumbnailer --help
usage: previewer-video-thumbnailer [-h] [--version] [--verbose] [-o OUTPUT] [-n COUNT] [--size SIZE] [--crop] [--prefix PREFIX] video

extract thumbnails from video

positional arguments:
  video                 video file

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --verbose             print more information
  -o OUTPUT, --output OUTPUT
                        output folder, default is current folder
  -n COUNT, --count COUNT
                        thumbnails count (default is 20)
  --size SIZE           thumbnail size
  --crop                crop thumbnails
  --prefix PREFIX       prefix for thumbnails (default is video filename)

```

# Usage: `previewer-folder-thumbnailer`

```sh
$ previewer-folder-thumbnailer --help
usage: previewer-folder-thumbnailer [-h] [--version] [-r] [-o OUTPUT] [-s SIZE] [--crop] folder

extract thumbnails from folder

positional arguments:
  folder                folder containing images

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -r, --recursive       list images recursively (only for images folders)
  -o OUTPUT, --output OUTPUT
                        output folder, default is current folder
  -s SIZE, --size SIZE  thumbnails max size (default is 256x256)
  --crop                crop thumbnails

```
