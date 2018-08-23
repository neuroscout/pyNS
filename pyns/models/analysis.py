"""Provides the Analysis related classes."""
from .base import Base
from pathlib import Path

class Analyses(Base):
    _base_path = 'analyses'
    _auto_methods = ('get', 'post', 'put')

    def delete(self, id):
        """ Delete analysis
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self._client._delete(self._base_path, id=id)

    def bundle(self, id, filename=None):
        """ Get analysis bundle
        :param str id: Analysis hash_id.
        :param str, object filename: Optional filename to save bundle to
        :return: client response object
        """
        bundle = self.get(id=id, sub_route='bundle')
        if filename is not None:
            if isinstance(filename, str):
                filename = Path(filename)
            with filename.open('wb') as f:
                f.write(bundle.content)
        else:
            return bundle

    def clone(self, id):
        """ Clone analysis
        :param str id: Analysis hash_id.
        :return: client response object, with new analysis id
        """
        return self.post(id=id, sub_route='clone')

    def compile(self, id):
        """ Submit analysis for complilation
        :param str id: Analysis hash_id.
        :return: client response object
        """
        return self.post(id=id, sub_route='compile')

    def full(self, id):
        """ Get full analysis object (including runs and predictors)
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
