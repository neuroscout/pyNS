----------
Quickstart
----------

.. testsetup::

   from pyns import Neuroscout
   neuroscout = Neuroscout()

First, instantiate a :py:class:`pyns.Neuroscout` API Client object, optionally passing in your authentication credentials:

.. doctest::
   
   >> from pyns import Neuroscout
   >> neuroscout = Neuroscout(email='myemail@emal.com', password='mypassword')


.. note::
   Google single-sign-on is not currently supported in pyNS. Please register for a Neuroscout account if you 
   wish to use `pyNS` to create analyses.

The :py:class:`pyns.Neuroscout` object provides a connection to the Neuroscout API, with each major endpoint represented as 
an object linked to the main :py:class:`pyns.Neuroscout` object. 

For example, using the attribute `neuroscout.datasets`, we can query the Neuroscout API for a list of datasets.

.. doctest::

   >>> datasets = neuroscout.datasets.get()
   >>> len(datasets) # Number of datasets available
   12
   >>> datasets[0]['name'] # Name of the first Dataset
   'Raiders'


The available Neuroscout endpoints are listed here: :py:mod:`pyns.endpoints`, and currently include:
``['analyses', 'datasets', 'tasks', 'runs', 'predictors', 'predictor_events', 'user']``
