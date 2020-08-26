import os
from typing import Union

import numpy as np
from PIL import Image, ImageDraw
from moviepy import editor
from pylsd.lsd import lsd

# static media files
pkg_path = os.path.dirname(os.path.realpath(__file__))
video_stick_bug = editor.VideoFileClip(os.path.join(pkg_path, 'media/stick_bug.mp4'))
audio_notes = [
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note0.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note1.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note2.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note3.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note4.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note5.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note6.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note7.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note8.wav')),
    editor.AudioFileClip(os.path.join(pkg_path, 'media/note9.wav')),
]
audio_transform = editor.AudioFileClip(os.path.join(pkg_path, 'media/transform.wav'))


class StickBug:
    def __init__(self, img: Union[Image.Image, str] = None, video_resolution=(720, 720), lsd_scale=0.8,
                 img_bg_color=(0, 0, 0), line_color=(255, 255, 211), line_bg_color=(125, 115, 119)):
        """
        Class that generates a stick bug meme from an image.
        :param img: The source image. Can be a PIL Image, a filepath, or left empty.
        :param video_resolution: The resolution of the generated video.
        :param lsd_scale: The image scaled passed to the LSD. This does not affect the image scale in the video.
        :param img_bg_color: The background color of the video while the image is visible.
        :param line_color: The color of the line segments.
        :param line_bg_color: The background color of the video when the image disappears.
        """
        if type(img) == str:
            self._img = Image.open(img)
        else:
            self._img = img
        self._img_processed = False
        self._img_scaled = None
        self._img_offset = (0, 0)

        self._segments = np.empty((9, 5), float)
        self._segments_processed = False
        self._lsd_scale = lsd_scale

        self._video = None
        self._video_processed = False
        self._video_resolution = tuple(video_resolution)
        self._img_bg_color = tuple(img_bg_color)
        self._line_color = tuple(line_color)
        self._line_bg_color = tuple(line_bg_color)
        self._stick_bug_video_offset = (0, 0)

        # end segment points
        self._end_segments = np.array([
            [315, 212, 408, 262, 8],
            [408, 262, 511, 263, 8],
            [236, 266, 332, 223, 8],
            [170, 339, 236, 266, 8],
            [268, 351, 320, 228, 8],
            [319, 297, 372, 247, 8],
            [306, 353, 319, 297, 8],
            [364, 360, 398, 260, 8],
            [494, 370, 489, 264, 8],
        ])

        if self._img is not None:
            self.process_image()

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
        if self._img is not None:
            self.process_image()
        self.clear_segments()

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
        Set the line segments array. This clears the video.
        :param arr: numpy array of 9 rows containing [x1, y1, x2, y2, width]
        """
        self._segments = arr
        self._segments_processed = True
        self.clear_video()

    @property
    def video(self):
        """The moviepy VideoClip. If the video hasn't been generated yet, that's done the next time this is called."""
        if not self._video_processed:
            self.process_video()
        return self._video

    @property
    def lsd_scale(self):
        """
        The scale of the image passed in the line segment detector. Lowering this may improve results, especially with
        large images. This does not affect the image scale in the video.
        """
        return self._lsd_scale

    @lsd_scale.setter
    def lsd_scale(self, value):
        """Set the LSD scale. This clears the segments and video."""
        self._lsd_scale = value
        self.clear_segments()

    @property
    def img_bg_color(self):
        """The background color of the video while the image is visible."""
        return self._img_bg_color

    @img_bg_color.setter
    def img_bg_color(self, rgb):
        """
        Set the image background color. This clears the video.
        :param rgb: tuple (R, G, B)
        """
        self._img_bg_color = tuple(rgb)
        self.clear_video()

    @property
    def line_color(self):
        """The color of the line segments in the video."""
        return self._line_color

    @line_color.setter
    def line_color(self, rgb):
        """
        Set the color of the line segments. This clears the video.
        :param rgb: tuple (R, G, B)
        """
        self._line_color = tuple(rgb)
        self.clear_video()

    @property
    def line_bg_color(self):
        """The background color of the video after the image disappears."""
        return self._line_bg_color

    @line_bg_color.setter
    def line_bg_color(self, rgb):
        """
        Set the video background color after the image disappears. This clears the video.
        :param rgb: tuple (R, G, B)
        """
        self._line_bg_color = tuple(rgb)
        self.clear_video()

    @property
    def video_resolution(self):
        """The resolution of the generated video."""
        return self._video_resolution

    @video_resolution.setter
    def video_resolution(self, res):
        """
        Set the video resolution. This clears the video and segments, since the segments have to be adjusted to the new
        resolution.
        :param res: video width and height as a tuple
        """
        self._video_resolution = tuple(res)
        self.process_image()
        self.clear_segments()

    def clear_segments(self):
        """Resets line segments to be calculated again. Called whenever self.image is set."""
        self._segments_processed = False
        self.clear_video()

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

        # scale stick bug video and end segments
        stick_bug_scale = min(self._video_resolution[0] / video_stick_bug.w,
                              self._video_resolution[1] / video_stick_bug.h)

        num_frames = 52  # number of frames that the lines will be moving

        # CALCULATE LINE INTERPOLATION
        # array to store the points of each line segment in each frame.
        segment_frames = np.empty((self.segments.shape[0], num_frames, 5), float)

        # add image offset to segment points so segments are aligned with centered image
        segments_centered = self._segments
        segments_centered[:, 0:3:2] += self._img_offset[0]
        segments_centered[:, 1:4:2] += self._img_offset[1]

        end_segments_offset = ((self._video_resolution[0] - video_stick_bug.w * stick_bug_scale) // 2,
                               (self._video_resolution[1] - video_stick_bug.h * stick_bug_scale) // 2)
        end_segments_centered = self._end_segments * stick_bug_scale
        end_segments_centered[:, 0:3:2] += end_segments_offset[0]
        end_segments_centered[:, 1:4:2] += end_segments_offset[1]

        for i in range(self._segments.shape[0]):
            segment_frames[i] = np.array([
                np.linspace(self._segments[i][0], end_segments_centered[i][0], num_frames, dtype=int),
                np.linspace(self._segments[i][1], end_segments_centered[i][1], num_frames, dtype=int),
                np.linspace(self._segments[i][2], end_segments_centered[i][2], num_frames, dtype=int),
                np.linspace(self._segments[i][3], end_segments_centered[i][3], num_frames, dtype=int),
                np.linspace(self._segments[i][4], end_segments_centered[i][4], num_frames, dtype=int),
            ]).transpose()

        segment_frames = np.transpose(segment_frames, (1, 0, 2))  # [frame, segment, point]

        # GENERATE VIDEO
        # list of clips in the video
        clips = []

        # first clip is just the source image
        # center the image on a black background
        frame = Image.new('RGB', self._video_resolution, self._img_bg_color)
        frame.paste(self._img_scaled, tuple(self._img_offset))
        clips.append(editor.ImageClip(np.array(frame), duration=1))

        # line segments start appearing
        # add an ImageClip for each segment
        draw = ImageDraw.Draw(frame)
        for i in range(segment_frames[0].shape[0]):
            x1, y1, x2, y2, w = segment_frames[0][i]
            draw.line((x1, y1, x2, y2), fill=self._line_color, width=int(w))
            clips.append(editor.ImageClip(np.array(frame), duration=0.33).set_audio(audio_notes[i]))

        # one more slightly longer clip for the last segment
        clips.append(editor.ImageClip(np.array(frame), duration=1))

        # redraw lines with the line background color
        draw.rectangle([(0, 0), self._video_resolution], self._line_bg_color)
        for segment in segment_frames[0]:
            x1, y1, x2, y2, w = segment
            draw.line((x1, y1, x2, y2), fill=self._line_color, width=int(w))
        clips.append(editor.ImageClip(np.array(frame), duration=0.75).set_audio(audio_notes[9]))

        # use an ImageSequenceClip for the line interpolation
        interp_frames = []
        for i in range(segment_frames.shape[0]):
            draw.rectangle([(0, 0), self._video_resolution], self._line_bg_color)
            for segment in segment_frames[i]:
                x1, y1, x2, y2, w = segment
                draw.line((x1, y1, x2, y2), fill=self._line_color, width=int(w))
            interp_frames.append(np.asarray(frame))
        interp_clip = editor.ImageSequenceClip(interp_frames, 30)
        clips.append(interp_clip.set_audio(audio_transform.set_end(interp_clip.end)))

        # concatenate all the clips and add the audio
        all_clips = editor.concatenate_videoclips(clips)
        # all_clips = all_clips.set_audio(editor.AudioFileClip(audio_path))

        # add stick bug video to the end
        stick_bug_clip = video_stick_bug.resize(stick_bug_scale).set_start(all_clips.end).set_position('center')
        self._video = editor.CompositeVideoClip([all_clips, stick_bug_clip])

        self._video_processed = True

    def save_video(self, fp: str):
        """Save the video file"""
        self.video.write_videofile(fp)
