""" High-level utilities for fetching predictors from Neuroscout API """
import math
import pandas as pd
from bids.variables import SparseRunVariable, BIDSRunVariableCollection
from bids.variables.entities import RunInfo
from pyns import Neuroscout


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
        collection = collection.sort_values(['subject', 'session', 'run', 'acquisition', 'onset'])

    return collection