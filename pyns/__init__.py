"""
    Neuroscout API client library
"""

API_BASE_URL = 'https://neuroscout.org/api'
ROUTE_PATTERN = '{base_url}/{route}[/{id}][/{sub_route}]'

from .api import Neuroscout
from . import endpoints

__all__ = ['Neuroscout', 'endpoints', 'fetch_utils']

__author__ = ['Alejandro de la Vega']
__license__ = 'MIT'
