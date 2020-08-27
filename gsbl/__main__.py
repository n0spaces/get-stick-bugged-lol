def main():
    import argparse

    parser = argparse.ArgumentParser(prog='gsbl', description="Create a 'get stick bugged lol' video from an image.")
    parser.add_argument('input',
                        help="the image file to be used to generate the video (png, jpg, ...). For best results, make"
                             "sure the image doesn't have any black or white borders surrounding it.")
    parser.add_argument('output', help='the video file to be generated and saved (mp4, webm, ...)')
    parser.add_argument('-r --resolution', dest='resolution', nargs=2, type=int, default=[720, 720],
                        metavar=('WIDTH', 'HEIGHT'), help='width and height of the video (default: 720 720)')
    parser.add_argument('--img-bg-color', dest='img_bg_color', nargs=3, type=int, default=[0, 0, 0],
                        metavar=('R', 'G', 'B'),
                        help='RGB background color while the image is visible (default: 0 0 0)')
    parser.add_argument('--line-color', dest='line_color', nargs=3, type=int, default=[255, 255, 211],
                        metavar=('R', 'G', 'B'), help='RGB color of line segments (default: 255 255 211)')
    parser.add_argument('--line-bg-color', dest='line_bg_color', nargs=3, type=int, default=[125, 115, 119],
                        metavar=('R', 'G', 'B'),
                        help='RGB background color after image disappears (default: 125 115 119)')
    parser.add_argument('-s --scale', dest='lsd_scale', type=float, default=0.8, metavar='SCALE',
                        help='the image scale passed to the line segment detector. Slightly lowering this may improve '
                             'results in large images. This does not affect the image scale in the video (try '
                             '--resolution instead). (default: 0.8)')

    args = parser.parse_args()

    from gsbl.stick_bug import StickBug

    sb = StickBug(img=args.input, video_resolution=args.resolution, lsd_scale=args.lsd_scale,
                  img_bg_color=args.img_bg_color, line_color=args.line_color, line_bg_color=args.line_bg_color)
    sb.save_video(args.output)


if __name__ == '__main__':
    main()
