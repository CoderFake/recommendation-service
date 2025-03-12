"""Initial migration with Spotify support

Revision ID: 0001
Revises:
Create Date: 2025-03-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('firebase_uid', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('avatar_url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('firebase_uid'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_firebase_uid'), 'user', ['firebase_uid'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)

    # Create song table with spotify_id instead of soundcloud_id
    op.create_table(
        'song',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spotify_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('artist', sa.String(), nullable=False),
        sa.Column('artwork_url', sa.String(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('genre', sa.String(), nullable=True),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('spotify_id')
    )
    op.create_index(op.f('ix_song_artist'), 'song', ['artist'], unique=False)
    op.create_index(op.f('ix_song_genre'), 'song', ['genre'], unique=False)
    op.create_index(op.f('ix_song_id'), 'song', ['id'], unique=False)
    op.create_index(op.f('ix_song_spotify_id'), 'song', ['spotify_id'], unique=True)
    op.create_index(op.f('ix_song_title'), 'song', ['title'], unique=False)

    # Create playlist table
    op.create_table(
        'playlist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('song_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playlist_id'), 'playlist', ['id'], unique=False)

    # Create interaction table
    op.create_table(
        'interaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('song_id', sa.Integer(), nullable=False),
        sa.Column('listen_count', sa.Integer(), nullable=False),
        sa.Column('like_score', sa.Float(), nullable=False),
        sa.Column('saved', sa.Boolean(), nullable=False),
        sa.Column('context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['song_id'], ['song.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interaction_id'), 'interaction', ['id'], unique=False)
    op.create_index(op.f('ix_interaction_timestamp'), 'interaction', ['timestamp'], unique=False)

    # Create playlist_song table (using underscore in the name)
    op.create_table(
        'playlist_song',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('playlist_id', sa.Integer(), nullable=False),
        sa.Column('song_id', sa.Integer(), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['playlist_id'], ['playlist.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['song_id'], ['song.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playlist_song_id'), 'playlist_song', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_playlist_song_id'), table_name='playlist_song')
    op.drop_table('playlist_song')
    op.drop_index(op.f('ix_interaction_timestamp'), table_name='interaction')
    op.drop_index(op.f('ix_interaction_id'), table_name='interaction')
    op.drop_table('interaction')
    op.drop_index(op.f('ix_playlist_id'), table_name='playlist')
    op.drop_table('playlist')
    op.drop_index(op.f('ix_song_title'), table_name='song')
    op.drop_index(op.f('ix_song_spotify_id'), table_name='song')
    op.drop_index(op.f('ix_song_id'), table_name='song')
    op.drop_index(op.f('ix_song_genre'), table_name='song')
    op.drop_index(op.f('ix_song_artist'), table_name='song')
    op.drop_table('song')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_firebase_uid'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')