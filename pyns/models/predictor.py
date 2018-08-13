"""Provides the Predictor related classes."""
from .base import Base

class Predictors(Base):
    _base_path = 'predictors'
    _allowed_methods = ('get', )

class PredictorEvents(Base):
    _base_path = 'predictor-events'
    _allowed_methods = ('get', )
