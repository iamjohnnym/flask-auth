# -*- coding: utf-8 -*-
from service.api.extensions import guard, db


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update,
    delete) operations.
    """

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        try:
            instance = cls(**kwargs)
            return instance.save()
        except Exception as e:
            return e

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True


# From Mike Bayer's "Building the app" talk
# https://speakerdeck.com/zzzeek/building-the-app
class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class.
    """

    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any((isinstance(record_id, (str, bytes)) and record_id.isdigit(),
                isinstance(record_id, (int, float)))):
            return cls.query.get(int(record_id))
        return None


def reference_col(
        tablename, nullable=False, pk_name="id",
        foreign_key_kwargs=None, column_kwargs=None):
    """Column that adds primary key foreign key reference.
    Usage ::
        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return db.Column(
        db.ForeignKey(
            "{0}.{1}".format(tablename, pk_name), **foreign_key_kwargs
            ),
        nullable=nullable,
        **column_kwargs
        )


class User(Model, SurrogatePK):
    """Base User model

    Inherits from Model and SurrogatePK.  Contains fields for interacting with
    flask-praetorian, user authentication/security.
    """

    __tablename__ = 'users'

    username = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=False)

    # flask-praetorian requirements
    roles = db.Column(db.String)
    is_active = db.Column(
        db.Boolean(), default=True, server_default='true')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = guard.hash_password(password)

    @property
    def rolenames(self):
        """Explode role names on comma

        self.roles is a string that contains a comma deliminated list of roles.
        This returns a list, which get's consumed by a praetorian decorator to
        parse.
        """
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, email):
        """Lookup user by email"""
        return cls.query.filter_by(email=email).one_or_none()

    @classmethod
    def identify(cls, user_id):
        """Get User by id"""
        return cls.query.get(user_id)

    @property
    def identity(self):
        """Return id of current User"""
        return self.id

    def is_valid(self):
        """Is User valid

        Determine if the user is valid or not.  When set False, that user
        cannot log in.
        """
        return self.is_active

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'roles': self.roles,
            'is_active': self.is_active,
            'admin': self.admin
            }
