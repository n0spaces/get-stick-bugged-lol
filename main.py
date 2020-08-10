import sys

from PIL import Image

from generator import find_segments, interp_segments, generate_video

im = Image.open(sys.argv[1])

segments = find_segments(im)

segment_frames = interp_segments(segments)

if len(sys.argv) > 2:
    generate_video(segment_frames, im, filename=sys.argv[2])
else:
    generate_video(segment_frames, im)
