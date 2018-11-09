from datetime import datetime
import time

from flask import current_app, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.constants import ACCEPTED_MIME_TYPES, NESTED_VALUES_LIMIT
from app.constants.statuses import DELETED_STATUS_ID
from app.models.mixins import (
    HasLocation, HasStatus, HasToken, LookUp, Persistence)
from utils import generate_unique_reference
from utils.contexts import (
    get_current_api_ref, get_current_request_data, get_current_request_headers)


GEO_LOCATION_FIELD = db.Float(6, 6)


class BaseModel(db.Model, HasStatus, Persistence):
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    modified_at = db.Column(db.DateTime, default=datetime.utcnow)
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(64), default=generate_unique_reference)

    @classmethod
    def get(cls, **kwargs):
        return cls.query.filter(
            cls.status_id != DELETED_STATUS_ID,
        ).filter_by(
            **kwargs
        ).first()

    @classmethod
    def scalar_get(cls, required_column, _desc=True, **args):
        cls_column = getattr(cls, required_column)

        query_ = db.session.query(cls_column).filter(
            cls.status_id != DELETED_STATUS_ID
        ).filter_by(
            **args
        )

        if _desc:
            query_.order_by(cls.id.desc())

        query_.limit(NESTED_VALUES_LIMIT)

        return [record[0] for record in query_.all()]


class AccessLog(BaseModel):
    __tablename__ = 'access_logs'

    api_ref = db.Column(
        db.String(64), default=get_current_api_ref, index=True, unique=True)
    cost = db.Column(db.Integer)
    endpoint = db.Column(db.String(1024))
    request_headers = db.Column(
        db.String(2000), default=get_current_request_headers)
    request_data = db.Column(
        db.String(2000), default=get_current_request_data)
    response_data = db.Column(db.Text)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_by = db.relationship(
        'User', backref=db.backref('api_logs', uselist=True), uselist=False)


class Blob(BaseModel):
    __tablename__ = 'blobs'

    data = db.Column(db.TEXT)
    mime_type = db.Column(db.Enum(*ACCEPTED_MIME_TYPES))


class Comment(BaseModel):
    __tablename__ = 'comments'

    body = db.Column(db.TEXT)


class Like(BaseModel):
    __tablename__ = 'likes'

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    post = db.relationship(
        'Post', backref=db.backref('likes', uselist=True), uselist=False)
    user = db.relationship(
        'User', backref=db.backref('likes', uselist=True), uselist=False)


class Location(BaseModel):
    __tablename__ = 'locations'

    latitude = db.Column(db.String(10))
    longitude = db.Column(db.String(10))


class Message(BaseModel):
    __tablename__ = 'messages'

    text = db.Column(db.TEXT)


class MessageAttachment(BaseModel):
    __tablename__ = 'message_attachments'

    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    blob_id = db.Column(db.Integer, db.ForeignKey('blobs.id'))

    message = db.relationship(
        'Message', backref=db.backref('message_attachments'), uselist=False)
    blob = db.relationship(
        'Blob', backref=db.backref('message_attachments'), uselist=False)


class Post(BaseModel, HasLocation):
    __tablename__ = 'posts'

    body = db.Column(db.TEXT)

    photo_id = db.Column(db.Integer, db.ForeignKey('blobs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('blobs.id'))

    photo = db.relationship('Blob', uselist=False, foreign_keys=[photo_id])
    user = db.relationship('User', uselist=False)
    video = db.relationship('Blob', uselist=False, foreign_keys=[video_id])


class Status(BaseModel, LookUp):
    __tablename__ = 'statuses'

    def __str__(self):
        return self.name


class Story(BaseModel, HasLocation):
    __tablename__ = 'stories'

    media = db.Column(db.Integer, db.ForeignKey('blobs.id'))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', uselist=False)


class User(BaseModel, HasToken, HasLocation):
    """Users of the social network"""
    __tablename__ = 'users'

    name = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(512))
    bio = db.Column(db.String(140))
    email = db.Column(db.String(128), unique=True, index=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20), unique=True, index=True)
    phone_confirmed = db.Column(db.Boolean, default=False)
    profile_photo_id = db.Column(db.Integer, db.ForeignKey('blobs.id'))

    created_by = db.Column(db.Integer, db.ForeignKey('apps.id'))

    profile_photo = db.relationship('Blob', uselist=False)

    @property
    def _profile_photo(self):
        return Blob.query.filter_by(id=self.profile_photo_id).first()

    def as_json(self, keys_to_exclude=None):
        result = {
            'uid': self.uid,
            'name': self.name,
            'email': self.email,
            'email_confirmed': self.email_confirmed,
            'phone': self.phone,
            'phone_confirmed': self.phone_confirmed,
            'profile_photo': self.profile_photo,
            'created_at': self.created_at.isoformat(),
        }

        if isinstance(keys_to_exclude, (list, tuple, set)):
            map(lambda excluded: result.pop(excluded, None), keys_to_exclude)

        if isinstance(keys_to_exclude, str):
            result.pop(keys_to_exclude, None)

        return result

    @classmethod
    def get_for_auth(cls, **filter_args):
        user = cls.get(**filter_args)

        # Even if the authentication process outside
        # here fails, we can at least know who the "current_user" is
        g.user = user

        return user

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(
            password, method='pbkdf2:sha512')

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=None):
        expiration = expiration or current_app.config['TOKEN_LIFESPAN']

        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)

        expires_on = datetime.fromtimestamp(time.time() + expiration)

        return s.dumps({'id': self.id}).decode('utf-8'), expires_on
