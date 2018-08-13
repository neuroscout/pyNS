"""Provides the Dataset related classes."""
from .base import Base

class Analyses(Base):
    _base_path = 'analyses'
    _auto_methods = ('get', 'post', 'put', 'delete')
