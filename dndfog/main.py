from argparse import ArgumentParser, Namespace

from dndfog.gameloop import run
from dndfog.saving import open_file_dialog


def start() -> None:
    parser = ArgumentParser()
    parser.add_argument("file", default=None, help="The file to load")
    try:
        args = parser.parse_args()
    except AttributeError:  # exe opened without args
        args = Namespace(file=None)

    if args.file is not None:
        map_file = str(args.file)
    else:
        map_file = open_file_dialog(
            title="Select a background map, or a json data file",
            ext=[("PNG file", "png"), ("JPG file", "jpg"), ("JSON file", "json"), ("DND fog file", "dndfog")],
        )

    if not map_file:
        msg = "No file selected."
        raise SystemExit(msg)

    run(map_file)


if __name__ == "__main__":
    start()
