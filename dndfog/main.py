from argparse import ArgumentParser

from dndfog.gameloop import run
from dndfog.saving import open_file_dialog


def start() -> None:
    parser = ArgumentParser()
    parser.add_argument("file", default=None)
    args = parser.parse_args()

    if args.file is not None:
        map_file = str(args.file)
    else:
        map_file = open_file_dialog(
            title="Select a background map, or a json data file",
            ext=[("PNG file", "png"), ("JPG file", "jpg"), ("JSON file", "json"), ("DND fog file", "dndfog")],
        )

    if not map_file:
        raise SystemExit("No file selected.")

    run(map_file)


if __name__ == "__main__":
    start()
