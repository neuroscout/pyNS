
def test_auth(recorder, client):
    assert client._api_token is not None
    assert len(client._api_token)

def test_datasets(recorder, client):
    with recorder.use_cassette('get_dataset'):
        resp = client.get('datasets')
        assert resp.status_code == 200

        datasets = resp.json()
        assert len(datasets) > 4
