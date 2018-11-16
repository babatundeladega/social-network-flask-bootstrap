from flask import current_app
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.exc import SQLAlchemyError

from app import db, errors, logger
from app.constants import statuses


def _commit_to_db():
    try:
        db.session.commit()
    except SQLAlchemyError:
        logger.error('Error persisting to DB', exc_info=True)
        db.session.rollback()
        raise


class HasLocation(object):
    @declared_attr
    def location_id(self):
        return db.Column(
            db.Integer, db.ForeignKey('locations.id'),
            default=statuses.ACTIVE_STATUS_ID)

    @declared_attr
    def location(self):
        return db.relationship(
            'Location', lazy=True, foreign_keys=[self.location_id])


class HasStatus(object):
    @declared_attr
    def status_id(self):
        return db.Column(
            db.Integer, db.ForeignKey('statuses.id'),
            default=statuses.ACTIVE_STATUS_ID)

    @declared_attr
    def status(self):
        return db.relationship(
            'Status', lazy=True, foreign_keys=[self.status_id])

    def is_active(self):
        return self.status_id == statuses.ACTIVE_STATUS_ID

    def is_deleted(self):
        return self.status_id == statuses.DELETED_STATUS_ID


class HasToken(object):
    @classmethod
    def verify_auth_token(cls, token):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except SignatureExpired:
            raise errors.TokenExpired
        except BadSignature:
            raise errors.InvalidAuthToken

        return getattr(cls, 'query').get_not_deleted(data['id'])


class LookUp(object):
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(128))

    def as_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Persistence(object):

    def save(self, _commit=True):
        db.session.add(self)
        if _commit:
            _commit_to_db()

    def delete(self, _commit=True):
        setattr(self, 'status_id', statuses.DELETED_STATUS_ID)

        db.session.delete(self)

        if _commit:
            _commit_to_db()
            # TODO: Implement job to mop up deleted records

    def update(self, _commit=True, **kwargs):

        for k, v in kwargs.items():
            setattr(self, k, v)
        if _commit:
            _commit_to_db()
