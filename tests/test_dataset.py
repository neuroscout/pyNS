def test_dataset(recorder, neuroscout):
    with recorder.use_cassette('dataset'):
        resp = neuroscout.datasets.get()
        assert resp.status_code == 200

        dataset_json = resp.json()
        assert len(dataset_json) > 3
        assert dataset_json[0]['id'] == 1

        resp = neuroscout.datasets.get(id=5)
        assert resp.status_code == 200
        runs = resp.json()['runs']
        assert len(runs) > 10
        tasks = resp.json()['tasks']
        assert len(tasks) == 1

        resp = neuroscout.tasks.get(dataset_id=5)
        assert resp.json()[0]['name'] == tasks[0]['name']

        resp = neuroscout.runs.get(dataset_id=5)
        assert len(resp.json()) == len(runs)
