import sys
from PIL import Image

import line_interp
import segment_finder
import video_generator

im = Image.open(sys.argv[1])
num_frames = 52  # video will be 30 fps

segments = segment_finder.find_segments(im)

segment_frames = line_interp.interp_segments(segments, num_frames)

if len(sys.argv) > 2:
    video_generator.generate_video(segment_frames, im, filename=sys.argv[2])
else:
    video_generator.generate_video(segment_frames, im)
