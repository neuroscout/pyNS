"""
    Neuroscout API client library
"""

API_BASE_URL = 'https://neuroscout.org/api'
ROUTE_PATTERN = '{base_url}/{route}[/{id}][/{sub_route}]'

from .api import Neuroscout
from . import models

__all__ = ['Neuroscout', 'models']

__author__ = ['Alejandro de la Vega']
__license__ = 'MIT'
