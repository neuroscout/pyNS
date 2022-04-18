"""Predictor endpoint"""
from .base import Base
import json


class Predictors(Base):
    """Predictors endpoint
    
    auto_methods: `get`, `post`
    """
    _base_path_ = 'predictors'
    _auto_methods_ = ('get', 'post')

    def create_collection(self, collection_name, dataset_id,
                          runs, event_files, descriptions=None):
        """ Create new predictor collection
        
        :param collection_name: Force upload with unique timestamped name.
        :type collection_name: str
        :param dataset_id: Dataset id.
        :type dataset_id: int
        :param runs: List of run ids corresponding to files
        :type runs: list
        :param event_files: List of TSV files with new predictor columns.
            Required columns: onset, duration, any number of columns 
            with values for new Predictors.
        :type event_files: list
        :param descriptions: list of descriptions (dict)
            for each column
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
