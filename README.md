# pyNS 🌲
[![Build Status](https://travis-ci.org/neuroscout/pyns.svg?branch=master)](https://travis-ci.org/neuroscout/pyns)
[![codecov](https://codecov.io/gh/neuroscout/pyns/branch/master/graph/badge.svg)](https://codecov.io/gh/neuroscout/pyns)

The Neuroscout API wrapper for Python

### Overview
py-ns is a python package to easily interact with the Neuroscout API.

For more API documentation, check out the Swagger API Docs: http://alpha.neuroscout.org/swagger-ui/

### Installation
py-ns is supported in Python 3.4+
Use `pip` to install it from github:

    pip install --upgrade https://github.com/neuroscout/pyns/archive/master.zip

### Quickstart
We are assuming you already have valid Neuroscout API credentials (and if you dont, sign up at: `alpha.neuroscout.org`)

First, instantiate a Neuroscout API Client object:

    from pyns import Neuroscout
    neuroscout = Neuroscout(username='USERNAME', password='PASSWORD')

With the `neuroscout` instance, you can interact with the API. All of the major routes are linked to the main `neuroscout` object,
and return `requests` `Response` objects.

For example we can retrieve our user profile:

    >>> neuroscout.user.get().json()
    {'email': 'user@example.com',
     'analyses': [ {'description': 'Does the brain care about language?',
      'hash_id': 'RZd',
      'modified_at': '2018-08-09T23:3',
      'name': 'My new analysis',
      'status': 'PASSED'}]]}

Or query various endpoints, such as `datasets`:

    >>> neuroscout.datasets.get().json()
    [{'description': {'Acknowledgements': '',
       'Authors': ['Tomoyasu Horikawa', 'Yukiyasu Kamitani'],
       'DatasetDOI': '',
       'Funding': '',
       'HowToAcknowledge': '',
       'License': '',
       'Name': 'Generic Object Decoding (fMRI on ImageNet)',
       'ReferencesAndLinks': ['Horikawa & Kamitani (2017) Generic decoding of seen and imagined objects using hierarchical visual features. Nature Communications volume 8:15037. doi:10.1038/ncomms15037']},
      'id': 1,
      'name': 'generic_object_decoding',
    ...
      'tasks': [{'id': 8, 'name': 'life'}]}]

For example, we could use this to get the first predictor associated with a dataset:

    >>> first = neuroscout.predictors.get(dataset_id=5).json()[0]
    {'description': 'Bounding polygon around face. y coordinate for vertex 1',
     'extracted_feature': {'created_at': '2018-04-12 00:44:14.868349',
      'description': 'Bounding polygon around face. y coordinate for vertex 1',
      'extractor_name': 'GoogleVisionAPIFaceExtractor',
      'id': 102,
      'modality': None},
     'id': 197,
     'name': 'boundingPoly_vertex1_y',
     'source': 'extracted'}


And get the predictor-events associated with that predictor:

    >>> neuroscout.predictor_events.get(predictor_id=first['id']).json()[0:2]
    [{'duration': 9.0,
      'id': '1050781',
      'onset': 114.0,
      'predictor_id': 197,
      'run_id': 2,
      'value': '13'},
     {'duration': 9.0,
      'id': '1050782',
      'onset': 114.0,
      'predictor_id': 197,
      'run_id': 26,
      'value': '13'}]




### Testing
We use pytest for testing, and betamax to record HTTP requests used in test into cassettes.

To re-run tests locally set the`USER_TEST_EMAIL` and `USER_TEST_PWD` environment variables with valid API credentials.
