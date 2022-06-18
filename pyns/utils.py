
from .api import Neuroscout
import warnings

# TO DO:
# - Define general decorator mapping names -> ids for task, dataset, or predictor
# - Keep task & dataset information for functions taking run_id (e.g., predictor events)
# - For predictor_events.get, also return predictors information

DATASETS_WEB = 'https://neuroscout.org/datasets'

def find_runs(function):
    ''' Decorator which allows passing dataset_name or task_name
        instead of run_id to any function requiring run_id.
    '''
    def wrapper(*args, **kwargs):
        task_name = kwargs.pop('task_name') if 'task_name' in kwargs else None
        ds_name = kwargs.pop('dataset_name') if 'dataset_name' in kwargs else None
        if ds_name is None:
            raise ValueError(f''' dataset_name must be defined. 
                                  Find available datasets at:
                                  {DATASETS_WEB}''')
        else:
            datasets = Neuroscout().datasets.get() 
            ds_id = [d['id'] for d in datasets if d['name']==ds_name]
            if len(ds_id)==0:
                raise ValueError(f'''{dataset_name} is not a 
                                     valid dataset name.
                                     Check dataset names at 
                                     {DATASETS_WEB}''')
            ds_tasks = Neuroscout().tasks.get(dataset_id=ds_id[0])
            if task_name is not None:
                task_ids = [t['id'] for t in ds_tasks if t['name']==task_name]
                if len(task_ids)==0:
                    raise ValueError(f''' {task_name} is not a valid task name.
                                            Check task names at: 
                                            {DATASETS_WEB}/{ds_id[0]}''')
            else:
                task_ids = [t['id'] for t in ds_tasks]
        runs = Neuroscout().runs.get(task_id=task_ids)
        if 'subject' in kwargs:
            subjects = kwargs.pop('subjects')
            filtered_runs = []
            for s in subjects:
                subj_runs = [r for r in runs if r['subject']==s]
                if len(subj_runs)==0:
                    warnings.warn(f'''subject {s} not found''')
                filtered_runs += subj_runs 
            runs = filtered_runs
        run_id = [r['id'] for r in runs]
        function(*args, **kwargs, run_id=run_id)
    return wrapper
                


@find_runs
def get_predictors(run_id):
    # Use run id to find predictors
    pass

def get_predictor_events(run_id, predictor_id):
    pass