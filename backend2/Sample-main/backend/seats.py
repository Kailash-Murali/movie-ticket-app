"""Seat recommendation algorithm: find best contiguous block."""

from backend.models import Seat, SeatBlock


# Row preference scores (middle/middle-back preferred)
_ROW_SCORES: dict[str, float] = {
    "A": 0.3,   # front
    "B": 0.7,   # middle-front
    "C": 1.0,   # middle (best)
    "D": 0.8,   # middle-back
    "E": 0.5,   # back
    "F": 0.3,   # far back
}


def find_best_seats(
    seats: list[Seat], group_size: int
) -> SeatBlock | None:
    """Find the best contiguous block of available seats for a group.

    Scoring:
    - horizontal center proximity: weight 0.7
    - preferred middle/middle-back row: weight 0.3

    Returns the highest-scoring block, or None if no valid block exists.
    """
    if group_size <= 0:
        return None

    # Group seats by row, sorted by seat number
    rows: dict[str, list[Seat]] = {}
    for seat in seats:
        rows.setdefault(seat.row, []).append(seat)

    for row_seats in rows.values():
        row_seats.sort(key=lambda s: s.number)

    best_block: SeatBlock | None = None
    best_score = -1.0

    for row_label, row_seats in rows.items():
        # Find contiguous available blocks
        blocks = _find_contiguous_available(row_seats, group_size)

        for block in blocks:
            score = _score_block(block, row_label, row_seats)
            if score > best_score:
                best_score = score
                best_block = SeatBlock(
                    seats=[s.id for s in block],
                    score=round(score, 4),
                )

    return best_block


def _find_contiguous_available(
    row_seats: list[Seat], group_size: int
) -> list[list[Seat]]:
    """Find all contiguous blocks of available seats of the required size."""
    blocks: list[list[Seat]] = []
    available_run: list[Seat] = []

    for seat in row_seats:
        if seat.status == "available":
            available_run.append(seat)
        else:
            # Reset run on booked seat
            if len(available_run) >= group_size:
                # Extract all windows of size group_size
                for i in range(len(available_run) - group_size + 1):
                    blocks.append(available_run[i : i + group_size])
            available_run = []

    # Don't forget the last run
    if len(available_run) >= group_size:
        for i in range(len(available_run) - group_size + 1):
            blocks.append(available_run[i : i + group_size])

    return blocks


def _score_block(
    block: list[Seat], row_label: str, row_seats: list[Seat]
) -> float:
    """Score a block based on center proximity (0.7) + row preference (0.3)."""
    total_seats_in_row = len(row_seats)
    if total_seats_in_row == 0:
        return 0.0

    # Center of row
    center = (total_seats_in_row + 1) / 2.0

    # Average position of block seats
    avg_pos = sum(s.number for s in block) / len(block)

    # Distance from center, normalized
    max_dist = (total_seats_in_row - 1) / 2.0
    if max_dist == 0:
        center_score = 1.0
    else:
        dist = abs(avg_pos - center)
        center_score = 1.0 - (dist / max_dist)

    # Row preference
    row_score = _ROW_SCORES.get(row_label.upper(), 0.5)

    return center_score * 0.7 + row_score * 0.3
