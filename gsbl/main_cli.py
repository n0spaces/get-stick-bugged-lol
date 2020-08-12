def main():
    import argparse
    import gsbl

    parser = argparse.ArgumentParser(description="Create a 'get stick bugged lol' video from an image.")
    parser.add_argument('input', help='the image file to be used to generate the video (png, jpg, ...)')
    parser.add_argument('output', help='the video file to be generated and saved (mp4, webm, ...)')
    parser.add_argument('--line-color', dest='line_color', nargs=3, type=int, default=[255, 255, 211],
                        metavar=('R', 'G', 'B'), help='RGB color to use for line segments (default: 255 255 211)')
    parser.add_argument('--bg-color', dest='bg_color', nargs=3, type=int, default=[125, 115, 119], metavar=('R', 'G', 'B'),
                        help='RGB color to use for background after image disappears (default: 125 115 119)')

    args = parser.parse_args()

    video = gsbl.generate_stick_bug(args.input, tuple(args.line_color), tuple(args.bg_color))
    gsbl.save_video(video, args.output)


if __name__ == '__main__':
    main()
