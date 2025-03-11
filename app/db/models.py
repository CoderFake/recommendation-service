from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class InteractionType(enum.Enum):
    """Kiểu tương tác của người dùng"""
    PLAY = "play"
    LIKE = "like"
    FOLLOW_ARTIST = "follow_artist"
    COMMENT = "comment"
    SHARE = "share"
    SKIP = "skip"
    ADD_TO_PLAYLIST = "add_to_playlist"


class DeviceType(enum.Enum):
    """Loại thiết bị người dùng sử dụng"""
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    SPEAKER = "speaker"
    TV = "tv"
    OTHER = "other"


class TimeContext(enum.Enum):
    """Ngữ cảnh thời gian"""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class Song(Base):
    """Model bài hát (đồng bộ từ music_service)"""
    __tablename__ = "songs"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # Thời lượng bài hát (giây)
    storage_id = Column(String(255), nullable=True)
    storage_type = Column(String(50), nullable=True)
    artist_id = Column(String(36), nullable=False)
    album_id = Column(String(36), nullable=True)
    genre_id = Column(String(36), nullable=True)
    release_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Đặc điểm âm thanh (audio features)
    tempo = Column(Float, nullable=True)  # Nhịp độ bài hát (BPM)
    danceability = Column(Float, nullable=True)  # Độ phù hợp để nhảy (0-1)
    energy = Column(Float, nullable=True)  # Độ năng lượng (0-1)
    valence = Column(Float, nullable=True)  # Độ tích cực (0-1)
    acousticness = Column(Float, nullable=True)  # Độ âm thanh acoustic (0-1)
    instrumentalness = Column(Float, nullable=True)  # Độ nhạc cụ (0-1)
    liveness = Column(Float, nullable=True)  # Độ live (0-1)
    key = Column(String(5), nullable=True)  # Tông của bài hát
    mode = Column(String(10), nullable=True)  # Thể thức (major/minor)

    # Relationships
    interactions = relationship("UserInteraction", back_populates="song")
    features = relationship("SongFeature", back_populates="song")

    # Indices
    __table_args__ = (
        Index('idx_song_artist', 'artist_id'),
        Index('idx_song_album', 'album_id'),
        Index('idx_song_genre', 'genre_id'),
        Index('idx_song_release_year', 'release_year'),
    )


class User(Base):
    """Model người dùng (đồng bộ từ user_service)"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=True)
    gender = Column(String(10), nullable=True)
    dob = Column(DateTime, nullable=True)
    country_iso2 = Column(String(2), nullable=True)
    language = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("UserInteraction", back_populates="user")
    genre_preferences = relationship("UserGenrePreference", back_populates="user")
    artist_preferences = relationship("UserArtistPreference", back_populates="user")

    # Indices
    __table_args__ = (
        Index('idx_user_country', 'country_iso2'),
        Index('idx_user_language', 'language'),
    )


class Artist(Base):
    """Model nghệ sĩ (đồng bộ từ music_service)"""
    __tablename__ = "artists"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    genre_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    songs = relationship("Song", primaryjoin="Artist.id==Song.artist_id", viewonly=True)
    user_preferences = relationship("UserArtistPreference", back_populates="artist")

    # Indices
    __table_args__ = (
        Index('idx_artist_genre', 'genre_id'),
    )


class Genre(Base):
    """Model thể loại nhạc (đồng bộ từ music_service)"""
    __tablename__ = "genres"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    key = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    songs = relationship("Song", primaryjoin="Genre.id==Song.genre_id", viewonly=True)
    artists = relationship("Artist", primaryjoin="Genre.id==Artist.genre_id", viewonly=True)
    user_preferences = relationship("UserGenrePreference", back_populates="genre")


class Album(Base):
    """Model album (đồng bộ từ music_service)"""
    __tablename__ = "albums"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    artist_id = Column(String(36), ForeignKey("artists.id"))
    release_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    artist = relationship("Artist")
    songs = relationship("Song", primaryjoin="Album.id==Song.album_id", viewonly=True)

    # Indices
    __table_args__ = (
        Index('idx_album_artist', 'artist_id'),
        Index('idx_album_release_year', 'release_year'),
    )


class UserInteraction(Base):
    """Model tương tác người dùng với bài hát"""
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    song_id = Column(String(36), ForeignKey("songs.id"), nullable=False)
    interaction_type = Column(Enum(InteractionType), nullable=False)
    play_count = Column(Integer, default=0)  # Số lần phát
    play_duration = Column(Integer, default=0)  # Thời gian phát (giây)
    liked = Column(Boolean, default=False)  # Đã thích chưa
    device_type = Column(Enum(DeviceType), nullable=True)  # Loại thiết bị
    time_context = Column(Enum(TimeContext), nullable=True)  # Ngữ cảnh thời gian
    location = Column(String(100), nullable=True)  # Vị trí (nếu có)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="interactions")
    song = relationship("Song", back_populates="interactions")

    # Indices
    __table_args__ = (
        Index('idx_interaction_user_song', 'user_id', 'song_id'),
        Index('idx_interaction_time', 'created_at'),
        Index('idx_interaction_type', 'interaction_type'),
        Index('idx_interaction_time_context', 'time_context'),
    )


class UserGenrePreference(Base):
    """Model sở thích thể loại của người dùng"""
    __tablename__ = "user_genre_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    genre_id = Column(String(36), ForeignKey("genres.id"), nullable=False)
    score = Column(Float, default=0.0)  # Điểm số sở thích (0-1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="genre_preferences")
    genre = relationship("Genre", back_populates="user_preferences")

    # Indices
    __table_args__ = (
        Index('idx_genre_pref_user', 'user_id'),
        Index('idx_genre_pref_score', 'score'),
    )


class UserArtistPreference(Base):
    """Model sở thích nghệ sĩ của người dùng"""
    __tablename__ = "user_artist_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    artist_id = Column(String(36), ForeignKey("artists.id"), nullable=False)
    score = Column(Float, default=0.0)  # Điểm số sở thích (0-1)
    follows = Column(Boolean, default=False)  # Người dùng có follow nghệ sĩ không
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="artist_preferences")
    artist = relationship("Artist", back_populates="user_preferences")

    # Indices
    __table_args__ = (
        Index('idx_artist_pref_user', 'user_id'),
        Index('idx_artist_pref_score', 'score'),
    )


class SongFeature(Base):
    """Model đặc trưng bổ sung của bài hát"""
    __tablename__ = "song_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    song_id = Column(String(36), ForeignKey("songs.id"), nullable=False)
    feature_name = Column(String(50), nullable=False)  # Tên đặc trưng
    feature_value = Column(Float, nullable=False)  # Giá trị đặc trưng
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    song = relationship("Song", back_populates="features")

    # Indices
    __table_args__ = (
        Index('idx_feature_song_name', 'song_id', 'feature_name'),
    )


class RecommendationRequest(Base):
    """Model lưu trữ các yêu cầu gợi ý"""
    __tablename__ = "recommendation_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    song_id = Column(String(36), ForeignKey("songs.id"), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=True)
    time_context = Column(Enum(TimeContext), nullable=True)
    request_json = Column(Text, nullable=True)  # Lưu JSON đầy đủ của request
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indices
    __table_args__ = (
        Index('idx_request_user', 'user_id'),
        Index('idx_request_song', 'song_id'),
        Index('idx_request_time', 'created_at'),
    )


class RecommendationResult(Base):
    """Model lưu trữ kết quả gợi ý"""
    __tablename__ = "recommendation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("recommendation_requests.id"), nullable=False)
    song_id = Column(String(36), ForeignKey("songs.id"), nullable=False)
    score = Column(Float, nullable=False)  # Điểm số gợi ý
    algorithm_type = Column(String(50), nullable=False)  # Loại thuật toán gợi ý
    rank_position = Column(Integer, nullable=False)  # Vị trí trong kết quả gợi ý
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indices
    __table_args__ = (
        Index('idx_result_request', 'request_id'),
        Index('idx_result_song', 'song_id'),
        Index('idx_result_algorithm', 'algorithm_type'),
    )