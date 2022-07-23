from time import sleep


def test_predictor(recorder, neuroscout):
    with recorder.use_cassette('predictor'):
        resp = neuroscout.predictors.get(run_id=126)
        assert len(resp) > 20

        first = resp[0]
        assert 'source' in first

        resp = neuroscout.predictors.get(id=first['id'])
        assert 'source' in resp

        resp = neuroscout.predictors.get(dataset_name='studyforrest')
        assert resp[0]['dataset_id'] == 11
        assert resp[-1]['dataset_id'] == 11

        resp2 = neuroscout.predictors.get(dataset_name='studyforrest', subject=16)
        resp3 = neuroscout.predictors.get(dataset_name='studyforrest', subject=14)

        assert len(resp2) == len(resp3)


def test_predictor_collection(recorder, neuroscout, get_test_data_path):
    with recorder.use_cassette('predictor_collection'):
        resp = neuroscout.predictors.create_collection(
                "test_collection", dataset_id=10, runs=[[10, 9], [8, 7]],
                event_files=[str(get_test_data_path / "new_events1.tsv"),
                             str(get_test_data_path / "new_events1.tsv")],
                descriptions={"reaction_time": "fake RT"})
        assert resp['collection_name'] == "test_collection"
        assert resp['status'] == "PENDING"

        new = neuroscout.predictors.get_collection(resp['id'])
        while new['status'] == "PENDING":
            sleep(1)
            new = neuroscout.predictors.get_collection(resp['id'])

        assert len(new['predictors']) == 3
