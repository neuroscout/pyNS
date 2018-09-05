"""Provides the User class."""
from .base import Base

class User(Base):
    _base_path_= 'user'
    _autho_methods_= ('get', 'post', 'put')
