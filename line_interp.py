from PIL import Image, ImageDraw
import numpy as np

# end segment points (using the 1280x720 video)
end_segments = np.array([
    [595, 212, 688, 262, 5],
    [688, 262, 791, 263, 5],
    [516, 266, 612, 223, 5],
    [450, 339, 516, 266, 5],
    [548, 351, 600, 228, 5],
    [599, 297, 652, 247, 5],
    [586, 353, 599, 297, 5],
    [644, 360, 678, 260, 5],
    [774, 370, 769, 264, 5],
])


def interp_segments(segments: np.ndarray, num_frames=60) -> np.ndarray:
    """
    Return the linearly interpolated points of each line segment for each frame.
    :param segments: array of segments returned by find_segments()
    :param num_frames: The number of frames to calculate
    :return: a 3-dimensional array [frame, segment, point]
    """
    # list to store each segment
    segment_frames = np.empty((segments.shape[0], num_frames, 5), float)

    for i in range(segments.shape[0]):
        # array to store the segment points of each frame (each index is a frame)
        segment_frames[i] = np.array([
            np.linspace(segments[i][0], end_segments[i][0], num_frames, dtype=int),
            np.linspace(segments[i][1], end_segments[i][1], num_frames, dtype=int),
            np.linspace(segments[i][2], end_segments[i][2], num_frames, dtype=int),
            np.linspace(segments[i][3], end_segments[i][3], num_frames, dtype=int),
            np.linspace(segments[i][4], end_segments[i][4], num_frames, dtype=int),
        ]).transpose()

    return np.transpose(segment_frames, (1, 0, 2))
