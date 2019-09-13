"""Provides the User class."""
from .base import Base


class User(Base):
    _base_path_ = 'user'
    _auto_methods_ = ('get', 'post', 'put')

    def get_predictors(self):
        """ Get NeuroVault uploads associated with this analysis
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(sub_route='predictors')
