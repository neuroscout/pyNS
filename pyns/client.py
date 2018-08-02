import requests
import json
from functools import partialmethod

from . import API_BASE_URL

class Client(object):
    def __init__(self, email=None, password=None, session=None,
                 api_base_url=None):
        if session is None:
            self.session = requests.Session()
            self.flask_session = False
        else:
            self.flask_session = session
            self.client_flask = False

        self.api_base_url = api_base_url or API_BASE_URL

        self.token = None

        if email is not None and password is not None:
            self.email = email
            self.password = password
            self._authorize(email, password)

    def _get_headers(self):
        if self.token is not None:
           return {'Authorization': 'JWT %s' % self.token}
        else:
            return None

    def _make_request(self, request, route, params=None, data=None, headers=None):
        """ Generic request handler """
        request_function = getattr(self.session, request)
        headers = headers or self._get_headers()

        if self.flask_session:
            return request_function(self.api_base_url + route, data=json.dumps(data),
                content_type='application/json', headers=headers, query_string=params)
        else:
            return request_function(self.api_base_url + route, json=data,
                headers=headers, params=params)

    def _authorize(self, email=None, password=None):
        if email is not None and password is not None:
            self.email = email
            self.password = password

        rv = self.post('/api/auth',
                        data={'email': self.email, 'password': self.password})

        if self.flask_session:
             self.token = json.loads(rv.data.decode())['access_token']
        else:
            self.token = rv.json()['access_token']

    get = partialmethod(_make_request, 'get')
    post = partialmethod(_make_request, 'post')
    put = partialmethod(_make_request, 'put')
    delete = partialmethod(_make_request, 'delete')
