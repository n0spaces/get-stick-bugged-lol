import numpy as np
from PIL import Image


class StickBug:
    def __init__(self):
        self._image = None
        self._video = None
        self._segments = np.empty((9, 5), float)

        self._segments_processed = False
        self._video_processed = False

    @property
    def image(self):
        """The source image as a PIL Image object"""
        return self._image

    @image.setter
    def image(self, im: Image):
        """
        Set the image. This resets the line segments and video.
        :param im: PIL Image
        """
        self._image = im
        self.clear_segments()
        self.clear_video()

    @property
    def segments(self):
        """
        The array of line segment points. Each row is a segment with the values [x1, y1, x2, y2, width].
        If the array hasn't been processed yet, that's done the next time this is called.
        """
        return self._segments

    @segments.setter
    def segments(self, arr: np.ndarray):
        """
        Set the line segments array. This resets the video.
        :param arr: numpy array of 9 rows containing [x1, y1, x2, y2, width]
        """
        self._segments = arr
        self.clear_video()

    @property
    def video(self):
        """The moviepy VideoClip. If the video hasn't been generated yet, that's done the next time this is called."""
        return self._video

    def clear_segments(self):
        """Resets line segments. Called whenever self.image is set, but can also be called manually."""
        self._segments_processed = False

    def clear_video(self):
        """Resets the video. Called whenever self.image or self.segments are set, but can also be called manually."""
        self._video_processed = False

