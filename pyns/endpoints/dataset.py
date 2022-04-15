"""Dataset related endpoints (including Tasks and Runs)"""
from .base import Base


class Datasets(Base):
    """Datsets endpoint
    
    auto_methods: `get`
    """
    base_path_ = 'datasets'
    _auto_methods_ = ('get', )


class Tasks(Base):
    """Tasks endpoint
    
    auto_methods: `get`
    """
    _base_path_ = 'tasks'
    _auto_methods_ = ('get', )


class Runs(Base):
    """Runs endpoint
    
    auto_methods: `get`
    """
    _base_path_ = 'runs'
    _auto_methods_ = ('get', )
