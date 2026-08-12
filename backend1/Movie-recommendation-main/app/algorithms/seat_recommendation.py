from typing import List, Dict, Any, Optional
from app.models.seat import Seat

def recommend_seats_for_show(
    seats: List[Seat],
    group_size: int = 2,
    preference: Optional[str] = "best_view"
) -> Dict[str, Any]:
    """
    Finds and ranks seat options based on availability, group size, and user preference.
    """
    if group_size < 1:
        group_size = 1

    # Filter available seats only
    available_seats = [s for s in seats if s.status == "available"]

    if not available_seats:
        return {
            "recommended_seats": [],
            "recommended_seat_ids": [],
            "score": 0.0,
            "total_price": 0,
            "reason": "No seats are available for this show."
        }

    # Group available seats by row
    seats_by_row: Dict[str, List[Seat]] = {}
    for s in available_seats:
        seats_by_row.setdefault(s.row, []).append(s)

    # Sort seats in each row by seat number ascending
    for row in seats_by_row:
        seats_by_row[row].sort(key=lambda x: x.number)

    candidates = []

    # 1. Search for contiguous adjacent seats in the same row
    for row, row_seats in seats_by_row.items():
        if len(row_seats) >= group_size:
            for i in range(len(row_seats) - group_size + 1):
                window = row_seats[i : i + group_size]
                # Check if contiguous numbers
                numbers = [s.number for s in window]
                if numbers == list(range(numbers[0], numbers[0] + group_size)):
                    score, reason = score_seat_window(window, preference, group_size)
                    candidates.append({
                        "seats": window,
                        "score": score,
                        "reason": reason
                    })

    # 2. If no single contiguous block found, fallback to split adjacent seats across closest rows
    if not candidates:
        available_seats.sort(key=lambda s: (abs(ord(s.row) - ord('D')), abs(s.number - 5.5)))
        window = available_seats[:group_size]
        score = 60.0
        reason = f"Closest available {group_size} seats (separate positions)."
        candidates.append({
            "seats": window,
            "score": score,
            "reason": reason
        })

    # Pick top scoring candidate
    candidates.sort(key=lambda x: x["score"], reverse=True)
    best_candidate = candidates[0]

    best_seats: List[Seat] = best_candidate["seats"]
    seat_codes = [s.seat_code for s in best_seats]
    seat_ids = [s.id for s in best_seats]
    total_price = sum(s.price for s in best_seats)

    return {
        "recommended_seats": seat_codes,
        "recommended_seat_ids": seat_ids,
        "score": best_candidate["score"],
        "total_price": total_price,
        "reason": best_candidate["reason"]
    }

def score_seat_window(window: List[Seat], preference: Optional[str], group_size: int) -> tuple[float, str]:
    score = 70.0  # Base contiguous score
    reasons = []

    row = window[0].row
    avg_num = sum(s.number for s in window) / len(window)
    center_dist = abs(avg_num - 5.5)

    # Row position score: Rows C and D are optimal eye-level center rows
    if row in ["C", "D"]:
        score += 15.0
        reasons.append("Optimal middle row viewing height")
    elif row in ["E", "F"]:
        score += 10.0
        reasons.append("Premium recliner row position")
    else:
        score += 5.0

    # Horizontal center score
    if center_dist <= 1.5:
        score += 15.0
        reasons.append("Centered directly in front of the screen")
    elif center_dist <= 2.5:
        score += 8.0
        reasons.append("Good central view")

    # Preference specific adjustments
    pref = (preference or "best_view").lower()
    if "cheapest" in pref:
        min_price = min(s.price for s in window)
        if min_price <= 250:
            score += 20.0
            reasons.append("Most budget-friendly seat tier")
    elif "aisle" in pref:
        has_aisle = any(s.number in [1, 10] for s in window)
        if has_aisle:
            score += 20.0
            reasons.append("Includes quick-access aisle seats")
    elif "recliner" in pref or "luxury" in pref:
        if any(s.type == "Recliner" for s in window):
            score += 25.0
            reasons.append("Luxury recliner seating")

    if group_size > 1:
        reasons.insert(0, f"{group_size} adjacent seats in Row {row}")
    else:
        reasons.insert(0, f"Seat {window[0].seat_code} in Row {row}")

    final_score = round(min(100.0, score), 1)
    explanation = ". ".join(reasons) + "."

    return final_score, explanation
