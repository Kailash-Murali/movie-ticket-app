"""initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-12 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'movies',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('genre', sa.JSON(), nullable=False),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('runtime', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('mood_tags', sa.JSON(), nullable=False),
        sa.Column('age_rating', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('formats', sa.JSON(), nullable=False),
    )
    op.create_index('ix_movies_id', 'movies', ['id'])
    op.create_index('ix_movies_title', 'movies', ['title'])
    op.create_index('ix_movies_language', 'movies', ['language'])

    op.create_table(
        'theaters',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('distance_km', sa.Float(), nullable=False),
        sa.Column('formats', sa.JSON(), nullable=False),
        sa.Column('amenities', sa.JSON(), nullable=False),
    )
    op.create_index('ix_theaters_id', 'theaters', ['id'])
    op.create_index('ix_theaters_name', 'theaters', ['name'])

    op.create_table(
        'shows',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('movie_id', sa.String(), sa.ForeignKey('movies.id'), nullable=False),
        sa.Column('theater_id', sa.String(), sa.ForeignKey('theaters.id'), nullable=False),
        sa.Column('date', sa.String(), nullable=False),
        sa.Column('time', sa.String(), nullable=False),
        sa.Column('format', sa.String(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
    )
    op.create_index('ix_shows_id', 'shows', ['id'])
    op.create_index('ix_shows_movie_id', 'shows', ['movie_id'])
    op.create_index('ix_shows_theater_id', 'shows', ['theater_id'])
    op.create_index('ix_shows_date', 'shows', ['date'])
    op.create_index('ix_shows_time', 'shows', ['time'])

    op.create_table(
        'seats',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('show_id', sa.String(), sa.ForeignKey('shows.id'), nullable=False),
        sa.Column('row', sa.String(), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('seat_code', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='available'),
        sa.Column('price', sa.Integer(), nullable=False),
    )
    op.create_index('ix_seats_id', 'seats', ['id'])
    op.create_index('ix_seats_show_id', 'seats', ['show_id'])
    op.create_index('ix_seats_status', 'seats', ['status'])

    op.create_table(
        'bookings',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('show_id', sa.String(), sa.ForeignKey('shows.id'), nullable=False),
        sa.Column('user_name', sa.String(), nullable=True),
        sa.Column('total_price', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='confirmed'),
        sa.Column('seat_codes', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_bookings_id', 'bookings', ['id'])
    op.create_index('ix_bookings_show_id', 'bookings', ['show_id'])

    op.create_table(
        'booking_seats',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('booking_id', sa.String(), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('seat_id', sa.String(), sa.ForeignKey('seats.id'), nullable=False),
        sa.Column('seat_code', sa.String(), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
    )
    op.create_index('ix_booking_seats_booking_id', 'booking_seats', ['booking_id'])
    op.create_index('ix_booking_seats_seat_id', 'booking_seats', ['seat_id'])

def downgrade() -> None:
    op.drop_table('booking_seats')
    op.drop_table('bookings')
    op.drop_table('seats')
    op.drop_table('shows')
    op.drop_table('theaters')
    op.drop_table('movies')
