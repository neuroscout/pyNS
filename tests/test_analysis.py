import pytest
from time import sleep
from requests.exceptions import HTTPError

TEST_ANALYSIS = {
  "dataset_id": 5,
  "model": {
    "blocks": [
      {
        "auto_contrasts": True,
        "contrasts": [],
        "level": "run",
        "model": {
          "HRF_variables": [],
          "variables": [
            "brightness"
          ]
        },
        "transformations": []
      },
      {
        "auto_contrasts": True,
        "level": "dataset"
      }
    ],
    "input": {
      "subject": [
        "28"
      ],
      "task": "MerlinMovie"
    },
    "name": "pytest_analysis"
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
            predictor_names=['brightness'],
            subject=['28'])

    return new

def test_analysis_object(recorder, analysis_object):
    assert analysis_object.status == 'DRAFT'
    assert analysis_object.name == 'pytest_analysis'
    assert analysis_object.description == None

    analysis_object.description = 'new_description'

    with recorder.use_cassette('test_analysis_object'):
        analysis_object.push()
        assert analysis_object.description == 'new_description'

        analysis_object.description = 'overwritten'
        analysis_object.pull()
        assert analysis_object.description == 'new_description'

        assert analysis_object.get_status()['status'] == 'DRAFT'

        # compile
        analysis_object.compile()
        assert analysis_object.get_status()['status'] != 'DRAFT'

        assert 'dataset_address' in analysis_object.get_resources()
        assert hasattr(analysis_object, 'dataset_address')

        # clone
        new = analysis_object.clone()
        assert new.name == analysis_object.name
        assert new.hash_id != analysis_object.hash_id

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

        # Test compile
        resp = neuroscout.analyses.compile(id=analysis_id)
        assert resp['hash_id'] == analysis_id
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
