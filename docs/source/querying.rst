Querying
=====

---------------------------
Querying the Neuroscout API
---------------------------

.. testsetup::

   from pyns import Neuroscout
   neuroscout = Neuroscout()

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

---------------------------------------------------------------
Human friendly queries: Automatic conversion of _name to _id
---------------------------------------------------------------

pyNS adds several conveniences to the Neuroscout API to make querying easier.

Typically, when querying the Neuroscout API you will need to refer to the `ids` of the objects you want to query.
For example, to discover the runs associated with `SherlockMerlin`, we would refer to the `id` of this dataset, 
which requires first looking up the dataset by name (``neuroscout.datasets.get(name='SherlockMerlin')``) and then
using the `dataset_id`` query for `runs` available:

.. doctest::

   >>> neuroscout.runs.get(dataset_id=5)[0] # First run of SherlockMerlin
   {'acquisition': None, 'dataset_id': 5, 'duration': 1453.5, 'id': 1428, 'number': None, 'session': None, 'subject': '17', 'task': 45, 'task_name': 'SherlockMovie'}

To make this query easier, `pyNS` automatically converts all arguments ending in `_name` to `_id`, by looking up the corresponding `id` 
in the Neuroscout API prior to making the subsequent API call. 

For example, we can ask for the first run for the dataset `NaturalisticNeuroimagingDatabase`, for the task `500daysofsummer` by name:

.. doctest::

   >>> neuroscout.runs.get(dataset_name='NaturalisticNeuroimagingDatabase', task_name='500daysofsummer')[0]
   {'acquisition': None, 'dataset_id': 28, 'duration': 5470.0, 'id': 1581, 'number': None, 'session': None, 'subject': '18', 'task': 50, 'task_name': '500daysofsummer'}

.. note::
   These conveniences are available in `pyNS`, and not when accessing the `API` directly.
   For example, the official API documentation does not list `dataset_name` as a valid argument for
   `neuroscout.datasets.get`, and instead lists `dataset_id` as required.

----------------------------------------------------
Looking up Predictors by run_id, and by run entities
----------------------------------------------------

Neuroscout provides a large number of pre-extracted `Predictors` all tasks and datasets.
It's important to note that the `Predictors` are always associated with `run_ids` rather than tasks or session directly, to enable maximum experimental design flexibility.
This means that when looking up `Predictors`, we must refer to one or more `run_ids`. 

For example, here's we can ask for an arbitrary `Predictor` associated with for the first run of `500daysofsummer` by referencing the `run_id`:

.. doctest::

   >>> neuroscout.predictors.get(run_id=1581)[0]
   {'dataset_id': 28, 'description': 'Degree of blur/sharpness of the image', 'extracted_feature': {'created_at': '2021-05-05 00:52:59.856713', 'description': 'Degree of blur/sharpness of the image', 'extractor_name': 'SharpnessExtractor', 'id': 425739, 'modality': 'image', 'resample_frequency': None}, 'id': 40254, 'max': 1.0, 'mean': 0.8604099357979763, 'min': 0.0, 'name': 'sharpness', 'num_na': 0, 'private': False, 'source': 'extracted'}


pyNS makes this query easier by allowing the user to instead pass `run` identifiers directly, and automatically converting them to `run_ids`.
For example, we can ask for a list of all `Predictors` associated with the the task `500daysofsummer` directly:

.. doctest::

   >>> predictors = neuroscout.predictors.get(dataset_name='NaturalisticNeuroimagingDatabase', task_name='500daysofsummer')
   >>> [p['name'] for p in predictors][0:5] # Print first 5 predictor names
   ['sharpness', 'tool', 'subtlexusfrequency_FREQcount', 'subtlexusfrequency_CDcount', 'subtlexusfrequency_FREQlow']


Under the hood, `pyNS` looks up the `dataset_id` and `task_id` for the given `dataset_name` and `task_name` and then uses these to lookup the `run_id` for the given `run`.

---------------------------------------------
Getting the data: querying `predictor_events`
---------------------------------------------

An important aspect of `pyNS` is the ability to retrieve moment by moment events for specific predictors.

The simplest way is to simply use `predictor_id` to query for a specific Predictor, for a specific `run_id`:

.. doctest::

   >>> neuroscout.predictor_events.get(predictor_id=40254, run_id=1581)[0:2]  # First two events for Predictor
   [{'duration': 1.0, 'onset': 0.0, 'predictor_id': 40254, 'run_id': 1581, 'value': '0.03137254901960784'}, {'duration': 1.0, 'onset': 1.0, 'predictor_id': 40254, 'run_id': 1581, 'value': '0.0196078431372549'}]

However, as before, we can make this simpler by taking advantage of pyNS's convenience features, and querying using the names directly.
Let's try looking up a `Predictor` named `speech` for the task `MerlinMovie`:

.. doctest::

   >>> neuroscout.predictor_events.get(predictor_name='speech', dataset_name='SherlockMerlin', task_name='MerlinMovie')[0:2]
   [{'duration': 0.30100000000000016, 'onset': 72.422, 'predictor_id': 12725, 'run_id': 134, 'value': '1'}, {'duration': 0.30100000000000016, 'onset': 72.422, 'predictor_id': 12725, 'run_id': 117, 'value': '1'}]

.. note::
   `PredictorEvents` are primarily associated with `run_id` to allow for maximum design flexibility, such as each subject seeing a different stimulus.
   As such, the above results will contain all event timepoints for all subjects/runs for that Predictor.
   However, in many cases all subjects will have seen the same movie, in which case you can simply use the events for a single subject as reference.


------------------------------------------
Friendly outputs to pandas DataFrames
------------------------------------------

You can easily convert any query result to a pandas DataFrame. Simply pass the argument `output_type='df'` to the query.
This is particularly useful for `PredictorEvents`, as the are naturally represented as a pandas DataFrame`.

::

   >>> neuroscout.predictor_events.get(predictor_name='speech', dataset_name='Sherlock_Merlin', task_name='MerlinMovie')

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

.. note::
   Asking for PredictorEvents for a dataset or task without specifying a `predictor_name` may results in a very long running query.