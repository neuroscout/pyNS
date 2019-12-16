def test_dataset(recorder, neuroscout):
    with recorder.use_cassette('dataset'):
        resp = neuroscout.datasets.get()

        assert len(resp) > 1

        resp = neuroscout.datasets.get(id=5)
        runs = resp['runs']
        assert len(runs) > 10
        tasks = resp['tasks']
        assert len(tasks) == 2

        resp = neuroscout.tasks.get(dataset_id=5)
        assert resp[0]['name'] == tasks[0]['name']

        resp = neuroscout.runs.get(dataset_id=5)
        assert len(resp) == len(runs)
