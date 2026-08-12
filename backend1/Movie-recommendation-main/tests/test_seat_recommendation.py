import pytest
from app.models.seat import Seat
from app.algorithms.seat_recommendation import recommend_seats_for_show

def generate_mock_seats(booked_codes=None):
    if booked_codes is None:
        booked_codes = set()
    seats = []
    for r in ["A", "B", "C", "D", "E", "F"]:
        for num in range(1, 11):
            code = f"{r}{num}"
            status = "booked" if code in booked_codes else "available"
            price = 200 if r in ["A", "B"] else (260 if r in ["C", "D"] else 350)
            seats.append(Seat(
                id=f"S001-{code}",
                show_id="S001",
                row=r,
                number=num,
                seat_code=code,
                type="Standard" if r in ["A", "B"] else ("Premium" if r in ["C", "D"] else "Recliner"),
                status=status,
                price=price
            ))
    return seats

def test_1_best_seat_for_one():
    seats = generate_mock_seats()
    res = recommend_seats_for_show(seats, group_size=1, preference="best_view")
    assert len(res["recommended_seats"]) == 1
    # Optimal single seat should be centered in Row C or D (e.g. C4, C5, C6, D5)
    assert res["recommended_seats"][0] in ["C4", "C5", "C6", "C7", "D4", "D5", "D6", "D7"]

def test_2_best_seats_for_two():
    seats = generate_mock_seats()
    res = recommend_seats_for_show(seats, group_size=2, preference="best_view")
    assert len(res["recommended_seats"]) == 2
    # Should be centered adjacent seats in Row C or D
    assert res["recommended_seats"] in [["C5", "C6"], ["D5", "D6"], ["C4", "C5"], ["D4", "D5"]]

def test_3_best_seats_for_four():
    seats = generate_mock_seats()
    res = recommend_seats_for_show(seats, group_size=4, preference="best_view")
    assert len(res["recommended_seats"]) == 4
    # All 4 seats must be contiguous in the same row
    codes = res["recommended_seats"]
    row = codes[0][0]
    nums = [int(c[1:]) for c in codes]
    assert all(c[0] == row for c in codes)
    assert nums == list(range(nums[0], nums[0] + 4))

def test_4_adjacent_seats_preference():
    seats = generate_mock_seats()
    res = recommend_seats_for_show(seats, group_size=3, preference="together")
    assert len(res["recommended_seats"]) == 3
    codes = res["recommended_seats"]
    nums = [int(c[1:]) for c in codes]
    assert nums == list(range(nums[0], nums[0] + 3))

def test_5_center_seats():
    seats = generate_mock_seats()
    res = recommend_seats_for_show(seats, group_size=2, preference="center")
    codes = res["recommended_seats"]
    assert any(c in ["C5", "C6", "D5", "D6"] for c in codes)

def test_6_aisle_preference():
    seats = generate_mock_seats()
    res = recommend_seats_for_show(seats, group_size=2, preference="aisle")
    # Aisle preference should select window containing seat 1 or 10
    codes = res["recommended_seats"]
    nums = [int(c[1:]) for c in codes]
    assert 1 in nums or 10 in nums

def test_7_cheapest_seats():
    seats = generate_mock_seats()
    res = recommend_seats_for_show(seats, group_size=2, preference="cheapest")
    # Should select Row A or B (price 200)
    row = res["recommended_seats"][0][0]
    assert row in ["A", "B"]
    assert res["total_price"] == 400

def test_8_sold_out_show():
    all_booked = {f"{r}{n}" for r in ["A", "B", "C", "D", "E", "F"] for n in range(1, 11)}
    seats = generate_mock_seats(booked_codes=all_booked)
    res = recommend_seats_for_show(seats, group_size=2)
    assert len(res["recommended_seats"]) == 0
    assert res["score"] == 0.0

def test_9_not_enough_adjacent_seats_fallback():
    # Book alternating seats in every row so no contiguous block of 3 exists
    booked = {f"{r}{n}" for r in ["A", "B", "C", "D", "E", "F"] for n in [1, 3, 5, 7, 9]}
    seats = generate_mock_seats(booked_codes=booked)
    res = recommend_seats_for_show(seats, group_size=3)
    # Should fall back to closest 3 available seats
    assert len(res["recommended_seats"]) == 3

def test_10_partial_availability():
    # Only Row F has 2 contiguous available seats left
    booked = {f"{r}{n}" for r in ["A", "B", "C", "D", "E"] for n in range(1, 11)}
    seats = generate_mock_seats(booked_codes=booked)
    res = recommend_seats_for_show(seats, group_size=2)
    assert len(res["recommended_seats"]) == 2
    assert all(c.startswith("F") for c in res["recommended_seats"])
