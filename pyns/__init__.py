"""
    pyns
    ~~~~~~~~~~~~~~~~~~~
    A client for interfacing with http://neuroscout.org API
    :copyright: (c) 2018 by Alejandro de la Vega.
    :license: MIT, see LICENSE for more details.
"""

API_BASE_URL = 'https://neuroscout.org/api'
ROUTE_PATTERN = '{base_url}/{route}[/{id}][/{sub_route}]'

from .api import Neuroscout

__all__ = ['Neuroscout']

__author__ = ['Alejandro de la Vega']
__license__ = 'MIT'
