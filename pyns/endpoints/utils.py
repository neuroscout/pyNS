""" Miscelaneous utilities """
import collections
import warnings
from functools import wraps
import pyns

module_names = {}
Dependency = collections.namedtuple('Dependency', 'package value')


def attempt_to_import(dependency, name=None, fromlist=None):
    """ Attempt to import dependency """
    if name is None:
        name = dependency
    try:
        mod = __import__(dependency, fromlist=fromlist)
    except ImportError:
        mod = None
    module_names[name] = Dependency(dependency, mod)
    return mod


def build_model(name, variables, tasks, subjects, runs=None, session=None,
                hrf_variables=None, transformations=None,
                contrasts=None, dummy_contrasts=True):
    """ Builds a basic two level BIDS-Stats model """
    hrf_variables = hrf_variables or []
    transformations = transformations or []
    contrasts = contrasts or []

    if not set(variables) >= set(hrf_variables):
        raise ValueError("HRF Variables must be a subset of all variables")

    if hrf_variables:
        transformations.append({
            "Input": hrf_variables,
            "Name": "Convolve"
        })

    model = {
        "Steps": [
          {
            "DummyContrasts": {"Type": "t"},
            "Contrasts": contrasts,
            "Level": "Run",
            "Model": {
              "X": variables
            },
            "Transformations": transformations
          }
        ],
        "Input": {
          "Subject": subjects,
          "Task": tasks
        },
        "Name": name,
    }

    model['Steps'].append(
        {
            "DummyContrasts": {"Type": "FEMA"},
            "Level": "Subject"
        }
    )

    model['Steps'].append(
        {
            "DummyContrasts": {"Type": "t"},
            "Level": "Dataset"
        }
    )

    if not dummy_contrasts:
        model['Steps'][0].pop('DummyContrasts')

    if dummy_contrasts == 'hrf' and hrf_variables:
        model['Steps'][0]['DummyContrasts']['Conditions'] = hrf_variables

    if runs is not None:
        model['Input']['Run'] = runs

    if session is not None:
        model['Input']['Session'] = session

    return model


def snake_to_camel(string):
    """ Convert string from snake to camel type """
    words = string.split('_')
    return words[0] + ''.join(word.title() for word in words[1:])


def dt_name_to_ids(func):
    ''' Decorator which converts dataset_name and task_name to ids. '''
    @wraps(func)
    def wrapper(*args, task_name=None, dataset_name=None, **kwargs):
        api = pyns.Neuroscout()
        dataset_id = None
        if dataset_name is not None:
            datasets = api.datasets.get() 
            ds_ids = [d['id'] for d in datasets if d['name']==dataset_name]
            if not ds_ids:
                raise ValueError(f"{dataset_name} is not a valid dataset name."
                                  "See all available datasets using"
                                  "Neuroscout().datasets.get()")
            kwargs['dataset_id'] = ds_ids[0]
        
        task_id = None
        if task_name is not None:
            tasks = api.tasks.get(dataset_id=dataset_id)
            task_ids = [t['id'] for t in tasks if t['name'] == task_name]
            if not task_ids:
                raise ValueError(f''' {task_name} is not a valid task name.''')
            kwargs['task_id'] = task_ids[0]
        
        return func(*args, **kwargs)
    
    return wrapper


def find_runs(func):
    """ Decorator which finds runs for a given dataset and task names.
    Assumes that downstream function accepts names instead of ids 
    (i.e. has been decorated with dt_name_to_ids)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api = pyns.Neuroscout()
        search_args = {}
        for i in ['dataset_name', 'task_name', 'subject', 'number', 'session']:
            if i in kwargs:
                search_args[i] = kwargs.pop(i)

        if 'run_ids' not in kwargs and search_args:
            runs = api.runs.get(**search_args)
            run_id = [r['id'] for r in runs]
            if not run_id:
                raise ValueError("No runs found using provided arguments")
            kwargs['run_id'] = run_id
        return func(*args, **kwargs)
    return wrapper