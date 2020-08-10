import numpy as np
from PIL import Image
from pylsd import lsd


def find_segments(im: Image, num_segments=9, sort_by_width=False) -> np.ndarray:
    """
    Find the largest line segments in an image and return an array of segment points.
    :param im: PIL Image object
    :param num_segments: Number of segments to return
    :param sort_by_width: If true, return segments with the largest width rather than distance
    :return: An array of line segment points [x1, y1, x2, y2, width]
    """
    # resize image to fit in video (1280x720) without cropping
    scale = min(1280 / im.width, 720 / im.height)
    im = im.resize((int(im.width * scale), int(im.height * scale)))
    x_offset = (1280 - im.width) // 2
    y_offset = (720 - im.height) // 2

    im_gray = np.array(im.convert('L'))

    segments = lsd(im_gray)

    # add offset to segment points since the image will be centered in the video
    segments[:, 0:3:2] += x_offset  # add x_offset to column 0 and 2
    segments[:, 1:4:2] += y_offset  # add Y_offset to column 1 and 3

    # sort by distance or width of segments
    if sort_by_width:
        segments = segments[segments[:, 4].argsort()[::-1]]
    else:
        # add a column to store distance
        rows, cols = segments.shape
        segments_d = np.empty((rows, cols + 1))
        segments_d[:, :-1] = segments

        # find length of each line segment
        for i in range(segments_d.shape[0]):
            x1, y1, x2, y2, *_ = segments_d[i]
            segments_d[i, 5] = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # distance formula

        # sort and remove distance column
        segments = segments_d[segments_d[:, 5].argsort()[::-1]][:, :-1]

    return segments[:num_segments]
