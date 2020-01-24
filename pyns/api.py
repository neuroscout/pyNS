import requests
import re
import jwt
import os
from datetime import datetime
from functools import partialmethod

from . import API_BASE_URL, ROUTE_PATTERN
from . import models


class Neuroscout(object):
    """Neuroscout API client object. This is the access point for the API.

    Args:
        email (str, optional): Email address to use for authorization.
        password (str, optional): Password for authorization (not saved)
        api_base_url (str, optional): Alternate base URL for API

    """
    def __init__(self, email=None, password=None, api_base_url=None):
        self._session = requests.Session()
        self._api_base_url = api_base_url or API_BASE_URL
        self._api_token = None

        self._authorize(email, password)

        # Set up main routes
        self.analyses = models.Analyses(self)
        self.datasets = models.Datasets(self)
        self.tasks = models.Tasks(self)
        self.runs = models.Runs(self)
        self.predictors = models.Predictors(self)
        self.predictor_events = models.PredictorEvents(self)
        self.datasets = models.Datasets(self)
        self.user = models.User(self)

    def _get_headers(self):
        """ Build authorization header """
        if self._api_token is not None:
            return {'Authorization': 'JWT %s' % self._api_token}
        else:
            return None

    def _build_path(self, route, **kwargs):
        """ Build and format a URI for a request.

        Args:
            route (str): Primary API route. E.g. 'user'
            kwargs (dict): Dictionary of variables used to format URI.

        Returns:
            path (str): Formatted URI
        """
        def _replace_variables(pattern, variables):
            for name in re.findall("\{(.*?)\}", pattern):
                if name in variables and variables[name] is not None:
                    di = {name: str(variables[name])}
                    pattern = pattern.format(**di)
                else:
                    return ''

            return pattern

        new_path = ROUTE_PATTERN
        optional_patterns = re.findall('\[(.*?)\]', ROUTE_PATTERN)

        for pattern in optional_patterns:
            chunk = _replace_variables(pattern, kwargs)
            new_path = new_path.replace('[%s]' % pattern, chunk)

        return new_path.format(base_url=self._api_base_url, route=route)

    def _make_request(self, request, route, sub_route=None, id=None,
                      params=None, data=None,
                      json=None, headers=None, remove_null=True,
                      files=None, **kwargs):
        """ Generic request handler """

        if route != 'auth':
            self._check_expiry()

        request_function = getattr(self._session, request)

        if remove_null is True:
            kwargs = {k: v for (k, v) in kwargs.items() if v is not None}

        if request == 'get':
            params = kwargs
            # Join lists as comma separated list
            for k, v in params.items():
                if isinstance(v, list):
                    v = [str(i) for i in v]
                    params[k] = ','.join(v)

        elif request in ['put', 'post']:
            if files:
                data = kwargs
            else:
                json = kwargs

        headers = headers or self._get_headers()
        route = self._build_path(route, sub_route=sub_route, id=id)

        resp = request_function(
            route, json=json, data=data, files=files,
            headers=headers, params=params)

        if resp.headers.get('Content-Type') == 'application/json':
            content = resp.json()
        else:
            content = resp.content

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as error:
            if isinstance(content, dict):
                if content.get('message') is not None:
                    error = str(error) + "\n Message: {}".format(
                        content['message'])

            raise requests.exceptions.HTTPError(error)

        return content

    def _authorize(self, email=None, password=None):
        """ Fetch api_token given access credentials """
        if email is None and 'NEUROSCOUT_USER' in os.environ:
            email = os.environ['NEUROSCOUT_USER']
        if password is None and 'NEUROSCOUT_PASSWORD' in os.environ:
            password = os.environ['NEUROSCOUT_PASSWORD']

        if email is not None and password is not None:
            rv = self._post('auth', email=email, password=password)
            self._api_token = rv['access_token']

            iat = datetime.utcfromtimestamp(
                jwt.decode(self._api_token, verify=False)['iat'])
            adj = iat - datetime.now()
            self._api_token_exp = datetime.utcfromtimestamp(
                jwt.decode(self._api_token, verify=False)['exp']) - adj

    def _check_expiry(self):
        if self._api_token is not None:
            if datetime.now() > self._api_token_exp:
                self._authorize()

    _get = partialmethod(_make_request, 'get')
    _post = partialmethod(_make_request, 'post')
    _put = partialmethod(_make_request, 'put')
    _delete = partialmethod(_make_request, 'delete')
