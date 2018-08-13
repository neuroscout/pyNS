
def test_auth(recorder, neuroscout):
    assert neuroscout._api_token is not None
    assert len(neuroscout._api_token)

def test_datasets(recorder, neuroscout):
    with recorder.use_cassette('get_dataset'):
        resp = neuroscout._get('datasets')
        assert resp.status_code == 200

        datasets = resp.json()
        assert len(datasets) > 4
