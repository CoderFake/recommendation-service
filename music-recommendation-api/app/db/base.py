# Import all the models, so that Base has them before being
# imported by Alembic

from app.db.base_class import Base
from app.models.user import User
from app.models.song import Song
from app.models.interaction import Interaction
from app.models.playlist import Playlist
from app.models.playlist_song import PlaylistSong