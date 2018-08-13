"""Provides the Dataset related classes."""
from .base import Base

class Datasets(Base):
    _base_path = 'datasets'
    _auto_methods = ('get', )

class Tasks(Base):
    _base_path = 'tasks'
    _auto_methods = ('get', )

class Runs(Base):
    _base_path = 'runs'
    _auto_methods = ('get', )
