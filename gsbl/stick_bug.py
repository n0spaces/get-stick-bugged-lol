import numpy as np
from PIL import Image, ImageDraw
from pylsd.lsd import lsd
from moviepy import editor

import os

# get media file paths
pkg_path = os.path.dirname(os.path.realpath(__file__))
stick_bug_path = os.path.join(pkg_path, 'media/stick_bug.mp4')
audio_path = os.path.join(pkg_path, 'media/audio.wav')


class StickBug:
    def __init__(self):
        self._img = None
        self._video = None
        self._segments = np.empty((9, 5), float)

        self._img_processed = False
        self._img_scaled = None
        self._img_offset = (0, 0)

        self._segments_processed = False
        self._lsd_scale = 0.5

        self._video_processed = False
        self._video_resolution = (1280, 720)
        self._line_color = (255, 255, 211)
        self._line_bg_color = (125, 115, 119)

        # end segment points (using the 1280x720 video)
        # TODO: support multiple resolutions
        self._end_segments = np.array([
            [595, 212, 688, 262, 8],
            [688, 262, 791, 263, 8],
            [516, 266, 612, 223, 8],
            [450, 339, 516, 266, 8],
            [548, 351, 600, 228, 8],
            [599, 297, 652, 247, 8],
            [586, 353, 599, 297, 8],
            [644, 360, 678, 260, 8],
            [774, 370, 769, 264, 8],
        ])

    @property
    def image(self):
        """The source image as a PIL Image object"""
        return self._img

    @image.setter
    def image(self, im: Image.Image):
        """
        Set the image. This resets the line segments and video.
        :param im: PIL Image
        """
        self._img = im
        self.process_image()
        self.clear_segments()
        self.clear_video()

    @property
    def segments(self):
        """
        The array of line segment points. Each row is a segment with the values [x1, y1, x2, y2, width].
        If the array hasn't been processed yet, that's done the next time this is called.
        """
        if not self._segments_processed:
            self.process_segments()
        return self._segments

    @segments.setter
    def segments(self, arr: np.ndarray):
        """
        Set the line segments array. This resets the video.
        :param arr: numpy array of 9 rows containing [x1, y1, x2, y2, width]
        """
        self._segments = arr
        self._segments_processed = True
        self.clear_video()

    def clear_segments(self):
        """Resets line segments to be calculated again. Called whenever self.image is set."""
        self._segments_processed = False
        self.clear_video()

    @property
    def video(self):
        """The moviepy VideoClip. If the video hasn't been generated yet, that's done the next time this is called."""
        if not self._video_processed:
            self.process_video()
        return self._video

    def clear_video(self):
        """Resets the video to be generated again. Called whenever self.image or self.segments are set."""
        self._video_processed = False

    def process_image(self):
        """Calculate the image's offset and scale in the video."""
        # resize image to fit video resolution without cropping
        scale = min(self._video_resolution[0] / self._img.width, self._video_resolution[1] / self._img.height)
        self._img_scaled = self._img.resize((int(self._img.width * scale), int(self._img.height * scale)))

        # calculate image offset to center image in video
        self._img_offset = ((self._video_resolution[0] - self._img_scaled.width) // 2,
                            (self._video_resolution[1] - self._img_scaled.height) // 2)

        self._img_processed = True

    def process_segments(self):
        """Run the line segment detector."""
        if self._img is None:
            raise ValueError('image must be set before running the line segment detector')

        img_gray = np.array(self._img_scaled.convert('L'))

        lsd_result = lsd(img_gray, scale=self._lsd_scale)

        # sort by distance and keep the 9 longest segments
        # add a column to store distance
        rows, cols = lsd_result.shape
        segments_d = np.empty((rows, cols + 1))
        segments_d[:, :-1] = lsd_result

        # find distance of each line segment
        for i in range(segments_d.shape[0]):
            x1, y1, x2, y2, *_ = segments_d[i]
            segments_d[i, 5] = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)  # distance formula

        # sort and remove distance column
        lsd_sorted = segments_d[segments_d[:, 5].argsort()[::-1]][:, :-1]

        # keep only the 9 longest segments
        self.segments = lsd_sorted[:9]

        self._segments_processed = True

    def process_video(self):
        """
        Process everything needed to generate the video. This includes calculating the line interpolation, drawing the
        frames, and creating the VideoClip object. The video will be in the following format:
        1. The source image
        2. Line segments start appearing
        3. Source image disappears and background changes
        4. Line segments interpolate to form a stick bug
        5. The stick bug video
        """
        if self._img is None:
            raise ValueError('image must be set before the video can be generated')

        num_frames = 52  # number of frames that the lines will be moving

        # CALCULATE LINE INTERPOLATION
        # array to store the points of each line segment in each frame.
        segment_frames = np.empty((self.segments.shape[0], num_frames, 5), float)

        # add image offset to segment points so segments are aligned with centered image
        segments_centered = self._segments
        segments_centered[:, 0:3:2] += self._img_offset[0]
        segments_centered[:, 1:4:2] += self._img_offset[1]

        for i in range(self._segments.shape[0]):
            segment_frames[i] = np.array([
                np.linspace(self._segments[i][0], self._end_segments[i][0], num_frames, dtype=int),
                np.linspace(self._segments[i][1], self._end_segments[i][1], num_frames, dtype=int),
                np.linspace(self._segments[i][2], self._end_segments[i][2], num_frames, dtype=int),
                np.linspace(self._segments[i][3], self._end_segments[i][3], num_frames, dtype=int),
                np.linspace(self._segments[i][4], self._end_segments[i][4], num_frames, dtype=int),
            ]).transpose()

        segment_frames = np.transpose(segment_frames, (1, 0, 2))  # [frame, segment, point]

        # GENERATE VIDEO
        # list of clips in the video
        clips = []

        # first clip is just the source image
        # center the image on a black background
        frame = Image.new('RGB', self._video_resolution)
        frame.paste(self._img_scaled, tuple(self._img_offset))
        clips.append(editor.ImageClip(np.array(frame), duration=1))

        # line segments start appearing
        # add an ImageClip for each segment
        draw = ImageDraw.Draw(frame)
        for segment in segment_frames[0]:
            x1, y1, x2, y2, w = segment
            draw.line((x1, y1, x2, y2), fill=self._line_color, width=int(w))
            clips.append(editor.ImageClip(np.array(frame), duration=0.33))

        # one more slightly longer clip for the last segment
        clips.append(editor.ImageClip(np.array(frame), duration=1))

        # redraw lines with the line background color (gray by default)
        draw.rectangle([(0, 0), self._video_resolution], self._line_bg_color)
        for segment in segment_frames[0]:
            x1, y1, x2, y2, w = segment
            draw.line((x1, y1, x2, y2), fill=self._line_color, width=int(w))
        clips.append(editor.ImageClip(np.array(frame), duration=0.75))

        # use an ImageSequenceClip for the line interpolation
        interp_frames = []
        for i in range(segment_frames.shape[0]):
            draw.rectangle([(0, 0), self._video_resolution], self._line_bg_color)
            for segment in segment_frames[i]:
                x1, y1, x2, y2, w = segment
                draw.line((x1, y1, x2, y2), fill=self._line_color, width=int(w))
            interp_frames.append(np.asarray(frame))
        clips.append(editor.ImageSequenceClip(interp_frames, 30))

        # concatenate all the clips and add the audio
        all_clips = editor.concatenate_videoclips(clips)
        all_clips = all_clips.set_audio(editor.AudioFileClip(audio_path))

        # add stick bug video to the end
        stick_bug_clip = editor.VideoFileClip(stick_bug_path).without_audio()
        self._video = editor.concatenate_videoclips([all_clips, stick_bug_clip])

        self._video_processed = True
