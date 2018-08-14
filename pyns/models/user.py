"""Provides the User class."""
from .base import Base

class User(Base):
    _base_path = 'user'
    _auto_methods = ('get', 'post', 'put')

    def resend_confimation(self):
        pass

    def reset_password(self):
        pass
