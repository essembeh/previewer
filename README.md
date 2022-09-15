![Github](https://img.shields.io/github/tag/essembeh/previewer.svg)
![PyPi](https://img.shields.io/pypi/v/previewer.svg)
![Python](https://img.shields.io/pypi/pyversions/previewer.svg)
![CI](https://github.com/essembeh/previewer/actions/workflows/poetry.yml/badge.svg)

# Previewer

Command line tools to generate previews from video clips or folders containing images.

_previewer_ is a collection of tools:

- `previewer montage`: to generate a single image with thumbnails from a _folder_ containing images or a video clip
- `previewer gif`: to generate a Gif with thumbnails from a _folder_ containing images or a video clip
- `previewer video-thumbnailer`: to extract a given number of thumbnails from a video clip
- `previewer folder-thumbnailer`: to generate thumbnails (resized and cropped images) from a folder containing larger images

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

# Usage: `previewer montage`

```sh
$ previewer montage --help
usage: previewer montage [-h] [-r] [-o OUTPUT] [-P PREFIX] [-S SUFFIX] [--polaroid | --no-polaroid] [--shadow | --no-shadow] [--auto_orient | --no-auto_orient] [--title | --no-title]
                         [--filenames | --no-filenames] [-B BACKGROUND] [-C COLUMNS] [-R ROWS] [--size SIZE] [--crop | --no-crop] [--fill | --no-fill] [--offset OFFSET]
                         input_files [input_files ...]

positional arguments:
  input_files           folders containing images or video files

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       list images recursively (only for images folders)
  -o OUTPUT, --output OUTPUT
                        output folder (default is current folder)
  -P PREFIX, --prefix PREFIX
                        generated filename prefix
  -S SUFFIX, --suffix SUFFIX
                        generated filename prefix
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
  --crop, --no-crop     crop thumbnails (default: False)
  --fill, --no-fill     fill thumbnails (default: False)
  --offset OFFSET       thumbnail offset (default is 10)
```

# Usage: `previewer gif`

```sh
$ previewer gif --help               
usage: previewer gif [-h] [-r] [-o OUTPUT] [-P PREFIX] [-S SUFFIX] [--delay DELAY | --fps DELAY] [-n COUNT | --speed SPEED] [--colors COLORS] [--size SIZE] [--crop | --no-crop] [--fill | --no-fill]
                     input_files [input_files ...]

positional arguments:
  input_files           folders containing images or video files

optional arguments:
  -h, --help            show this help message and exit
  -r, --recursive       list images recursively (only for images folders)
  -o OUTPUT, --output OUTPUT
                        output folder (default is current folder)
  -P PREFIX, --prefix PREFIX
                        generated filename prefix
  -S SUFFIX, --suffix SUFFIX
                        generated filename prefix
  --delay DELAY         delay for frames in ms, default is 500
  --fps DELAY           frame per second, default is 2
  -n COUNT, --count COUNT
                        thumbnails count for videos (default calculated given --delay/--fps)
  --speed SPEED         calculate frames count to extract to respect given speed (only for videos)
  --colors COLORS       gif colors
  --size SIZE           thumbnail size (default is 640x480)
  --crop, --no-crop     crop thumbnails (default: False)
  --fill, --no-fill     fill thumbnails (default: False)
```

# Usage: `previewer video-thumbnailer`

```sh
$ previewer video-thumbnailer --help
usage: previewer video-thumbnailer [-h] [-o OUTPUT] [-n COUNT] [--size SIZE] [--crop | --no-crop] [--fill | --no-fill] videos [videos ...]

positional arguments:
  videos                video file

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output folder (default is a new folder in current directory)
  -n COUNT, --count COUNT
                        thumbnails count (default is 20)
  --size SIZE           thumbnail size
  --crop, --no-crop     crop thumbnails (default is False) (default: False)
  --fill, --no-fill     fill thumbnails (defailt is False) (default: False)
```

# Usage: `previewer folder-thumbnailer`

```sh
$ previewer folder-thumbnailer --help
usage: previewer folder-thumbnailer [-h] [-o OUTPUT] [-r] --size SIZE [--crop | --no-crop] [--fill | --no-fill] folders [folders ...]

positional arguments:
  folders               folders containging images

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output folder (default is a new folder in current directory)
  -r, --recursive       list images recursively (only for images folders)
  --size SIZE           thumbnail size
  --crop, --no-crop     crop thumbnails (default is False) (default: False)
  --fill, --no-fill     fill thumbnails (defailt is False) (default: False)
```
