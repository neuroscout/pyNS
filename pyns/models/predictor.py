"""Provides the Predictor related classes."""
from .base import Base

class Predictors(Base):
    _base_path = 'predictors'
    _auto_methods = ('get', )

class PredictorEvents(Base):
    _base_path = 'predictor-events'
    _auto_methods = ('get', )
