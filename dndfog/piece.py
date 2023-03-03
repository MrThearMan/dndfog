from random import randint

from dndfog.types import PieceData, PieceSize, orig_colors


def add_piece(
    add_place: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
    colors: list[tuple[int, int, int]],
    selected_size: PieceSize,
) -> None:
    overlap_with_other_pieces = any(
        (add_place[0] + x, add_place[1] + y) in pieces
        for x in range(selected_size.value)
        for y in range(selected_size.value)
    )
    if overlap_with_other_pieces:
        return

    color = (
        # Prefedined Color
        colors.pop(0)
        if len(colors) > 0
        # Random Color
        else (randint(0, 255), randint(0, 255), randint(0, 255))
    )

    for x in range(selected_size.value):
        for y in range(selected_size.value):
            pieces[(add_place[0] + x, add_place[1] + y)] = PieceData(
                parent=add_place,
                place=(add_place[0] + x, add_place[1] + y),
                color=color,
                size=selected_size,
                show=(x == 0 and y == 0),
            )


def remove_piece(
    next_place: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
    colors: list[tuple[int, int, int]],
) -> None:
    piece_data: PieceData | None = pieces.get(next_place, None)
    if piece_data is not None:
        place = piece_data["parent"]
        size = piece_data["size"]
        color = piece_data["color"]

        for x in range(size.value):
            for y in range(size.value):
                pieces.pop((place[0] + x, place[1] + y), None)
                if color in orig_colors and color not in colors:
                    colors.insert(0, color)


def move_piece(
    current_place: tuple[int, int],
    next_place: tuple[int, int],
    pieces: dict[tuple[int, int], PieceData],
) -> tuple[int, int]:
    piece_to_move = pieces[current_place]
    piece_place = piece_to_move["parent"]
    piece_size = piece_to_move["size"]

    movement = (next_place[0] - current_place[0], next_place[1] - current_place[1])
    current_self_positions = {
        (piece_place[0] + x, piece_place[1] + y) for x in range(piece_size.value) for y in range(piece_size.value)
    }

    next_self_positions = {(x + movement[0], y + movement[1]) for x, y in current_self_positions}
    no_overlap_with_other_pieces = not any(
        pos in pieces for pos in next_self_positions if pos not in current_self_positions
    )

    moving = current_place

    if next_place != current_place and no_overlap_with_other_pieces:
        # Remove own positions
        for self_pos in current_self_positions:
            pieces.pop(self_pos, None)

        # Add own positions back
        for self_pos in current_self_positions:
            pieces[(self_pos[0] + movement[0], self_pos[1] + movement[1])] = PieceData(
                parent=(piece_place[0] + movement[0], piece_place[1] + movement[1]),
                place=(self_pos[0] + movement[0], self_pos[1] + movement[1]),
                color=piece_to_move["color"],
                size=piece_size,
                show=(self_pos[0] == piece_place[0] and self_pos[1] == piece_place[1]),
            )

        moving = next_place

    return moving
