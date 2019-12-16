import pytest
from time import sleep
from requests.exceptions import HTTPError

TEST_ANALYSIS = {
  "dataset_id": 5,
  "model": {
    "Steps": [
      {
        "DummyContrasts": {"Type": "t"},
        "Contrasts": [],
        "Level": "Run",
        "Model": {
          "X": [
            "brightness"
          ]
        },
        "Transformations": []
      },
      {
        "DummyContrasts": {"Type": "t"},
        "Level": "Dataset"
      }
    ],
    "Input": {
      "Subject": [
        "28"
      ],
      "Task": "MerlinMovie"
    },
    "Name": "pytest_analysis"
  },
  "name": "pytest_analysis",
  "predictors": [12728],
  "runs": [126],
  "task_name": "MerlinMovie",
}


@pytest.fixture(scope='module')
def analysis(recorder, neuroscout):
    """ Creates analysis """
    with recorder.use_cassette('analysis'):
        new = neuroscout.analyses.post(**TEST_ANALYSIS)

    return new


@pytest.fixture(scope='module')
def analysis_object(recorder, neuroscout):
    """ Create analysis object """
    with recorder.use_cassette('analysis_object'):
        new = neuroscout.analyses.create_analysis(
            name='pytest_analysis',
            dataset_name='SherlockMerlin',
            task='MerlinMovie',
            predictor_names=['brightness'],
            hrf_variables=['brightness'],
            subject=['28'])

    return new


def test_analysis_object(recorder, neuroscout, analysis_object):
    assert analysis_object.status == 'DRAFT'
    assert analysis_object.name == 'pytest_analysis'
    assert analysis_object.description is None

    analysis_object.description = 'new_description'

    with recorder.use_cassette('test_analysis_object'):
        analysis_object.push()
        assert analysis_object.description == 'new_description'

        analysis_object.description = 'overwritten'
        analysis_object.pull()
        assert analysis_object.description == 'new_description'

        assert analysis_object.get_status()['status'] == 'DRAFT'

        # test fill
        analysis_object.predictors = []
        analysis_object.push()
        analysis_object.fill()
        assert len(analysis_object.predictors) == 1

        # Test get_report
        resp = analysis_object.generate_report(run_id=analysis_object.runs[0])
        assert resp['status'] == 'PENDING'

        # Wait until compiled
        while(resp['status'] == 'PENDING'):
            sleep(1)
            resp = analysis_object.get_report(run_id=analysis_object.runs[0])

        assert len(resp['result']['design_matrix']) == 1

        # compile
        analysis_object.compile()
        assert analysis_object.get_status()['status'] != 'DRAFT'

        assert 'dataset_address' in analysis_object.get_resources()
        assert hasattr(analysis_object, 'dataset_address')

        while analysis_object.get_status()['status'] != 'PASSED':
            sleep(1)

        # clone
        new = analysis_object.clone()
        assert new.name == analysis_object.name
        assert new.hash_id != analysis_object.hash_id
        assert new.parent_id == analysis_object.hash_id

        # Create object from existing id
        same = neuroscout.analyses.get_analysis(id=new.hash_id)
        assert same.hash_id == new.hash_id
        assert same.name == new.name

        # Test delete
        new.delete()

        with pytest.raises(HTTPError):
            analysis_object._analyses.get(id=new.hash_id)


def test_get_analysis(recorder, neuroscout, analysis):
    analysis_id = analysis['hash_id']

    # Test get
    with recorder.use_cassette('get_analysis'):
        resp = neuroscout.analyses.get(id=analysis_id)
        assert resp['name'] == 'pytest_analysis'
        assert resp['status'] == 'DRAFT'


def test_put_analysis(recorder, neuroscout, analysis):
    analysis_id = analysis['hash_id']

    analysis['description'] = 'new_description'

    # Test put
    with recorder.use_cassette('put_analysis'):
        resp = neuroscout.analyses.put(id=analysis_id, **analysis)

        assert resp['name'] == 'pytest_analysis'
        assert resp['description'] == 'new_description'


def test_id_actions(recorder, neuroscout, analysis):
    analysis_id = analysis['hash_id']

    with recorder.use_cassette('id_analysis'):
        # Test full
        resp = neuroscout.analyses.full(id=analysis_id)
        assert 'runs' in resp

        # Test get_report
        resp = neuroscout.analyses.generate_report(id=analysis_id,
                                                   run_id=analysis['runs'][0])
        assert resp['status'] == 'PENDING'

        # Wait until compiled
        while(resp['status'] == 'PENDING'):
            sleep(1)
            resp = neuroscout.analyses.get_report(id=analysis_id,
                                                  run_id=analysis['runs'][0])

        assert len(resp['result']['design_matrix']) == 1

        # Test fill

        analysis['runs'] = []
        analysis['predictors'] = []

        # Put first
        resp = neuroscout.analyses.put(id=analysis_id, **analysis)
        assert len(resp['predictors']) == 0

        resp = neuroscout.analyses.fill(
            id=analysis_id)

        assert len(resp['runs']) == 36
        assert len(resp['predictors']) == 1

        # Test compile
        resp = neuroscout.analyses.compile(id=analysis_id)
        assert resp['status'] == 'PENDING'

        # Test status
        resp = neuroscout.analyses.status(id=analysis_id)
        assert 'status' in resp

        # Wait until compiled
        while(resp['status'] == 'PENDING'):
            sleep(1)
            resp = neuroscout.analyses.status(id=analysis_id)

        # Test resources
        resp = neuroscout.analyses.resources(id=analysis_id)
        assert 'dataset_address' in resp

        # Test bundle
        resp = neuroscout.analyses.bundle(id=analysis_id)

        # Test clone
        resp = neuroscout.analyses.clone(id=analysis_id)
        new_id = resp['hash_id']
        assert new_id != analysis_id

        # Test delete
        resp = neuroscout.analyses.delete(id=new_id)


def test_upload_analysis(recorder, neuroscout, analysis, get_test_data_path):
    analysis_id = 'A1rYM'  # This is an existing analysis on the api

    with recorder.use_cassette('upload_analysis'):
        group_paths = [str(p) for p in
                       (get_test_data_path / 'fitlins').glob('task*')]
        sub_paths = [str(p) for p in
                     (get_test_data_path / 'fitlins').glob('sub*')]
        resp = neuroscout.analyses.upload_neurovault(
            id=analysis_id, group_paths=group_paths,
            subject_paths=sub_paths,
            validation_hash='QEynReX0Xp', force=True,
            n_subjects=99)

        assert 'uploaded_at' in resp
        uploaded_at = resp['uploaded_at']

        # Check uploads
        uploads = neuroscout.analyses.get_uploads(id=analysis_id)

        assert len(uploads) >= 1
        newest = [u for u in uploads if u['uploaded_at'] == uploaded_at][0]

        # Wait until compiled
        while(
          any([True for f in newest['files'] if f['status'] == 'PENDING'])):
            sleep(2)
            uploads = neuroscout.analyses.get_uploads(id=analysis_id)
            newest = [u for u in uploads if u['uploaded_at'] == uploaded_at]
            if len(newest) > 0:
                newest = newest[0]

        assert all([f['status'] == 'OK' for f in newest['files']])
        assert newest['collection_id'] is not None
