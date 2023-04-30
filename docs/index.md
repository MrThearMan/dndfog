# DnD Fog

[![GitHub Workflow Status][status-badge]][status]
[![PyPI][pypi-badge]][pypi]
[![GitHub][licence-badge]][licence]
[![GitHub Last Commit][repo-badge]][repo]
[![GitHub Issues][issues-badge]][issues]
[![Downloads][downloads-badge]][pypi]
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
- Add and remove a [fog of war](https://en.wikipedia.org/wiki/Fog_of_war) effect
- Import maps from image files
- Place, move and remove pieces on a grid (can be matched to image grid)
- Place 1x1, 2x2, 3x3, or 4x4 pieces
- Make markings on the map to show areas of effect or point out things to the players
- Save and load file to a single JSON file (no need to keep the image file separately!)

## How to use

When installing from [pypi](https://pypi.org/), the library should come with a script
named `dndfog` that you can run. It should be available in your environment if
the `Python\Scripts` folder is set in PATH. You can also download an EXE from
the [GitHub releases](https://github.com/MrThearMan/dndfog/releases).

When the program opens, you need to select an image file to use as a background,
or a JSON data file to load a map from. You can also lauch the program with
a positional argument `<filepath>` to add an initial file.

> The program does not autosave! You have to save (and override) the file yourself!

### Keyboard shortcuts

Toolbar:
- Open/close the toolbar: `TAB`
- Select tool from the toolbar: Quick select with the number keys `1-9` or click the
  tool button with `Left mouse button` when the toolbar is open

Camera:
- Move camera: `Click and drag: Middle mouse button`
- Zoom in: _Any tool except the `grid` tool_ selected from the toolbar + `Scroll wheel: Up`
- Zoom out: _Any tool except the `grid` tool_ selected from the toolbar + `Scroll wheel: Down`

Piece (quick select: `1`):
- Add a piece: Select the `piece` tool from the toolbar + `Right mouse button` on an empty square
- Remove a piece: Select the `piece` tool from the toolbar  + `Right mouse button` on a piece
- Move a piece: Select the `piece` tool from the toolbar  + `Click and drag: Left mouse button`

Fog (quick select: `2`):
- Add fog: Select the `fog` tool from the toolbar  + `Left mouse button`
- Remove fog: Select the `fog` tool from the toolbar  + `Right mouse button`
- Show/hide fog: `F1` or the checkbox in the `fog` toolbar
- Change fog size: Select the size to use from the `size` selector in the `fog` toolbar

Map (quick select: `3`):
- Move map image: Select the `map` tool from the toolbar + `Click and drag: Left mouse button`

Grid (quick select: `4`):
- Increase gridsize: Select the `grid` tool from the toolbar + `Scroll wheel: Up`
- Decrease gridsize: Select the `grid` tool from the toolbar + `Scroll wheel: Down`
- Show/hide grid: `F2` or the checkbox in the `fog` toolbar

Mark (quick select: `5`):
- Make markings: Select the `mark` tool from the toolbar + `Click and drag: Left mouse button`
- Erase markings: Select the `mark` tool from the toolbar + `Click and drag: Right mouse button`
- Clear markings: Click the `clear` button in the `mark` toolbar
- Change marker color: Use the color selector in the `mark` toolbar

Misc:
- Save file: `CTRL + S` (will skip file dialog if json data file already exists)
- Save file as: `CTRL + Shift + S` (will always open a file dialog)
- Open file: `CTRL + O`
- Quit program: Press the X mutton on the window

## Known issues or lacking features

- Matching program gridsize to background gridsize is a bit awkward
- When zooming, the program grid and background map might not stay aligned
- It's hard to keep track of combat, since there is no built-in turn order tracking
- It's too easy to accidentally remove fog you didn't mean to. There should be some way to
  layer fog, so that only some of it can be removed
- Markings do not scale when zooming
- There is no undo or redo
- There is no way to add pictures to pieces to identify them better

[status-badge]: https://img.shields.io/github/actions/workflow/status/MrThearMan/dndfog/test.yml?branch=main
[pypi-badge]: https://img.shields.io/pypi/v/dndfog
[licence-badge]: https://img.shields.io/github/license/MrThearMan/dndfog
[repo-badge]: https://img.shields.io/github/last-commit/MrThearMan/dndfog
[issues-badge]: https://img.shields.io/github/issues-raw/MrThearMan/dndfog
[version-badge]: https://img.shields.io/pypi/pyversions/dndfog
[downloads-badge]: https://img.shields.io/pypi/dm/dndfog

[status]: https://github.com/MrThearMan/dndfog/actions/workflows/test.yml
[pypi]: https://pypi.org/project/dndfog
[licence]: https://github.com/MrThearMan/dndfog/blob/main/LICENSE
[repo]: https://github.com/MrThearMan/dndfog/commits/main
[issues]: https://github.com/MrThearMan/dndfog/issues
