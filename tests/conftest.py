import os
import pytest
import betamax
from betamax_serializers import pretty_json

from pyns import Neuroscout

USER_TEST_EMAIL = os.environ.get('USER_TEST_EMAIL', '** secret user **')
USER_TEST_PWD = os.environ.get('USER_TEST_PWD', '** secret password **')

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.define_cassette_placeholder('<USER_TEST_EMAIL>', USER_TEST_EMAIL)
    config.define_cassette_placeholder('<USER_TEST_PWD>', USER_TEST_PWD)


@pytest.fixture(scope='function')
def client_recorder():
    """ Sets up client, recorder pair """
    client = Neuroscout()
    return betamax.Betamax(client.session), client

@pytest.fixture(scope='function')
def recorder(client_recorder):
    """ Returns only recorder """
    return client_recorder[0]

@pytest.fixture(scope='function')
def client(client_recorder):
    """ Authorizes and returns client """
    recorder, client = client_recorder
    with recorder.use_cassette('auth'):
        client._authorize(email=USER_TEST_EMAIL, password=USER_TEST_PWD)
    return client
