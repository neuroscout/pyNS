"""User endpoint"""
from .base import Base


class User(Base):
    """User endpoint
    
    auto_methods: `get`, `post`, `put`
    """
    _base_path_ = 'user'
    _auto_methods_ = ('get', 'post', 'put')

    def get_predictors(self, **kwargs):
        """ Get Predictors uploaded by user
        
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.get(sub_route='predictors', **kwargs)
    
    def get_analyses(self):
        """ Get NeuroVault uploads associated with this analysis

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        
        return self.get(sub_route='myanalyses', **kwargs)
