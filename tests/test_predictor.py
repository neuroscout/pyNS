def test_predictor(recorder, neuroscout):
    with recorder.use_cassette('predictor'):
        resp = neuroscout.predictors.get(dataset_id=5, run_id=126)
        assert resp.status_code == 200
        assert len(resp.json()) > 20

        first = resp.json()[0]
        assert 'source' in first

        resp = neuroscout.predictors.get(id=first['id'])
        assert resp.status_code == 200
        assert 'source' in resp.json()

        resp = neuroscout.predictor_events.get(predictor_id=first['id'])
        assert resp.status_code == 200
        assert len(resp.json()) > 20

        first = resp.json()[0]
        assert 'duration' in first
