"""Provides the Predictor related classes."""
from .base import Base

class Predictors(Base):
    _base_path_= 'predictors'
    _auto_methods_= ('get', )

class PredictorEvents(Base):
    _base_path_= 'predictor-events'
    _auto_methods_= ('get', )
