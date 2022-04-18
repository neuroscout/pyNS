Usage
=====

.. _installation:

Installation
------------

To use pyNS, first install it using pip:

.. code-block:: console

   $ pip install pyns

Quickstart
----------

.. note::
   For a full tutorial see this `Jupyter Notebook <https://github.com/neuroscout/pyNS/blob/master/examples/Tutorial.ipynb>`_ or
   the Neuroscout Paper `Jupyter Book <https://neuroscout.github.io/neuroscout-paper/intro.html>`_

We are assuming you already have valid Neuroscout API credentials (and
if you dont, sign up at: ``neuroscout.org``)

First, instantiate a Neuroscout API Client object:

::

   from pyns import Neuroscout
   neuroscout = Neuroscout(username='USERNAME', password='PASSWORD')

With the ``neuroscout`` instance, you can interact with the API. All of
the major routes are linked to the main ``neuroscout`` object, and
return ``requests`` ``Response`` objects.

For example we can retrieve our user profile:

::

   >>> neuroscout.user.get()
   {'email': 'user@example.com',
    'analyses': [ {'description': 'Does the brain care about language?',
     'hash_id': 'RZd',
     'modified_at': '2018-08-09T23:3',
     'name': 'My new analysis',
     'status': 'PASSED'}]]}

Or query various endpoints, such as ``datasets``:

::

   >>> neuroscout.datasets.get()
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

For example, we could use this to get the first predictor associated
with a dataset:

::

   >>> first = neuroscout.predictors.get(dataset_id=5)[0]
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

::

   >>> neuroscout.predictor_events.get(predictor_id=first['id'])[0:2]
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