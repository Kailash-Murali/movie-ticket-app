"""Streamlit frontend for the AI Movie Booking Assistant."""

import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="🎬 AI Movie Booking Assistant",
    page_icon="🎬",
    layout="wide",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%); }

    .hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    .rec-card {
        background: linear-gradient(145deg, #1e293b, #1a1a2e);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .rec-card:hover { transform: translateY(-2px); }
    .rec-card.best {
        border: 2px solid #6bcb77;
        box-shadow: 0 0 20px rgba(107, 203, 119, 0.2);
    }

    .movie-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.3rem;
    }

    .movie-meta {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .score-bar {
        background: #1e293b;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        margin: 0.2rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .constraint-tag {
        display: inline-block;
        background: #7f1d1d;
        color: #fca5a5;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.15rem;
    }

    .pref-tag {
        display: inline-block;
        background: #1e3a5f;
        color: #93c5fd;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.15rem;
    }

    .seat-available {
        background: #1e293b;
        border: 2px solid #475569;
        color: #94a3b8;
        width: 42px; height: 42px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 3px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .seat-booked {
        background: #7f1d1d;
        border: 2px solid #991b1b;
        color: #fca5a5;
        width: 42px; height: 42px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 3px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .seat-recommended {
        background: #14532d;
        border: 2px solid #22c55e;
        color: #86efac;
        width: 42px; height: 42px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 3px;
        font-size: 0.75rem;
        font-weight: 700;
        box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
    }

    .screen-label {
        text-align: center;
        color: #475569;
        font-size: 0.85rem;
        letter-spacing: 8px;
        padding: 0.5rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid #334155;
        border-radius: 0 0 40% 40%;
    }

    .booking-success {
        background: linear-gradient(145deg, #14532d, #1a3a1a);
        border: 2px solid #22c55e;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
    }

    .ticket {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 2px dashed #6366f1;
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1rem;
        position: relative;
    }
    .ticket::before {
        content: '🎫';
        font-size: 2rem;
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────
st.markdown('<div class="hero-title">🎬 AI Movie Booking Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Constraint-aware group consensus for the perfect movie night</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────
if "stage" not in st.session_state:
    st.session_state.stage = "input"  # input → results → seats → booked
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "parsed_prefs" not in st.session_state:
    st.session_state.parsed_prefs = []
if "selected_show" not in st.session_state:
    st.session_state.selected_show = None
if "booking" not in st.session_state:
    st.session_state.booking = None
if "num_members" not in st.session_state:
    st.session_state.num_members = 3


# ──────────────────────────────────────────────
# STAGE: Input
# ──────────────────────────────────────────────
if st.session_state.stage == "input":
    st.markdown("### 👥 Group Member Preferences")
    st.markdown("Enter what each person wants in natural language.")

    num = st.slider("Number of group members", 2, 6, st.session_state.num_members)
    st.session_state.num_members = num

    members = []
    default_examples = [
        "I want a Hindi comedy after 7 PM, preferably something fun",
        "No horror movies please, and keep it under ₹500",
        "I'd like good seats together, preferably a short movie",
        "Must be Hindi, prefer action or comedy",
        "Something highly rated, prefer evening show",
        "Family friendly movie, not too expensive",
    ]

    for i in range(num):
        default = default_examples[i] if i < len(default_examples) else ""
        text = st.text_area(
            f"Person {i+1}",
            value=default,
            height=80,
            key=f"member_{i}",
        )
        members.append(text)

    col1, col2 = st.columns([1, 4])
    with col1:
        analyze = st.button("🔍 Analyze Group", type="primary", use_container_width=True)

    if analyze:
        non_empty = [m.strip() for m in members if m.strip()]
        if len(non_empty) < 2:
            st.error("Please enter preferences for at least 2 group members.")
        else:
            with st.spinner("🤖 Analyzing preferences with AI..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/recommend",
                        json={"members": non_empty},
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.parsed_prefs = data["parsed_preferences"]
                        st.session_state.recommendations = data["recommendations"]
                        st.session_state.num_members = len(non_empty)
                        st.session_state.stage = "results"
                        st.rerun()
                    else:
                        error_detail = resp.json().get("detail", "Unknown error")
                        st.error(f"❌ Backend error: {error_detail}")
                except requests.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure FastAPI is running on port 8000.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")


# ──────────────────────────────────────────────
# STAGE: Results
# ──────────────────────────────────────────────
elif st.session_state.stage == "results":
    # Show parsed preferences
    st.markdown("### 🧠 Extracted Preferences")

    prefs = st.session_state.parsed_prefs
    cols = st.columns(min(len(prefs), 3))

    for i, pref in enumerate(prefs):
        with cols[i % len(cols)]:
            st.markdown(f"**Person {i+1}**")

            # Hard constraints
            if pref.get("hard_constraints"):
                st.markdown("**Hard Constraints:**")
                tags = "".join(
                    f'<span class="constraint-tag">🚫 {c}</span>'
                    for c in pref["hard_constraints"]
                )
                st.markdown(tags, unsafe_allow_html=True)

            # Soft preferences
            if pref.get("soft_preferences"):
                st.markdown("**Soft Preferences:**")
                tags = "".join(
                    f'<span class="pref-tag">💡 {p}</span>'
                    for p in pref["soft_preferences"]
                )
                st.markdown(tags, unsafe_allow_html=True)

            st.markdown("---")

    # Recommendations
    st.markdown("### 🎯 Top Recommendations")

    recs = st.session_state.recommendations

    if not recs:
        st.warning("⚠️ No shows satisfy all group members' hard constraints. Try relaxing some constraints.")
        if st.button("← Back to Input"):
            st.session_state.stage = "input"
            st.rerun()
    else:
        for idx, rec in enumerate(recs):
            is_best = idx == 0
            card_class = "rec-card best" if is_best else "rec-card"
            badge = "🏆 BEST GROUP MATCH" if is_best else f"#{idx+1}"

            st.markdown(f"""
            <div class="{card_class}">
                <div style="color: {'#6bcb77' if is_best else '#94a3b8'}; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.5rem;">
                    {badge}
                </div>
                <div class="movie-title">{rec['movie_title']}</div>
                <div class="movie-meta">
                    🕐 {rec['time']} &nbsp;|&nbsp; 🏢 {rec['cinema']} &nbsp;|&nbsp; 💰 ₹{rec['price']}/person
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Individual scores
            score_cols = st.columns(len(rec["individual_scores"]) + 2)

            for j, score in enumerate(rec["individual_scores"]):
                with score_cols[j]:
                    pct = int(score * 100)
                    color = "#22c55e" if pct >= 80 else "#eab308" if pct >= 60 else "#ef4444"
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div style="font-size: 0.8rem; color: #94a3b8;">Person {j+1}</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: {color};">{pct}%</div>
                    </div>
                    """, unsafe_allow_html=True)

            with score_cols[-2]:
                min_pct = int(rec["minimum_score"] * 100)
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">Min Score</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #f59e0b;">{min_pct}%</div>
                </div>
                """, unsafe_allow_html=True)

            with score_cols[-1]:
                avg_pct = int(rec["average_score"] * 100)
                st.markdown(f"""
                <div style="text-align: center;">
                    <div style="font-size: 0.8rem; color: #94a3b8;">Avg Score</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: #3b82f6;">{avg_pct}%</div>
                </div>
                """, unsafe_allow_html=True)

            # Reasons
            with st.expander(f"📋 Why this option?", expanded=is_best):
                for reason in rec["reasons"]:
                    st.markdown(f"- {reason}")

            st.markdown("---")

        # Show selection
        st.markdown("### 🎬 Select a Show")
        options = {
            f"{rec['movie_title']} — {rec['time']} at {rec['cinema']} (₹{rec['price']}/person)": rec
            for rec in recs
        }
        choice = st.selectbox("Choose your show:", list(options.keys()))

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🪑 Select Seats", type="primary", use_container_width=True):
                st.session_state.selected_show = options[choice]
                st.session_state.stage = "seats"
                st.rerun()
        with col2:
            if st.button("← Back to Input"):
                st.session_state.stage = "input"
                st.rerun()


# ──────────────────────────────────────────────
# STAGE: Seats
# ──────────────────────────────────────────────
elif st.session_state.stage == "seats":
    show_info = st.session_state.selected_show
    show_id = show_info["show_id"]
    group_size = st.session_state.num_members

    st.markdown(f"### 🪑 Seat Selection — {show_info['movie_title']}")
    st.markdown(f"🕐 {show_info['time']} | 🏢 {show_info['cinema']} | 💰 ₹{show_info['price']}/person")

    # Fetch seats
    try:
        resp = requests.get(
            f"{API_URL}/shows/{show_id}/seats",
            params={"group_size": group_size},
            timeout=10,
        )
        if resp.status_code != 200:
            st.error("Failed to load seats.")
            st.stop()
        seat_data = resp.json()
    except requests.ConnectionError:
        st.error("❌ Cannot connect to backend.")
        st.stop()

    seats = seat_data["seats"]
    rec_block = seat_data.get("recommended_block")
    rec_seat_ids = set(rec_block["seats"]) if rec_block else set()

    # Screen label
    st.markdown('<div class="screen-label">S C R E E N</div>', unsafe_allow_html=True)

    # Group by row
    rows: dict[str, list] = {}
    for s in seats:
        rows.setdefault(s["row"], []).append(s)

    for row_label in sorted(rows.keys()):
        row_seats = sorted(rows[row_label], key=lambda s: s["number"])
        seat_html = f'<div style="display: flex; align-items: center; margin-bottom: 2px;"><span style="color: #64748b; width: 25px; font-weight: 700;">{row_label}</span>'

        for s in row_seats:
            if s["id"] in rec_seat_ids:
                css_class = "seat-recommended"
            elif s["status"] == "booked":
                css_class = "seat-booked"
            else:
                css_class = "seat-available"
            seat_html += f'<span class="{css_class}">{s["id"]}</span>'

        seat_html += "</div>"
        st.markdown(seat_html, unsafe_allow_html=True)

    # Legend
    st.markdown("""
    <div style="display: flex; gap: 1.5rem; margin-top: 1rem; justify-content: center;">
        <span><span class="seat-available" style="display: inline-flex; width: 16px; height: 16px; font-size: 0px;"></span> Available</span>
        <span><span class="seat-booked" style="display: inline-flex; width: 16px; height: 16px; font-size: 0px;"></span> Booked</span>
        <span><span class="seat-recommended" style="display: inline-flex; width: 16px; height: 16px; font-size: 0px;"></span> Recommended</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if rec_block:
        st.success(f"✅ Recommended seats: **{', '.join(rec_block['seats'])}** (Score: {rec_block['score']:.2f})")
        total = show_info["price"] * group_size
        st.info(f"💰 Total price: ₹{total} for {group_size} seats")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("✅ Confirm Booking", type="primary", use_container_width=True):
                with st.spinner("Processing booking..."):
                    try:
                        book_resp = requests.post(
                            f"{API_URL}/book",
                            json={
                                "show_id": show_id,
                                "seats": rec_block["seats"],
                            },
                            timeout=10,
                        )
                        if book_resp.status_code == 200:
                            st.session_state.booking = book_resp.json()
                            st.session_state.stage = "booked"
                            st.rerun()
                        else:
                            error = book_resp.json().get("detail", "Booking failed")
                            st.error(f"❌ {error}")
                    except Exception as e:
                        st.error(f"❌ Booking error: {e}")
        with col2:
            if st.button("← Back to Recommendations"):
                st.session_state.stage = "results"
                st.rerun()
    else:
        st.warning("⚠️ No contiguous seats available for your group size. Try a different show.")
        if st.button("← Back to Recommendations"):
            st.session_state.stage = "results"
            st.rerun()


# ──────────────────────────────────────────────
# STAGE: Booked
# ──────────────────────────────────────────────
elif st.session_state.stage == "booked":
    booking = st.session_state.booking
    show_info = st.session_state.selected_show

    st.markdown("""
    <div class="booking-success">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎉</div>
        <div style="font-size: 1.8rem; font-weight: 800; color: #86efac;">Booking Confirmed!</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ticket">
        <div style="text-align: center; margin-top: 0.5rem;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #e2e8f0;">{show_info['movie_title']}</div>
            <div style="color: #94a3b8; margin-top: 0.5rem;">
                🕐 {show_info['time']} &nbsp;|&nbsp; 🏢 {show_info['cinema']}
            </div>
            <div style="margin-top: 1rem; display: flex; justify-content: space-around;">
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Booking ID</div>
                    <div style="color: #a78bfa; font-size: 1.2rem; font-weight: 700;">{booking['booking_id']}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Seats</div>
                    <div style="color: #6bcb77; font-size: 1.2rem; font-weight: 700;">{', '.join(booking['seats'])}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Total</div>
                    <div style="color: #fbbf24; font-size: 1.2rem; font-weight: 700;">₹{booking['total_price']}</div>
                </div>
                <div>
                    <div style="color: #64748b; font-size: 0.8rem;">Status</div>
                    <div style="color: #22c55e; font-size: 1.2rem; font-weight: 700;">✅ {booking['status'].upper()}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("🎬 Book Another Movie", type="primary"):
        st.session_state.stage = "input"
        st.session_state.recommendations = []
        st.session_state.parsed_prefs = []
        st.session_state.selected_show = None
        st.session_state.booking = None
        st.rerun()
