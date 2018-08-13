"""Provides the Dataset related classes."""
from .base import Base

class Datasets(Base):
    _base_path = 'datasets'
    _allowed_methods = ('get', )

class Tasks(Base):
    _base_path = 'tasks'
    _allowed_methods = ('get', )

class Runs(Base):
    _base_path = 'runs'
    _allowed_methods = ('get', )
