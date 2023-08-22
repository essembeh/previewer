![Github](https://img.shields.io/github/tag/essembeh/previewer.svg)
![PyPi](https://img.shields.io/pypi/v/previewer.svg)
![Python](https://img.shields.io/pypi/pyversions/previewer.svg)
![CI](https://github.com/essembeh/previewer/actions/workflows/poetry.yml/badge.svg)

# Previewer

Command line tool to generate montages (image previews) from video clips or folders containing images.

# Install

Install `ffmpeg` if you want to generate previews for video clips.

```sh
$ sudo apt update
$ sudo apt install ffmpeg
```

Install the latest release of _previewer_ from [PyPI](https://pypi.org/project/previewer/)

```sh
$ pip3 install previewer
$ previewer --help
```

Or install _previewer_ from the sources

```sh
$ pip3 install poetry
$ pip3 install git+https://github.com/essembeh/previewer
$ previewer --help
```

# Usage

You can customize the generated image:

- change geometry (width, height, crop, fit or fill) of the thumbnails
- change the background color
- show or hide the a title
- adjust the space between thumbnails
- add a border, a shadow to thumbnails

## Example: generate a preview from a video clip

We can build a preview image of a video using:

```sh
$ previewer --crop 256 --shadow --title --background lightblue "samples/Rick Astley - Never Gonna Give You Up.mp4"
🎬 Generate montage from video samples/Rick Astley - Never Gonna Give You Up.mp4 using 36 thumbnails
🍺 Montage generated ./Rick Astley - Never Gonna Give You Up.jpg
```

![Video preview](images/preview-video.jpg)

## Example: generate a preview from a folder containing images

We can build a preview folder containing images like this:

![Folder with images](images/folder.png)

```sh
$ previewer --columns 5 --polaroid --background b2967d "samples/Rick Astley - Never Gonna Give You Up"
📷 Generate montage from folder samples/Rick Astley - Never Gonna Give You Up/ containing 20 images
🍺 Montage generated ./Rick Astley - Never Gonna Give You Up.jpg
```

![Folder preview](images/preview-folder.jpg)
