"""Base endpoint class"""
from abc import ABC, abstractmethod
from functools import partial
from .utils import names_to_ids

class Base(ABC):
    """Superclass for all resources.
    
    All classes that inherent this can automatically have
    `get`, `post`, `put`, and `delete` methods associated 
    with them, if they are compatible with that endpoint. 
    
    These are listed in subclasses as `auto_methods`.
    """

    _convert_names_to_ids_ = False
    _auto_methods_ = ()

    def __init__(self, client):
        """Initialize a Model instance.

        :param client: base client instance
        :type client: :class:`.Neuroscout`
        """
        self._client = client

        all_methods = ('get', 'post', 'put', 'delete')
        assert set(self._auto_methods_) <= set(all_methods)

        for method in self._auto_methods_:
            setattr(self,
                    method,
                    partial(
                        getattr(self._client, "_" + method),
                        self._base_path_)
            )
            # For get methods, automatically convert dataset and task name to ID
            if method == 'get':
                if self._convert_names_to_ids_ is True:
                    setattr(self,
                            method,
                            names_to_ids(getattr(self, method))
                    )

    @property
    @abstractmethod
    def _base_path_(self):
        pass

    @property
    @abstractmethod
    def _auto_methods_(self):
        """ HTTP methods to auto create in subordinate classes """
        pass
