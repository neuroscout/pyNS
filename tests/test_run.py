
def test_run(recorder, neuroscout):
    with recorder.use_cassette('run'):
        resp = neuroscout.runs.get()
        assert len(resp) > 1

        resp = neuroscout.runs.get(id=5)
        assert isinstance(resp, dict)
        assert resp['id'] == 5

        resp = neuroscout.runs.get(dataset_id=5)
        resp2 = neuroscout.runs.get(dataset_name='SherlockMerlin')
        assert resp == resp2

        resp3 = neuroscout.runs.get(dataset_name='SherlockMerlin',
                                   task_name='MerlinMovie')
        assert len(resp3) < len(resp2)

        resp4 = neuroscout.runs.get(dataset_id=5,
                                   task_id=4)

        assert resp3 == resp4
