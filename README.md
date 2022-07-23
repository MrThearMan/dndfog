# DnD Fog

[![Coverage Status][coverage-badge]][coverage]
[![GitHub Workflow Status][status-badge]][status]
[![PyPI][pypi-badge]][pypi]
[![GitHub][licence-badge]][licence]
[![GitHub Last Commit][repo-badge]][repo]
[![GitHub Issues][issues-badge]][issues]
[![Python Version][version-badge]][pypi]

```shell
pip install dndfog
```

---

**Documentation**: [https://mrthearman.github.io/dndfog/](https://mrthearman.github.io/dndfog/)

**Source Code**: [https://github.com/MrThearMan/dndfog/](https://github.com/MrThearMan/dndfog/)

---

Create battlemaps for tabletop RPGs, like [D&D](https://www.dndbeyond.com/).

> Program is Windows only for now. This is due to the saving and loading widgets
> being Windows only (using pywin32). You're free to modify the code to add file
> loading and saving for other platforms.

![Example Map](https://github.com/MrThearMan/dndfog/blob/main/docs/img/example-map.png?raw=true)

## Features

- Infinite grid
- Add and remove a "[fog of war](https://en.wikipedia.org/wiki/Fog_of_war)" effect
- Import maps from image files
- Place, move and remove pieces on a grid (can be matched to image grid)
- Place 1x1, 2x2, 3x3, or 4x4 pieces
- Save and load file to JSON files (background image saved in the JSON file!)

## How to use

When installing from [pypi](https://pypi.org/), the library should come with a script
named `dndfog` that you can run. It should be available in your environment if
the `Python\Scripts` folder is set in PATH. You can also download an EXE from
the [GitHub releases](https://github.com/MrThearMan/dndfog/releases).

When the program opens, you need to select an image file to use as a background,
or a JSON data file to load a map from. You can also lauch the program with extra
arguments `--file=<filepath>` or `--gridsize=<size>` to change the opening parameters.

> The program does not autosave! You have to save (and override) the file yourself!

### Keyboard shortcuts

- Remove fog: `CTRL + Left mouse button`
- Add fog: `CTRL + Shift + Left mouse button`
- Add a piece: `Right mouse button`
- Remove a piece: `Double click: Right mouse button`
- Move a piece: `Click and drag: Left mouse button`
- Move camera: `Click and drag: Middle mouse button`
- Move background map: `ALT + Click and drag: Left mouse button`
- Zoom in: `Scroll wheel: Up`
- Zoom out: `Scroll wheel: Down`
- Select 1x1 piece placement: `1`
- Select 2x2 piece placement: `2`
- Select 3x3 piece placement: `3`
- Select 4x4 piece placement: `4`
- Show/hide fog: `F1`
- Show/hide grid: `F12`
- Save file: `CTRL + s`
- Open file: `CTRL + o`
- Quit program: `Esc`

## Known issues or lacking features

When zooming, the program grid and background map might not stay aligned,
if you have moved the background map. This is due to the background map offset
not being scaled correctly to the new zoom level. Usually this should be only
a few pixels, and you can fix it quickly by moving the background.

Gridsize can only be changed on initial lauch. Use the `--gridsize=<size>`
extra argument on first lauch to change the grid size, and when you get it
correct, save the file. There was some alignment issues with the background
map when I tried adding this, so I skipped it for now. Might add later.

There is no undo or redo. Might add later.

There is no way to mark/point on things on the map (apart from the mouse cursor).
Might add later.

[coverage-badge]: https://coveralls.io/repos/github/MrThearMan/dndfog/badge.svg?branch=main
[status-badge]: https://img.shields.io/github/workflow/status/MrThearMan/dndfog/Test
[pypi-badge]: https://img.shields.io/pypi/v/dndfog
[licence-badge]: https://img.shields.io/github/license/MrThearMan/dndfog
[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/dndfog
[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/dndfog
[version-badge]: https://img.shields.io/pypi/pyversions/dndfog
[loc-badge]: https://img.shields.io/tokei/lines/github.com/MrThearMan/dndfog
[downloads-badge]: https://img.shields.io/pypi/dm/dndfog

[coverage]: https://coveralls.io/github/MrThearMan/dndfog?branch=main
[status]: https://github.com/MrThearMan/dndfog/actions/workflows/test.yml
[pypi]: https://pypi.org/project/dndfog
[licence]: https://github.com/MrThearMan/dndfog/blob/main/LICENSE
[repo]: https://github.com/MrThearMan/dndfog/commits/main
[issues]: https://github.com/MrThearMan/dndfog/issues
