def test_predictor(recorder, neuroscout):
    with recorder.use_cassette('predictor'):
        resp = neuroscout.predictors.get(dataset_id=5, run_id=126)
        assert len(resp) > 20

        first = resp[0]
        assert 'source' in first

        resp = neuroscout.predictors.get(id=first['id'])
        assert 'source' in resp

        resp = neuroscout.predictor_events.get(predictor_id=first['id'])
        assert len(resp) > 20

        first = resp[0]
        assert 'duration' in first
