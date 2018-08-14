"""Provides the Dataset related classes."""
from .base import Base

class Analyses(Base):
    _base_path = 'analyses'
    _auto_methods = ('get', 'post', 'put')

    def delete(self, id):
        """ Delete analysis
        :param id: Analysis hash_id.
        """
        return self._client._delete(self._base_path, id=id)

    def get_bundle(self):
        pass

    def clone(self):
        pass

    def compile(self):
        pass

    def get_full(self):
        pass

    def get_resources(self):
        pass

    def get_status(self):
        pass
