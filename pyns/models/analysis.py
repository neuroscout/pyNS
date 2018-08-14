"""Provides the Dataset related classes."""
from .base import Base

class Analyses(Base):
    _base_path = 'analyses'
    _auto_methods = ('get', 'post', 'put')

    def delete(self, analysis_id):
        """ Delete analysis
        :param str analysis_id: Analysis hash_id.
        :return: client response object
        """
        return self._client._delete(self._base_path, id=analysis_id)

    def bundle(self, analysis_id):
        """ Get analysis bundle
        :param str analysis_id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=analysis_id, sub_route='bundle')

    def clone(self, analysis_id):
        """ Clone analysis
        :param str analysis_id: Analysis hash_id.
        :return: client response object, with new analysis id
        """
        return self.post(id=analysis_id, sub_route='clone')

    def compile(self, analysis_id):
        """ Submit analysis for complication
        :param str analysis_id: Analysis hash_id.
        :return: client response object
        """
        return self.post(id=analysis_id, sub_route='compile')

    def full(self, analysis_id):
        """ Submit analysis for complication
        :param str analysis_id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=analysis_id, sub_route='full')

    def resources(self, analysis_id):
        """ Get analysis resources
        :param str analysis_id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=analysis_id, sub_route='resources')

    def status(self, analysis_id):
        """ Get analysis status
        :param str analysis_id: Analysis hash_id.
        :return: client response object
        """
        return self.get(id=analysis_id, sub_route='status')
