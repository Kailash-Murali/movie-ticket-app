from typing import List, Dict, Any, Optional
from app.models.show import Show
from app.schemas.intent import UserIntent

def score_show(show: Show, intent: UserIntent, group_size: int = 1) -> Dict[str, Any]:
    score = 50.0
    reasons = []

    # 1. Time proximity score (up to 25 points)
    if intent.min_time or intent.max_time:
        show_mins = int(show.time.split(":")[0]) * 60 + int(show.time.split(":")[1])
        time_valid = True

        if intent.min_time:
            req_min_mins = int(intent.min_time.split(":")[0]) * 60 + int(intent.min_time.split(":")[1])
            if show_mins < req_min_mins:
                time_valid = False
                score -= 30.0
                reasons.append(f"Showtime {show.time} is earlier than requested {intent.min_time}")

        if intent.max_time:
            req_max_mins = int(intent.max_time.split(":")[0]) * 60 + int(intent.max_time.split(":")[1])
            if show_mins > req_max_mins:
                time_valid = False
                score -= 30.0
                reasons.append(f"Showtime {show.time} is later than requested limit {intent.max_time}")

        if time_valid:
            score += 25.0
            reasons.append(f"Showtime ({show.time}) fits your time window")
    else:
        score += 15.0

    # 2. Budget score (up to 20 points)
    if intent.max_price:
        if show.price <= intent.max_price:
            savings = intent.max_price - show.price
            score += 20.0
            reasons.append(f"Ticket price (₹{show.price}) is within your budget (₹{intent.max_price})")
        else:
            overage = show.price - intent.max_price
            penalty = min(30.0, overage * 0.2)
            score -= penalty
            reasons.append(f"Ticket price (₹{show.price}) exceeds budget (₹{intent.max_price})")
    else:
        score += 10.0

    # 3. Format score (up to 15 points)
    if intent.format:
        if intent.format.lower() in show.format.lower():
            score += 15.0
            reasons.append(f"Matches preferred format ({show.format})")
    else:
        score += 5.0

    # 4. Theater distance score (up to 15 points)
    if show.theater and hasattr(show.theater, 'distance_km'):
        dist = show.theater.distance_km
        if dist <= 4.0:
            score += 15.0
            reasons.append(f"Nearby theater location ({dist} km away)")
        elif dist <= 8.0:
            score += 10.0
            reasons.append(f"Accessible theater distance ({dist} km away)")
        else:
            score += 5.0

    # 5. Seat availability score (up to 15 points)
    available_count = sum(1 for s in show.seats if s.status == "available") if show.seats else 60
    if available_count >= group_size:
        score += 15.0
        reasons.append(f"{available_count} seats available")
    else:
        score -= 40.0
        reasons.append(f"Insufficient seats (only {available_count} left)")

    final_score = round(max(0.0, min(100.0, score)), 1)
    return {
        "show": show,
        "score": final_score,
        "reasons": reasons
    }

def rank_shows(shows: List[Show], intent: UserIntent, group_size: int = 1) -> Dict[str, Any]:
    if not shows:
        return {
            "recommended_show": None,
            "alternatives": []
        }

    scored = [score_show(s, intent, group_size) for s in shows]
    scored.sort(key=lambda x: x["score"], reverse=True)

    recommended = scored[0]
    alternatives = scored[1:4]

    return {
        "recommended_show": recommended,
        "alternatives": alternatives
    }
