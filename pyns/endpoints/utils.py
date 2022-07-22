""" Miscelaneous utilities """
import collections
from os import kill
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


def names_to_ids(func):
    ''' Decorator which converts *_name to *_id by automatically looking up in API'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        api = pyns.Neuroscout()

        # Sorting guarantees that 'dataset' is looked up before 'task' to constrain search
        for kw in sorted(kwargs):
            if kw.endswith('_name'):
                try:
                    mod = getattr(api, kw.replace('_name', 's'))
                except:
                    raise ValueError("No API endpoint for {}".format(kw))

                filter_args = {'name': kwargs[kw]}
                if kw == 'task_name' and 'dataset_id' in kwargs:
                    filter_args['dataset_id'] = kwargs['dataset_id']

                res = mod.get(**filter_args)

                if not res:
                    raise ValueError("No {} found using provided arguments".format(kw))
                if len(res) > 1:
                    raise ValueError("Multiple {} found using provided arguments".format(kw))

                kwargs[kw.replace('_name', '_id')] = res[0]['id']
                kwargs.pop(kw)

        return func(*args, **kwargs)
    return wrapper


def find_runs(func):
    """ Decorator which finds runs for a given dataset and task names.
    Assumes that downstream function accepts names instead of ids 
    (i.e. has been decorated with names_to_ids)"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        api = pyns.Neuroscout()
        FIELDS = ['dataset_name', 'task_name', 'subject', 'number', 'session']
        search_args = {k: kwargs.pop(k) for k in FIELDS if k in kwargs}

        if 'run_ids' not in kwargs and search_args:
            kwargs['run_id'] = [r['id'] for r in api.runs.get(**search_args)]
            if not kwargs['run_id']:
                raise ValueError("No runs found using provided arguments")
        elif 'run_ids' in kwargs and search_args:
            raise ValueError(f"Run filter arguments {search_args} cannot be provided if run_ids are provided")
        return func(*args, **kwargs)
    return wrapper