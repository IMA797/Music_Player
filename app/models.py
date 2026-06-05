from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import *


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    # unique=True значит что в таблице в данной строке н может быть одинаковых значений
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    # Optional - данный столбец может быть пустым или обнуляемым
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    
    role: so.Mapped[str] = so.mapped_column(sa.String(10), index=True, default='user')
    tracks: so.WriteOnlyMapped['Track'] = so.relationship(back_populates='user')
    playlists: so.WriteOnlyMapped['PlayList'] = so.relationship(back_populates='user')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class PendingUser(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    verification_code: so.Mapped[int] = so.mapped_column(index=True)
    code_expires_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Track(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    artist: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    filename: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), index=True)
    uploaded_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    status: so.Mapped[str] = so.mapped_column(sa.String(20), index=True, default='pending')
    
    user: so.Mapped['User'] = so.relationship(back_populates='tracks')
    playlists: so.WriteOnlyMapped['PlayList'] = so.relationship(secondary='playlist_track', back_populates='tracks')

class PlayList(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    user: so.Mapped['User'] = so.relationship(back_populates='playlists')
    tracks: so.WriteOnlyMapped['Track'] = so.relationship(secondary='playlist_track', back_populates='playlists')

class PlaylistTrack(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    playlist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('play_list.id'), index=True)
    track_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('track.id'), index=True)
