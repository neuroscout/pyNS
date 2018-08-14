"""Provides the Dataset related classes."""
from .base import Base

class Analyses(Base):
    _base_path = 'analyses'
    _auto_methods = ('get', 'post', 'put')

    def delete(self, id):
        """ Delete analysis
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self._client._delete(self._base_path, id=id)

    def bundle(self, id):
        """ Get analysis bundle
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=id, sub_route='bundle')

    def clone(self, id):
        """ Clone analysis
        :param str id: Analysis hash_id.
        :return: client response object, with new analysis id
        """
        return self.post(id=id, sub_route='clone')

    def compile(self, id):
        """ Submit analysis for complication
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.post(id=id, sub_route='compile')

    def full(self, id):
        """ Submit analysis for complication
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=id, sub_route='full')

    def resources(self, id):
        """ Get analysis resources
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=id, sub_route='resources')

    def status(self, id):
        """ Get analysis status
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=id, sub_route='status')
