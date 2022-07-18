# DnD Fog

```shell
pip install dndfog
```

Create battlemaps for tabletop RPGs, like [D&D](https://www.dndbeyond.com/).

> Program is Windows only for now. This is due to the saving and loading widgets
> being Windows only (using pywin32). You're free to modify the code to add file
> loading and saving for other platforms.

![Example Map](img/example-map.png)

## Features

- Infinite grid
- Add and remove a [fog of war](https://en.wikipedia.org/wiki/Fog_of_war) effect
- Import maps from image files
- Place, move and remove pieces on a grid (can be matched to image grid)
- Save and load file to JSON files (background image saved in the JSON file!)

## How to use

When the program opens, you need to select an image file to use as a background,
or a JSON data file to load a map from. You can also lauch the program with extra
arguments `--file=<filepath>` or `--gridsize=<size>` to change the opening parameters.

> The program does not autosave! You have to save (and override) the file yourself!

### Keyboard shortcuts

- Remove fog: `CTRL + Left mouse button`
- Add fog: `CTRL + Shift + Left mouse button`
- Add a piece: `Right mouse button`
- Remove a piece: `Double click: Left mouse button`
- Move a piece: `Click and drag: Left mouse button`
- Move camera: `Click and drag: Middle mouse button`
- Move background map: `ALT + Click and drag: Left mouse button`
- Zoom in: `Scroll wheel: Up`
- Zoom out: `Scroll wheel: Down`
- Show/hide fog: `1`
- Show/hide grid: `g`
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
