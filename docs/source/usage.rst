Usage
=====

----------
Quickstart
----------

.. testsetup::

   from pyns import Neuroscout
   neuroscout = Neuroscout()

First, instantiate a Neuroscout API Client object, optionally passing in your authentication credentials:

.. doctest::
   
   >> from pyns import Neuroscout
   >> neuroscout = Neuroscout()

The ```Neuroscout`` object provides a connection the Neuroscout API, with each major endpoint represented as 
an object linked to the main ``Neuroscout`` object. 

For example, using the attribute `neuroscout.datasets`, we can query the Neuroscout API for a list of datasets.

.. doctest::

   >>> datasets = neuroscout.datasets.get()
   >>> len(datasets) # Number of datasets available
   12
   >>> datasets[0]['name'] # Name of the first Dataset
   'Raiders'


The available Neuroscout endpoints are listed here: :meth:`mymodule.MyClass.mymethod`, and currently include:
`['analyses', 'datasets', 'tasks', 'runs', 'predictors', 'predictor_events', 'user']`

Query parameters
================

For each of the available endpoints, the Neuroscout API provides a number of query parameters. 

The valid arguments for each endpoint are listed in the official Neuroscout `API documentation <https://neuroscout.org/api/>`_.

In the documentation, we can see that we the `name` argument can be used to find a specific dataset.

.. doctest::

   >>> dataset = neuroscout.datasets.get(name='SherlockMerlin')[0]
   >>> dataset['name']
   'SherlockMerlin'
   >>> dataset['id']
   5
   >>> dataset['long_description']
   'This dataset includes the data of 18 particpants who watched Sherlock movie and data of 18 participants who watched Merlin movie.'


------------------------------------------------------------
Human friendly queries: Automatic conversion of _name to _id
------------------------------------------------------------

Typically, to query the Neuroscout API you will need to refer to the `ids` of the objects you want to query.
For example, to discover the runs associated with `SherlockMerlin`, we would refer to the `id` of this dataset, 
which requires first looking up the dataset by name (``neuroscout.datasets.get(name='SherlockMerlin')``) and then
using the dataset's ID to complete the `runs` query:

.. doctest::

   >>> neuroscout.runs.get(dataset_id=5)[0] # First run of SherlockMerlin
   {'acquisition': None, 'dataset_id': 5, 'duration': 1453.5, 'id': 1428, 'number': None, 'session': None, 'subject': '17', 'task': 45, 'task_name': 'SherlockMovie'}

To make this query easier, `pyNS` automatically converts all arguments ending in `_name` to `_id`, by looking up the corresponding `id` 
in the Neuroscout API prior to making the subsequent API call. 

For example, we can ask for the first run for the dataset `NaturalisticNeuroimagingDatabase`, for the task `500daysofsummer` by name:


.. doctest::

   >>> neuroscout.runs.get(dataset_name='NaturalisticNeuroimagingDatabase', task_name='500daysofsummer')[0]
   {'acquisition': None, 'dataset_id': 28, 'duration': 5470.0, 'id': 1581, 'number': None, 'session': None, 'subject': '18', 'task': 50, 'task_name': '500daysofsummer'}


However, `pyNS` adds conveniences to make this easier.
For any argument ending in `_id` (such as `dataset_id`), you can simply use the name of the object, and `pyNS` will 
automatically look up the id for you and pass it to the API.

For example, perform the same query as above using `dataset_name`, and further restrict results
to a specific task as follows:

::

   >>> first = neuroscout.predictors.get(dataset_name='SherlockMerlin', task_name='MerlinMovie')[0]
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

---------------------------------------------
Getting the data: querying `predictor_events`
---------------------------------------------

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

We can also take advantage of the `pyNS` syntactic sugar to query for the events for the first predictor:

::

   >>> neuroscout.predictor_events.get(predictor_name='speech', dataset_name='Sherlock_Merlin', task_name='MerlinMovie')[0:2]
   [{'duration': 0.30100000000000016,
   'onset': 72.422,
   'predictor_id': 12725,
   'run_id': 134,
   'value': '1'},
   {'duration': 0.30100000000000016,
   'onset': 72.422,
   'predictor_id': 12725,
   'run_id': 117,
   'value': '1'}]


------------------------------------------
Automatic conversion to pandas DataFrames
------------------------------------------

You can easily convert any query result to a pandas DataFrame. Simply pass the argument output_type='df' to the query:

::

   >>> neuroscout.predictor_events.get(predictor_id=first['id'])[0:2]

            duration    onset  predictor_id  run_id value predictor_name subject session number acquisition
      0         0.301   72.422         12725     134     1         speech      36    None   None        None
      1         0.301   72.422         12725     117     1         speech      19    None   None        None
      2         0.301   72.422         12725     118     1         speech      20    None   None        None
      3         0.301   72.422         12725     119     1         speech      21    None   None        None
      4         0.301   72.422         12725     120     1         speech      22    None   None        None
      ...         ...      ...           ...     ...   ...            ...     ...     ...    ...         ...
      25735     0.371  793.302         12725    1410     1         speech      25    None   None        None
      25736     0.280  793.673         12725    1410     1         speech      25    None   None        None
      25737     0.380  794.883         12725    1410     1         speech      25    None   None        None
      25738     0.180  796.358         12725    1410     1         speech      25    None   None        None
      25739     0.549  796.648         12725    1410     1         speech      25    None   None        None

      [25740 rows x 10 columns]

To make the interpretation of the query easier, `pyNS` automatically converts all columns ending in `_id` to their respective names.
In the case of `run_id`, we fetch the corresponding BIDS entities (i.e.`subject`, `number`, `session`, `acquisition`) and add them to the DataFrame.

--------
Tutorial
--------

For a full fledged tutorial see this `Jupyter Notebook <https://github.com/neuroscout/pyNS/blob/master/examples/Tutorial.ipynb>`_.

For a complete example, including meta-analytic workflows, see the the Neuroscout Paper `Jupyter Book <https://neuroscout.github.io/neuroscout-paper/intro.html>`_.
