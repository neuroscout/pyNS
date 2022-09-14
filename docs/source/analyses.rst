Creating analyses
=================

Another major use of `pyNS` is to create `Neuroscout` analyses programatically.

This is particulary useful for users that want to create a large number of analyses, or specify a
BIDS Stats Model that is not currently supported by the Neuroscout frontend web application.

.. note::
   To update analyses, you must be authenticated and be the owner of a particular analysis

.. testsetup::

   from pyns import Neuroscout
   neuroscout = Neuroscout()
   my_analysis = neuroscout.analyses.get_analysis('52546')


----------------------
Querying for Analyses
----------------------

First, as before, you can use `pyNS` to query and look up existing any existing public analyses.

For example, we can find two arbitrary analyses named `brightness` by name:

.. doctest::

   >>> neuroscout.analyses.get(name='speech')[-1]
   {'dataset_id': 30, 'description': None, 'hash_id': '52546', 'modified_at': '2021-10-07T21:1', 'name': 'speech', 'nv_count': 0, 'status': 'PASSED', 'user': 'adelavega'}


----------------------
The Analysis object
----------------------

To make it easier to work with the analyses, `pyNS` provides a special `Analysis` which represents a single Neuroscout analysis
as a Python object. To create this object, you can use :meth:`pyns.endpoints.analyses.get_analysis` to create an object from an Analysis' ``hash_id``

This `Analysis` object has all the attributes of an analysis as class attributes that can be modified and updated.

.. doctest::

    >> my_analysis = neuroscout.analyses.get_analysis('52546')
    >> my_analysis.hash_id
    '52546'
    >> my_analysis.predictors
    [40344,
    40345,
    40346,
    40347,
    40348,
    40349,
    40995,
    40999,
    41003,
    41007,
    41011,
    41015,
    42227]
    >> my_analysis.user
    'adelavega'


----------------------
Modifying analyses
----------------------

Assuming you are the owner of an analysis--and the analysis is still editable--you can modify it using the `Analysis` object.
Simply modify the attributes of the :class:`pyns.endpoints.Analysis` object and then call `Analysis.push()` to push the changes to the server


::
    
   >>> my_analysis.predictors = [40344] # remove all other predictors
   >>> my_analysis.push()
   >>> my_analysis.pull() # pull the updated analysis from the server
   >>> my_analysis.predictors
   [40344]


.. note::
   If you have compiled the analysis, it can no longer be modified


----------------------
Creating new analyses
----------------------

You can use the :meth:`pyns.endpoints.analyses.create_analysis` function to create a new :class:`pyns.endpoints.Analysis` object corresponding to a new analysis you just created.
This function makes it easy to create an analysis, by allowing you to specify your predictors, dataset, and other attributes
of the analysis by name.

::

    >>> analysis = neuroscout.analyses.create_analysis(
    dataset_name='Life', name='My new analysis!',
    predictor_names=['rmse', 'FramewiseDisplacement'],
    hrf_variables=['rmse'], 
    subject=['rid000001', 'rid000005']
    )

---------------------------
Uploading custom predictors
---------------------------

It is possible to upload custom predictors using :meth:`neuroscout.predictors.create_collection`. Features should be in BIDS-compliant events format. Two columns are mandatory: “onset” and “duration” (both in seconds). You can then include any number of novel predictors as additional columns. Missing values can be annotated using the value “n/a” (no quotes).

For each events file that you upload, you will be asked to associate it with runs in the respective dataset. Typically, there will be a different event file for each run in a naturalistic dataset. You must then associate each file with subjects. For example, in most cases, all subjects will have seen the same stimulus, but this will vary across datasets.

::

      >>> raiders1 = neuroscout.runs.get(dataset_id=10,number=1)[0:3] # 3 runs from raiders part 1
      >>> raiders2 = neuroscout.runs.get(dataset_id=10,number=2)[0:3] # 3 runs from raiders part 2
      >>> runs = [ [p['id'] for p in raiders1], [p['id'] for p in raiders2] ]
      >>> runs
      [[328, 344, 336], [331, 323, 355]]
      >>> event_files = ['food_raiders1.tsv', 'food_raiders2.tsv']
      >>> descriptions = {
          "grapes": "instances of grapes manually coded",
          "apples": "instances of apples manually coded",
          "bananas": "instances of bananas manually coded"}
      >>> neuroscout.predictors.create_collection(collection_name="raiders food",\
                                              dataset_id=11, \
                                              runs=runs, \
                                              event_files=event_files, \
                                              descriptions = descriptions)

--------
Tutorial
--------

For a complete guide on using pyNS, and in particular creating and updating ``Analysis``, see this `Jupyter Notebook <https://github.com/neuroscout/pyNS/blob/master/examples/Tutorial.ipynb>`_.

For a complete example, including meta-analytic workflows, see the the Neuroscout Paper `Jupyter Book <https://neuroscout.github.io/neuroscout-paper/intro.html>`_.
