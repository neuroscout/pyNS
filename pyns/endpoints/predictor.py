"""Predictor endpoint"""
from .base import Base
import json

class Predictors(Base):
    """Predictors endpoint
    
    auto_methods: `get`, `post`
    """
    _base_path_ = 'predictors'
    _auto_methods_ = ('get', 'post')
    _find_runs_ = True

    def create_collection(self, collection_name, dataset_id,
                          runs, event_files, descriptions=None):
        """ Create new predictor collection
        
        :param collection_name: Collection name.
        :type collection_name: str
        :param dataset_id: Dataset id.
        :type dataset_id: int
        :param runs: List of lists of run ids corresponding to each event_file.
        :type runs: list
        :param event_files: List of TSV files with new predictor columns.
            Required columns: onset, duration, any number of columns 
            with values for new Predictors.
        :type event_files: list
        :param descriptions: list of dictionaries, where each dict matches to 
            a tsv file, and keys in the dict correspond to columns in the event
            file. Values are strings with a verbal description of each column. 
        :type descriptions: list

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        files = tuple([('event_files', open(f, 'rb')) for f in event_files])
        runs = [",".join([str(r) for r in s]) for s in runs]
        descriptions = json.dumps(descriptions)
        return self.post('collection', dataset_id=dataset_id, files=files,
                         runs=runs, collection_name=collection_name,
                         descriptions=descriptions)

    def get_collection(self, collection_id):
        """ Get predictor collection
        
        :param collection_id: Collection ID
        :type collection_id: int
        
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.get(f'collection/{collection_id}')


class PredictorEvents(Base):
    _base_path_ = 'predictor-events'
    _auto_methods_ = ('get', )
    _convert_names_to_ids_ = True
    _find_runs_ = True
