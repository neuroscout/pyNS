Usage
=====

.. _installation:

Installation
------------

To use pyNS, simply install it using pip:

.. code-block:: console

   $ pip install pyns

Quickstart
----------

.. note::
   We are assuming you already have valid Neuroscout API credentials (and
   if you dont, sign up at: `neuroscout.org  <https://neuroscout.org>`_)

First, instantiate a Neuroscout API Client object:

::

   from pyns import Neuroscout
   neuroscout = Neuroscout(username='USERNAME', password='PASSWORD')

With the ``neuroscout`` instance, you can interact with the API. All of
the major routes are linked to the main ``neuroscout`` object, and
return JSON objects.

For example we can retrieve our user profile:

::

   >>> neuroscout.user.get()
   {'email': 'user@example.com',
    'analyses': [ {'description': 'Does the brain care about language?',
     'hash_id': 'RZd',
     'modified_at': '2018-08-09T23:3',
     'name': 'My new analysis',
     'status': 'PASSED'}]]}

Querying the Neuroscout API
----------
----------
`pyNS` makes it easy query various endpoints of the Neuroscout API, such as ``datasets``:

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

Note that the valid arguments for each endpoint are listed in the official Neuroscout `API documentation <https://neuroscout.org/api/>`_.
For example, for `neuroscout.datasets.get`, this is the `reference for the valid arguments <https://neuroscout.org/api/swagger/#/dataset/get_api_datasets>`.

In the documentation, we can see that we the `name` argument can be used to find a specific dataset.

::

   >>> neuroscout.datasets.get(name='SherlockMerlin')
      {'active': True,
      'dataset_address': None,
      'description': {'Authors': ['Zadbood, A.',
         'Chen, J.',
         'Leong, Y.C.',
         'Norman, K.A.',
         'Hasson, U.'],
      'BIDSVersion': '1.0.2',
      'Funding': 'National Institutes of Health (1R01MH112357-01 and 1R01MH112566-01)',
      'Name': 'Sherlock_Merlin',
      'ReferencesAndLinks': ['https://academic.oup.com/cercor/article/doi/10.1093/cercor/bhx202/4080827/How-We-Transmit-Memories-to-Other-Brains']},
      'id': 5,
   ...
      'url': 'https://openneuro.org/datasets/ds001110'}

Syntactic sugar: pyNS makes using the Neuroscout API easier
----------
----------

Typically, to query the Neuroscout API you will need to refer to the `ids` of the objects you want to query.
For example, to discover the available predictors for `SherlockMerlin`, we would refer to the `id` of the dataset:

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


However, `pyNS` adds conveniences to make this easier.
For any argument ending in `_id` (such as `dataset_id`), you can simply use the name of the object, and `pyNS` will 
automatically look up the id for you and pass it to the API.

For example, perform the same query as above using `dataset_name`, and further restrict results
to a specific task as follows:

::

   >>> first = neuroscout.predictors.get(dataset_name='Sherlock_Merlin', task_name='MerlinMovie')[0]
   {'description': 'Bounding polygon around face. y coordinate for vertex 1',
    'extracted_feature': {'created_at': '2018-04-12 00:44:14.868349',
     'description': 'Bounding polygon around face. y coordinate for vertex 1',
     'extractor_name': 'GoogleVisionAPIFaceExtractor',
     'id': 102,
     'modality': None},
    'id': 197,
    'name': 'boundingPoly_vertex1_y',
    'source': 'extracted'}

.. note::
   This syntactic sugar is only available in `pyNS`, and not when accessing the `API` directly.
   For example, the official API documentation does not list `dataset_name` as a valid argument for
   `neuroscout.predictors.get`, and instead lists `dataset_id` as required.


Getting the data: querying `predictor_events`
----------
----------

An important aspect of `pyNS` is the ability to retrieve moment by moment events for specific predictors.

For example, we can chain the previous query with a query to `predictor_events` to get the events for the first predictor:

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

Tutorial
--------

For a full fledged tutorial see this `Jupyter Notebook <https://github.com/neuroscout/pyNS/blob/master/examples/Tutorial.ipynb>`_.

For a complete example, including meta-analytic workflows, see the the Neuroscout Paper `Jupyter Book <https://neuroscout.github.io/neuroscout-paper/intro.html>`_.
