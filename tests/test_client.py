def test_auth(recorder, neuroscout):
    assert neuroscout._api_token is not None
    assert len(neuroscout._api_token)

def test_datasets(recorder, neuroscout):
    with recorder.use_cassette('get_dataset'):
        resp = neuroscout._get('datasets')

        datasets = resp
        assert len(datasets) > 1
