pyNS: Neuroscout API client documentation
===================================

.. image:: neuroscout-logo.svg
  :width: 400
  :alt: Neuroscout Logo


**pyNS** is the Python client for the `Neuroscout API <https://neuroscout.org/api>`_, allowing users 
to programmatically query and interactive with the Neuroscout database. This allows users to
create analyses, query for analyses, and download analysis results.

**pyNS** provides a number of high-level functions for common tasks (that would typically require 
multiple API calls), such as creating and registering analyses, and fetching predictor and imaging data directly.

Advanced use cases include: batch-creation of analyses (e.g. for meta-analysis) and the
creation of custom analysis pipelines.

**pyNS** mirrors the official Neuroscout API with a Pythonic interface.
Note that the best reference for the API is the official `API docs <https://neuroscout.org/api>`_

See the :doc:`installation` and :doc:`quickstart` sections to get started.

.. note::

   If you're just starting out with Neuroscout, take a look at the main website
   (https://neuroscout.org), and the accompanying `documentation <https://neuroscout.github.io/neuroscout/>`_.

Contents
--------

.. toctree::

   installation
   quickstart
   querying
   analyses
   fetching
   api
