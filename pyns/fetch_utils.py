""" High-level utilities for fetching predictors from Neuroscout API """
import math
import warnings
import pandas as pd
from bids.variables import SparseRunVariable, BIDSRunVariableCollection
from bids.variables.entities import RunInfo
from pyns import Neuroscout
from datalad.api import install, get
from pathlib import Path

def fetch_neuroscout_predictors(predictor_names, dataset_name, return_type='df', resample=True, api=None, **entities):
    """ Fetch predictors from Neuroscout API, and return as a BIDSRunVariableCollection or pandas DataFrame

    Parameters
    ----------
    predictor_names : str
        Name of predictors to fetch
    dataset_name : str
        Name of dataset to fetch predictors from
    return_type : str
        Either 'df' or 'BIDSRunVariableCollection'
    resample : bool
        Whether to resample predictors to TR
    api : pyns.Neuroscout
        Authenticated instance of Neuroscout API (if None, will create one)
    entities : dict
        Entities to filter by


    """
    if api is None:
        api = Neuroscout()

    # Fetch from API
    all_df = api.predictor_events.get(
        predictor_name=predictor_names, dataset_name=dataset_name, output_type='df', **entities)
    all_df = all_df.rename(columns={'number': 'run', 'value': 'amplitude'})
    
    # Get run-level metadata
    all_run_info = {}
    for run_id in all_df.run_id.unique():
        resp = api.runs.get(run_id)
        ri = {
            'duration': resp['duration'],
            'tr': api.tasks.get(resp['task'])['TR'],
            'image': None
        }
        
        # TODO: Fetch real number of volumes, or allowing passing it in
        ri['n_vols'] = math.ceil(ri['duration'] / ri['tr'])
        all_run_info[run_id] = ri
        
    # Create BIDSRunVariableCollection
    variables = []
    for (run_id, predictor_names), df in all_df.groupby(['run_id', 'predictor_name']):
        # Determine entities / run info
        keep_cols = []
        entities = {}
        for j in ['subject', 'session', 'run', 'acquisition', 'run_id']:
            val = df[j].iloc[0]
            if val:
                entities[j] = val
                keep_cols.append(j)
        run_info = RunInfo(**all_run_info[run_id], entities=entities)

        try:
            df['amplitude'] = pd.to_numeric(df['amplitude'])
        except ValueError:
            pass
        
        df = df[['onset', 'duration', 'amplitude'] + keep_cols].sort_values('onset')
        variables.append(SparseRunVariable(
            predictor_names, df, run_info, 'events'))
            
    collection = BIDSRunVariableCollection(variables=variables)

    if resample:
        collection = collection.to_dense().resample('TR')

    if return_type == 'df':
        collection = collection.to_df()
        sort_keys = [a for a in ['subject', 'session', 'run', 'acquisition', 'onset'] if a in collection.columns]
        collection = collection.sort_values(sort_keys)

    return collection


def get_paths(preproc_dir, fetch_json=False, subjects=None, runs=None, tasks=None):
    """ Get paths to preprocessed images in a Neuroscout dataset.
    Args:
        preproc_dir (str): Path to preprocessed dataset
        fetch_json (bool): Whether to fetch JSON metadata files
        subjects (list or str): List of subjects to fetch
        runs (list or str): List of runs to fetch
        tasks (list or str): List of tasks to fetch
    
    Returns:
        paths: List of paths to images
    """
    preproc_dir = Path(preproc_dir)
    paths = []
    

    if tasks is None:
        tasks = ''
    if not isinstance(tasks, list):
        tasks = [tasks]
    tasks = [f'task-{t}*' for t in tasks]
    
    if not subjects:
        subjects = '*'
    if not isinstance(subjects, list):
        subjects = [subjects]
    
    if not runs:
        runs = ''
    if not isinstance(runs, list):
        runs = [runs]
        
    run_p = [f'run-{r}*'  if r else r for r in runs]
    run_p += [f'run-{str(r).zfill(2)}*' if r else r for r in runs]
    runs = list(set(run_p))
    
    for sub in subjects:
        for run in runs:
            for task in tasks:
                pre =  f'sub-{sub}/**/func/*{task}{run}space-MNI152NLin2009cAsym*'
                paths += list(preproc_dir.glob(pre + 'preproc*.nii.gz'))
                paths += list(preproc_dir.glob(pre + 'brain_mask.nii.gz'))

    if not paths:
        raise Exception("No images suitable for download.")
    
    if fetch_json:
        # Get all JSON files in Dataset just in case
        paths += list(preproc_dir.rglob('*.json'))
    
    # Check for correctness:
    errors = [1 if not p.is_symlink() else 0 for p in paths]
    if sum(errors) > 0:
        warnings.warn("Error computing image paths. Attempt fetch anyways.")
    
    return paths

def install_dataset(dataset_dir, preproc_address, no_get=False):
    """ Install a Neuroscout dataset using DataLad.
    Args:
        dataset_dir (str): Path to install dataset
        preproc_address (str): URL to install dataset from
        no_get (bool): Whether to skip installation (i.e. dry run)

    Returns:
        preproc_dir (str): Path to preprocessed folder (i.e. fmriprep or preproc)
    """
    dataset_dir = Path(dataset_dir)
    # Install DataLad dataset if dataset_dir does not exist
    if not dataset_dir.exists() and not no_get:
        # Use datalad to install the preproc dataset
        install(source=preproc_address,
                path=str(dataset_dir))

    for option in ['preproc', 'fmriprep']:
        if (dataset_dir / option).exists():
            preproc_dir = (dataset_dir / option).absolute()
            break
    else:
        preproc_dir = dataset_dir
        
    return preproc_dir


def fetch_preproc(dataset_name, data_dir, no_get=False, datalad_jobs=-1, **filters):
    """ Fetch preprocessed images from a Neuroscout dataset.
    Installs dataset using DataLad if not already installed.
    
    Args:
        dataset_name (str): Name of dataset to fetch
        data_dir (str): Path to datasets directories. Dataset will be installed
            in data_dir / dataset_name if not already installed.
        no_get (bool): Whether to skip fetching (i.e. dry run)
        datalad_jobs (int): Number of jobs to use for DataLad download
        **filters: Additional filters to pass to get_paths (e.g. subjects, runs, tasks)

    Returns:
        paths (Path object): List of paths to images 
    
    Examples:
        >>> from pyns.fetch_utils import fetch_preproc
        >>> paths = fetch_preproc('Budapest', '/data/neuroscout', subjects='sid000005', runs=[1, 2])
        >>> paths
        [PosixPath('/data/neuroscout/Budapest/fmriprep/sub-sid000005/func/sub-sid000005_task-movie_run-1_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'),
        ...
        ]
    """
    api = Neuroscout()
    preproc_address = api.datasets.get(name=dataset_name)[0]['preproc_address']
    data_dir = Path(data_dir)
    dataset_dir = data_dir / dataset_name
    
    preproc_dir = install_dataset(dataset_dir, preproc_address, no_get=no_get)
    
    paths = get_paths(preproc_dir, **filters)
    
    try:
        # Get with DataLad
        if not no_get:
            get([str(p) for p in paths], dataset=dataset_dir, jobs=datalad_jobs)

    except Exception as exp:
        if hasattr(exp, 'failed'):
            message = exp.failed[0]['message']
            raise ValueError("Datalad failed. Reason: {}".format(message))
        else:
            raise exp
            
    return paths