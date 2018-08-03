"""Provide the Base superclass."""


class Base(object):
    """Superclass for all models."""

    @classmethod
    def parse(cls, data, neuroscout):
        """Return an instance of ``cls`` from ``data``.
        :param data: The structured data.
        :param reddit: An instance of :class:`.Neuroscout`.
        """
        return cls(neuroscout, _data=data)

    def __init__(self, neuroscout, _data):
        """Initialize a Model instance.
        :param reddit: An instance of :class:`.Neuroscout`.
        """
        self._neuroscout = neuroscout
        if _data:
            for attribute, value in _data.items():
                setattr(self, attribute, value)
