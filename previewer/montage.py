from math import ceil

from PIL import Image, ImageDraw, ImageFont


def build_montage(
    images: list[Image.Image],
    columns: int,
    background_color: str = "white",
    margin: int = 10,
    text: str | None = None,
    text_color: str = "black",
    text_font: ImageFont.ImageFont | ImageFont.FreeTypeFont | None = None,
) -> Image.Image:
    """
    Build a montage which is an image with all given images organized  in columns
    """
    # compute final image size
    columns_max_width = [0] * min(columns, len(images))
    rows_max_heigth = [0] * ceil(len(images) / columns)
    for i, img in enumerate(images):
        icol, irow = i % columns, int(i / columns)
        if img.size[0] > columns_max_width[icol]:
            columns_max_width[icol] = img.size[0]
        if img.size[1] > rows_max_heigth[irow]:
            rows_max_heigth[irow] = img.size[1]

    # compute text size and offsets
    text_size, text_offset = (0, 0), 0
    if text is not None and text_font is not None:
        text_size = text_font.getbbox(text)[2:]
        text_offset = margin + text_size[1] + margin

    # create the result image
    out = Image.new(
        "RGB",
        (
            sum(columns_max_width) + margin * (len(columns_max_width) + 1),
            sum(rows_max_heigth) + margin * (len(rows_max_heigth) + 1) + text_offset,
        ),
        background_color,
    )

    # write text if needed
    if text is not None and text_font is not None:
        draw = ImageDraw.Draw(out)
        draw.text(
            (int((out.size[0] - text_size[0]) / 2), margin),
            text,
            font=text_font,
            fill=text_color,
        )

    # add all images
    for i, img in enumerate(images):
        icol, irow = i % columns, int(i / columns)
        center_x = int(
            sum(columns_max_width[:icol])
            + columns_max_width[icol] / 2
            + margin * (icol + 1)
        )
        center_y = int(
            sum(rows_max_heigth[:irow])
            + rows_max_heigth[irow] / 2
            + margin * (irow + 1)
            + text_offset
        )
        out.paste(
            img,
            (
                int(center_x - img.size[0] / 2),
                int(center_y - img.size[1] / 2),
            ),
        )

    return out
