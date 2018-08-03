"""
    pyns
    ~~~~~~~~~~~~~~~~~~~
    A client for interfacing with http://neuroscout.org API
    :copyright: (c) 2018 by Alejandro de la Vega.
    :license: MIT, see LICENSE for more details.
"""

API_BASE_URL = 'http://alpha.neuroscout.org/api/'

from .api import Neuroscout

__all__ = ['Neuroscout']

__author__ = ['Alejandro de la Vega']
__license__ = 'MIT'
