import pytest
from pyns.client import Client

@pytest.fixture(scope="function")
def client():
    """ Client authorizer with test user """

    client = Client(email="test-email@tests.com", password="onlyfortesting")
    return client
