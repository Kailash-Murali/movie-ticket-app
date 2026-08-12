from app.models.seat import Seat
from app.algorithms.seat_recommendation import recommend_seats_for_show

def test_seat_recommendation_adjacent_group():
    # Mock 60 seats (Rows A-F, 1-10)
    seats = []
    for r in ["A", "B", "C", "D", "E", "F"]:
        for num in range(1, 11):
            seats.append(Seat(
                id=f"S001-{r}{num}",
                show_id="S001",
                row=r,
                number=num,
                seat_code=f"{r}{num}",
                type="Standard" if r in ["A", "B"] else "Premium",
                status="available",
                price=300
            ))

    rec = recommend_seats_for_show(seats, group_size=4, preference="best_view")
    assert len(rec["recommended_seats"]) == 4
    # Check that contiguous adjacent numbers in optimal middle row (Row C or D) were selected
    codes = rec["recommended_seats"]
    assert codes[0][0] in ["C", "D"] # Row C or D
    nums = [int(c[1:]) for c in codes]
    assert nums == list(range(nums[0], nums[0] + 4))

def test_seat_recommendation_sold_out():
    seats = [
        Seat(id="S001-A1", show_id="S001", row="A", number=1, seat_code="A1", type="Standard", status="booked", price=200)
    ]
    rec = recommend_seats_for_show(seats, group_size=2)
    assert len(rec["recommended_seats"]) == 0
    assert rec["score"] == 0.0
