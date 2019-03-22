import os
import pytest
import betamax
from betamax_serializers import pretty_json
from pathlib import Path

from pyns import Neuroscout

USER_TEST_EMAIL = os.environ.get('USER_TEST_EMAIL', '** secret user **')
USER_TEST_PWD = os.environ.get('USER_TEST_PWD', '** secret password **')

betamax.Betamax.register_serializer(pretty_json.PrettyJSONSerializer)

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = 'tests/cassettes'
    config.default_cassette_options['serialize_with'] = 'prettyjson'
    config.define_cassette_placeholder('<USER_TEST_EMAIL>', USER_TEST_EMAIL)
    config.define_cassette_placeholder('<USER_TEST_PWD>', USER_TEST_PWD)


@pytest.fixture(scope='module')
def neuroscout_recorder():
    """ Sets up client, recorder pair """
    neuroscout = Neuroscout()
    return betamax.Betamax(neuroscout._session), neuroscout


@pytest.fixture(scope='module')
def recorder(neuroscout_recorder):
    """ Returns only recorder """
    return neuroscout_recorder[0]


@pytest.fixture(scope='module')
def neuroscout(neuroscout_recorder):
    """ Authorizes and returns client """
    recorder, neuroscout = neuroscout_recorder
    with recorder.use_cassette('auth'):
        neuroscout._authorize(email=USER_TEST_EMAIL, password=USER_TEST_PWD)
    return neuroscout


@pytest.fixture(scope='module')
def get_test_data_path():
    return Path(__file__).parents[0].absolute() / 'data'
