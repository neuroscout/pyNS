"""Provides the User class."""
from .base import Base


class User(Base):
    _base_path_ = 'user'
    _auto_methods_ = ('get', 'post', 'put')

    def get_predictors(self, **kwargs):
        """ Get Predictors uploaded by user
        :return: client response object
        """
        return self.get(sub_route='predictors', **kwargs)
    
    def get_analyses(self, load=False):
        """ Get NeuroVault uploads associated with this analysis
        :param str id: Analysis hash_id.
        :return: client response object
        """
        
        return self.get(sub_route='myanalyses', **kwargs)
