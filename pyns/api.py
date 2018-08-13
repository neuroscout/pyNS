import requests
from functools import partialmethod

from . import API_BASE_URL
from . import models

class Neuroscout(object):
    def __init__(self, email=None, password=None, api_base_url=None):
        self._session = requests.Session()
        self._api_base_url = api_base_url or API_BASE_URL
        self._api_token = None

        if email is not None and password is not None:
            self._authorize(email, password)

        self.user = models.User(self)

    def _get_headers(self):
        if self._api_token is not None:
           return {'Authorization': 'JWT %s' % self._api_token}
        else:
            return None

    def _make_request(self, request, route, params=None, data=None, headers=None):
        """ Generic request handler """
        request_function = getattr(self._session, request)
        headers = headers or self._get_headers()
        route = self._api_base_url + route

        return request_function(
            route, json=data, headers=headers, params=params)

    def _authorize(self, email=None, password=None):
        rv = self._post('auth', data={'email': email, 'password': password})

        self._api_token = rv.json()['access_token']

    _get = partialmethod(_make_request, 'get')
    _post = partialmethod(_make_request, 'post')
    _put = partialmethod(_make_request, 'put')
    _delete = partialmethod(_make_request, 'delete')
