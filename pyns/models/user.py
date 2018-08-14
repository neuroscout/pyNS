"""Provides the User class."""
from .base import Base

class User(Base):
    _base_path = 'user'
    _auto_methods = ('get', 'post', 'put')
