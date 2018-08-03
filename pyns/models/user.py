"""Provides the User class."""
from .base import Base

class User(Base):
    def __init__(self, reddit):
        """Initialize a User instance.
        This class is intended to be interfaced with through ``neuroscout.user``.
        """
        super(User, self).__init__(reddit, None)

    def profile(self):
        return self._neuroscout.get('user')
