from argparse import ArgumentParser

from dndfog.draw import main
from dndfog.saving import open_file_dialog


def start() -> None:
    parser = ArgumentParser()
    parser.add_argument("--file", default=None)
    parser.add_argument("--gridsize", default=36)
    args = parser.parse_args()

    if args.file is not None:
        start_file = str(args.file)
    else:
        start_file = open_file_dialog(
            title="Select a background map, or a json data file",
            ext=[("PNG file", "png"), ("JPG file", "jpg"), ("JSON file", "json")],
        )

    if not start_file:
        raise SystemExit("No file selected.")

    main(start_file, int(args.gridsize))


if __name__ == "__main__":
    start()
