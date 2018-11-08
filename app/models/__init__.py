from datetime import datetime
from decimal import Decimal
import time

from flask import current_app, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy import and_
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.constants import (
    COMMISSION_RATE, DEFAULT_TOKEN_COUNT, NESTED_VALUES_LIMIT,
    PAYMENT_CATEGORIES, TOKEN_EQUIVALENT_OF_USD, TOLL_FREE_DAILY_REQUESTS)
from app.constants.statuses import (
    ACTIVE_STATUS_ID, DELETED_STATUS_ID, DISABLED_STATUS_ID)
from app.models.mixins import HasStatus, HasToken, LookUp, Persistence
from utils import generate_unique_reference
from utils.contexts import (
    get_current_api_ref, get_current_request_data, get_current_request_headers)


EMPTY_AMOUNT = '0.00'
AMOUNT_FIELD = db.DECIMAL(12, 6)
GEO_LOCATION_FIELD = db.Float(6, 6)
APP_OWNERSHIP_OPTIONS = ('Proprietary', 'Third Party')
THIRD_PARTY_APP_OWNERSHIP = 'Third Party'


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


class APILog(BaseModel):
    __tablename__ = 'api_logs'

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


class App(BaseModel):
    __tablename__ = 'apps'

    api_key = db.Column(db.String(64), default=generate_unique_reference)
    description = db.Column(db.String(128))
    image = db.Column(db.TEXT)
    meta = db.Column(db.TEXT, default="{}")
    name = db.Column(db.String(64))
    privacy_policy_url = db.Column(db.TEXT)
    ownership = db.Column(
        db.Enum(*APP_OWNERSHIP_OPTIONS, name='app_ownership'),
        default=THIRD_PARTY_APP_OWNERSHIP)
    url = db.Column(db.String(128))
    webhook_url = db.Column(db.String(128))

    app_category_id = db.Column(db.Integer, db.ForeignKey('app_categories.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    app_category = db.relationship(
        'AppCategory', backref=db.backref('carts', uselist=True), uselist=False)
    user = db.relationship(
        'User', backref=db.backref('apps', uselist=True),
        foreign_keys=[user_id], uselist=False)

    def as_json(self, keys_to_exclude=None):
        result = {
            'created_at': self.created_at.isoformat(),
            'api_key': self.api_key,
            'app_category': self.app_category.as_json(),
            'description': self.description,
            'name': self.name,
            'ownership': self.ownership,
            'privacy_policy_url': self.privacy_policy_url,
            'url': self.url,
            'webhook_url': self.webhook_url,
            'image': self.image
        }

        return result


class AppCategory(BaseModel, LookUp):
    __tablename__ = 'app_categories'

    name = db.Column(db.String(16))
    description = db.Column(db.String(128))

    def as_json(self):
        return {
            'created_at': self.created_at.isoformat(),
            'name': self.name,
            'description': self.description
        }


class Like(BaseModel):
    __tablename__ = 'likes'


class Message(BaseModel):
    __tablename__ = 'messages'

    text = db.Column(db.TEXT)


class MessageAttachment(BaseModel):
    __tablename__ = 'message_attachments'

    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    blob_id = db.Column(db.Integer, db.ForeignKey('blobs.id'))


class Post(BaseModel):
    __tablename__ = 'posts'

    body = db.Column(db.TEXT)

    photo_id = db.Column(db.Integer, db.ForeignKey('blobs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('blobs.id'))


class Comment(BaseModel):
    __tablename__ = 'comments'


class Status(BaseModel, LookUp):
    __tablename__ = 'statuses'

    def __str__(self):
        return self.name


class User(BaseModel, HasToken):
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
    tokens = db.Column(AMOUNT_FIELD, default=DEFAULT_TOKEN_COUNT)

    created_by = db.Column(db.Integer, db.ForeignKey('apps.id'))
    profile_photo = db.relationship('Blob', uselist=True)

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

    def record_request_cost(self, cost):
        self.tokens -= cost
        self.save()

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=None):
        expiration = expiration or current_app.config['TOKEN_LIFESPAN']

        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)

        expires_on = datetime.fromtimestamp(time.time() + expiration)

        return s.dumps({'id': self.id}).decode('utf-8'), expires_on
