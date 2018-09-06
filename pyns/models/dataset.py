"""Provides the Dataset related classes."""
from .base import Base

class Datasets(Base):
    _base_path_= 'datasets'
    _auto_methods_= ('get', )

class Tasks(Base):
    _base_path_= 'tasks'
    _auto_methods_= ('get', )

class Runs(Base):
    _base_path_= 'runs'
    _auto_methods_= ('get', )
