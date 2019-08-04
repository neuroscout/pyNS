"""Provides the Predictor related classes."""
from .base import Base
import json


class Predictors(Base):
    _base_path_ = 'predictors'
    _auto_methods_ = ('get', 'post')

    def create_collection(self, collection_name, dataset_id,
                          runs, event_files, descriptions=None):
        """ Create new predictor collection
        :param str collection_name: Force upload with unique timestamped name.
        :param int dataset_id: Dataset id.
        :param list(list((int)) runs: List of run ids corresponding to files
        :param list(str) event_files: TSV files with new predictor columns.
            Required columns: onset, duration,
            any number of columns with values for new Predictors.
        :param list(dict) descriptions: optional list of descriptions
                                        for each columns
        :return: JSON response
        """
        files = tuple([('event_files', open(f, 'rb')) for f in event_files])
        runs = [",".join([str(r) for r in s]) for s in runs]
        descriptions = json.dumps(descriptions)
        return self.post('collection', dataset_id=dataset_id, files=files,
                         runs=runs, collection_name=collection_name,
                         descriptions=descriptions)

    def get_collection(self, collection_id):
        return self.get('collection', collection_id=collection_id)


class PredictorEvents(Base):
    _base_path_ = 'predictor-events'
    _auto_methods_ = ('get', )
