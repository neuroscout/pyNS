"""Base endpoint class"""
from abc import ABC, abstractmethod
from functools import partial
import pandas as pd
from functools import wraps
import pyns
import warnings

class Base(ABC):
    """Superclass for all resources.
    
    All classes that inherent this can automatically have
    `get`, `post`, `put`, and `delete` methods associated 
    with them, if they are compatible with that endpoint. 
    
    These are listed in subclasses as `auto_methods`.
    """

    _convert_names_to_ids_ = False
    _find_runs_ = False
    _auto_methods_ = ()

    def __init__(self, client):
        """Initialize a Model instance.

        :param client: base client instance
        :type client: :class:`.Neuroscout`
        """
        self._client = client

        all_methods = ('get', 'post', 'put', 'delete')
        assert set(self._auto_methods_) <= set(all_methods)

        for method in self._auto_methods_:
            setattr(self,
                    method,
                    partial(
                        getattr(self._client, "_" + method),
                        self._base_path_)
            )
            # Add decorators to get types
            if method == 'get': 
                setattr(self,
                        method,
                        to_df(getattr(self, method))
                        )
                if self._convert_names_to_ids_ is True:
                    setattr(self,
                            method,
                            names_to_ids(getattr(self, method))
                    )
                if self._find_runs_ is True:
                    setattr(self,
                            method,
                            find_runs(getattr(self, method))
                    ) 
    @property
    @abstractmethod
    def _base_path_(self):
        pass

    @property
    @abstractmethod
    def _auto_methods_(self):
        """ HTTP methods to auto create in subordinate classes """
        pass


def names_to_ids(func):
    ''' Decorator which converts *_name to *_id by automatically looking up in API'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        api = pyns.Neuroscout()
        # Sorting guarantees that 'dataset' is looked up before 'task' and 'predictor' to constrain search
        for kw in sorted(kwargs):
            if kw.endswith('_name'):
                try:
                    mod = getattr(api, kw.replace('_name', 's'))
                except:
                    raise ValueError("No API endpoint for {}".format(kw))

                filter_args = {'name': kwargs[kw]}
                if kw == 'task_name' and 'dataset_id' in kwargs:
                    filter_args['dataset_id'] = kwargs['dataset_id']

                if kw == 'predictor_name' and 'run_id' in kwargs: 
                    filter_args['run_id'] = kwargs['run_id']
                
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


def _id_to_entities(df):
    """ Given a column of ids, return a column of names, or in the case of
    run_id, a column of dataset_name, task_name, and predictor_name """
    api = pyns.Neuroscout()
    for col in df.columns:
        if col.endswith('_id'):
            try:
                endpoint = getattr(api, col.replace('_id', 's'))
            except:
                warnings.warn(f"No API endpoint for {col}, could not convert")
                
            if col == 'run_id':
                ents = ['subject', 'session', 'number', 'acquisition']
                entities = {
                    'subject': {},
                    'session': {},
                    'number': {},
                    'acquisition': {}
                }
                for r in df[col].unique():
                    res = endpoint.get(r)
                    for e in entities:
                        entities[e][r] = res[e]

                for e, mapping in entities.items():
                    df[e] = df[col].map(mapping)        
            else:
                names = {
                    r: endpoint.get(r)['name'] 
                    for r in df[col].unique()
                    }
                df[col.replace('_id', '_name')] = df[col].map(names)
    return df

def to_df(func):
    """ Adds automatic conversion to pandas dataframe """
    @wraps(func)
    def wrapper(*args, output_type='json', **kwargs):
        if output_type not in ['df', 'json']:
            raise ValueError("Invalid output type")
        res = func(*args, **kwargs)

        if output_type == 'df':
            if isinstance(res, list):
                res = _id_to_entities(pd.DataFrame(res))
            else:
                raise ValueError("Cannot convert to dataframe")
        return res
    return wrapper