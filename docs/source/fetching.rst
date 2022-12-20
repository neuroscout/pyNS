Fetching predictors & images
=============================

To facilitate creating custom analysis workflows, `pyNS` provides a number of high-level utilities for fetching 
predictors from the Neuroscout API, and the corresponding images from the preprocessed BIDS dataset.

.. note::

    Analysis pipelines created using these utilities will not be centrally registered on Neuroscout, and 
    will not be available to other users by the Neuroscout API or web interface.

    If your analysis type is supported by `Neuroscout-CLI <https://neuroscout-cli.readthedocs.io/en/latest/>`_ 
    (e.g. summary statistics GLM), it is recommended to use the 
    web interface to create your analysis or the follow the guide for :doc:`analyses` using pyNS.

    If you use these data in a publication, please cite the following paper:
    
    Alejandro de la Vega, Roberta Rocca, Ross W Blair, Christopher J Markiewicz, Jeff Mentch, James D Kent, Peer Herholz, Satrajit S Ghosh, Russell A Poldrack, Tal Yarkoni (2022). *Neuroscout, a unified platform for generalizable and reproducible fMRI research*. eLife 11:e79277
    https://doi.org/10.7554/eLife.79277

    In addition, please cite the original dataset(s), and the predictor extractors you use.


--------------------------------------
Fetching & re-sampling predictor data
--------------------------------------

.. note::
    
    To learn about low-level utilities for fetching predictors, see the :doc:`querying` documentation.

The method :meth:`pyns.fetch_utils.fetch_predictors` can be used to fetch predictor data, 
resample it to the TR of the images, and return it as a pandas DataFrame.

You only need two things: a list of predictors, and the name of the BIDS dataset.
Optionally, you can also restrict the data to a subset of subjects, runs or tasks (reccomended for testing).

.. code-block:: python

    fetch_predictors(predictor_names=['speech', 'rms'], dataset_name='Budapest', 
        subject='sid000005', run=[1, 2]resample=True)


+----+------------+---------+-------+-----------+--------------+--------------+----------+
|    |   duration |   onset |   run | subject   |          rms |       speech |   run_id |
+====+============+=========+=======+===========+==============+==============+==========+
|  0 |          1 |       0 |     1 | sid000005 |  6.18876e-07 |  9.5801e-06  |     1433 |
+----+------------+---------+-------+-----------+--------------+--------------+----------+
|  2 |          1 |       1 |     1 | sid000005 | -1.49298e-06 | -2.57011e-05 |     1433 |
+----+------------+---------+-------+-----------+--------------+--------------+----------+
|  4 |          1 |       2 |     1 | sid000005 |  3.50004e-06 |  6.755e-05   |     1433 |
+----+------------+---------+-------+-----------+--------------+--------------+----------+
|  6 |          1 |       3 |     1 | sid000005 | -7.91888e-06 | -0.000173993 |     1433 |
+----+------------+---------+-------+-----------+--------------+--------------+----------+
|  8 |          1 |       4 |     1 | sid000005 |  1.70871e-05 |  0.000439006 |     1433 |
+----+------------+---------+-------+-----------+--------------+--------------+----------+

This will return a pandas DataFrame with the predictors resampled to the TR (in this case 0.33s) 
ith `onset` and `duration` columns. In addition, columns describing the entities identifying each columns
(e.g. which run, subject, etc...) are included as columns.

-----------------------------
Fetching preprocessed images
-----------------------------

.. note::
    
    Datalad is required to download images. See `DataLad documentation <https://handbook.datalad.org>`_
    for installation instructions.

The method :meth:`pyns.fetch_utils.fetch_images` facilitates downloading preprocessed images from the
Neuroscout datasets. It can be used to download images for a single subject, or for all subjects in a
dataset.

Simply provide a directory where Neuroscout datasets should be installed, and the dataset name.
Optionally, you can also restrict the data to a subset of subjects, runs or tasks (reccomended for testing).

.. code-block:: python
    
    preproc_dir, img_paths = fetch_images('Budapest', '/tmp/', subject=subject)
    img_paths[0]
    
    <BIDSImageFile filename='/tmp/Budapest/fmriprep/sub-sid000005/func/sub-sid000005_task-movie_run-1_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'>

:meth:`pyns.fetch_utils.fetch_images` installs the dataset using datalad, and returns the path to the 
preprocessed dataset, as well as a list of `BIDSImageFile` objects for each image.

The `BIDSImageFile` objects can be used to load the images into memory using `nibabel <https://nipy.org/nibabel/>`_, 
and can be used to extract metadata about the image, such as the associated entities:

.. code-block:: python

    target = img_paths[0]
    img = target.get_image()
    target.get_entities()
    
     {'datatype': 'func',
      'desc': 'preproc',
      'extension': '.nii.gz',
      'run': 1,
      'space': 'MNI152NLin2009cAsym',
      'subject': 'sid000005',
      'suffix': 'bold',
      'task': 'movie'}


Using these methods you can easily create custom analysis workflows. 