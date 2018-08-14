import pytest
from time import sleep

@pytest.fixture(scope='module')
def analysis(recorder, neuroscout):
    """ Creates analysis """
    analysis_content = {
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
      "predictors": [
        {
          "id": 12728
        }
      ],
      "runs": [
        {
          "id": 126
        }
      ],
      "task_name": "MerlinMovie",
    }

    with recorder.use_cassette('analysis'):
        new = neuroscout.analyses.post(**analysis_content)

    return new

def test_get_analysis(recorder, neuroscout, analysis):
    analysis_id = analysis.json()['hash_id']

    # Test get
    with recorder.use_cassette('get_analysis'):
        resp = neuroscout.analyses.get(id=analysis_id)
        assert resp.status_code == 200

        analysis_json = resp.json()
        assert analysis_json['name'] == 'pytest_analysis'
        assert analysis_json['status'] == 'DRAFT'

def test_put_analysis(recorder, neuroscout, analysis):
    analysis_json = analysis.json()
    analysis_id = analysis_json['hash_id']

    analysis_json['description'] = 'new_description'

    # Test put
    with recorder.use_cassette('put_analysis'):
        resp = neuroscout.analyses.put(id=analysis_id, **analysis_json)
        assert resp.status_code == 200

        analysis_json = resp.json()
        assert analysis_json['name'] == 'pytest_analysis'
        assert analysis_json['description'] == 'new_description'

def test_id_actions(recorder, neuroscout, analysis):
    analysis_json = analysis.json()
    analysis_id = analysis_json['hash_id']

    with recorder.use_cassette('id_analysis'):
        # Test full
        resp = neuroscout.analyses.full(id=analysis_id)
        assert resp.status_code == 200
        assert 'runs' in resp.json()

        # Test compile
        resp = neuroscout.analyses.compile(id=analysis_id)
        assert resp.status_code == 200
        assert resp.json()['hash_id'] == analysis_id
        assert resp.json()['status'] == 'PENDING'

        # Test status
        resp = neuroscout.analyses.status(id=analysis_id)
        assert resp.status_code == 200
        assert 'status' in resp.json()

        # Wait until compiled
        while(resp.json()['status'] == 'PENDING'):
            sleep(1)
            resp = neuroscout.analyses.status(id=analysis_id)

        # Test resources
        resp = neuroscout.analyses.resources(id=analysis_id)
        assert resp.status_code == 200
        assert 'dataset_address' in resp.json()

        # Test bundle
        resp = neuroscout.analyses.bundle(id=analysis_id)
        assert resp.status_code == 200

        # Test clone
        resp = neuroscout.analyses.clone(id=analysis_id)
        assert resp.status_code == 200
        new_id = resp.json()['hash_id']
        assert new_id != analysis_id

        # Test delete
        resp = neuroscout.analyses.delete(id=new_id)
        assert resp.status_code == 200
