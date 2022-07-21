"""Dataset related endpoints (including Tasks and Runs)"""
from .base import Base


class Datasets(Base):
    """Datasets endpoint
    
    auto_methods: `get`
    """
    _base_path_ = 'datasets'
    _auto_methods_ = ('get', )


class Tasks(Base):
    """Tasks endpoint
    
    auto_methods: `get`
    """
    _base_path_ = 'tasks'
    _auto_methods_ = ('get', )
    _convert_dt_to_ids_ = True


class Runs(Base):
    """Runs endpoint
    
    auto_methods: `get`
    """
    _base_path_ = 'runs'
    _auto_methods_ = ('get', )
    _convert_dt_to_ids_ = True