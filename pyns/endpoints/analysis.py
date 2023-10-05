"""Analysis endpoint"""
from .base import Base
from pathlib import Path
from functools import partial
import datetime
import tempfile
import requests
from .utils import build_model, attempt_to_import
from .base import names_to_ids
import tqdm
import time
import re
import json

altair = attempt_to_import('altair')
nib = attempt_to_import('nibabel')
nilearn = attempt_to_import('nilearn.plotting')


TMP_DIR = Path(tempfile.mkdtemp())


class Analysis:
    """ Analysis interactive object.
    
    This class is represents a specific instance of a Neuroscout `Analysis` that is synced
    with the API. 
    
    `Analysis` values (e.g. `.model`, `.name`) are set as attributes of the instance, and kept in 
    sync with the API using the `push` and `pull` methods.
    
    Most methods avaiable to :class:`.Analyses` are aliased here.
    """
    _mutable_fields_ = ['dataset_id', 'description', 'name',  'predictions',
                        'model', 'predictors', 'private', 'runs']

    _aliased_methods_ = ['delete', 'get_bundle', 'compile', 'generate_report',
                         'get_report', 'upload_neurovault', 'get_uploads',
                         'load_uploads', 'plot_uploads',
                         'plot_report', 'get_design_matrix']

    def __init__(self, *, analyses, name, dataset_id, **kwargs):
        """ Initate a new Analysis object. Typically, this is done by
        :class:`.Analyses` `get_analysis` or `create_analysis` methods.
        
        :param analyses: Instantiated :class:`.Analyses` object
        :type analyses: :class:`.Analyses`
        :param name: Analysis name
        :type name: str
        :param dataset_id: Dataset ID
        :type dataset_id: int
        :param kwargs: kwargs to set as class attributes        
        :type kwargs: dict
        """
        self.name = name
        self.dataset_id = dataset_id
        self._analyses = analyses

        # Set up (invalid fields will also be set, but not pushed to API)
        for k, v in kwargs.items():
            setattr(self, k, v)

        # If no hash_id, create
        if not hasattr(self, 'hash_id'):
            self._fromdict(self._analyses.post(**self._asdict()))

        # Attach aliased methods
        for method in self._aliased_methods_:
            setattr(self,
                    method,
                    partial(
                        getattr(self._analyses, method),
                        self.hash_id)
                    )

    def __repr__(self):
        return "<:class:`Analysis`={} name={} dataset_id={}>".format(
            self.hash_id, self.name, self.dataset_id)

    def _asdict(self):
        """ Return dictionary representation of mutable fields """
        di = {}
        for field in self._mutable_fields_:
            if hasattr(self, field):
                di[field] = getattr(self, field)

        return di

    def _fromdict(self, di):
        """ Update field values from response """
        for k, v in di.items():
            setattr(self, k, v)

    def push(self):
        """ Push changes from to API, and sync with returned results"""
        self._fromdict(self._analyses.put(self.hash_id, **self._asdict()))

    def pull(self):
        """ Pull updates from API, overriding changes made locally """
        self._fromdict(self._analyses.get(self.hash_id))

    def _getter_wrapper(self, method, **kwargs):
        """ Get representation of analysis, sync and return """
        new = getattr(self._analyses, method)(self.hash_id, **kwargs)
        self._fromdict(new)
        return new

    def fill(self, partial=True, dryrun=False):
        """ Fill missing fields
        
        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param partial: Partial fill.
        :type partial: bool
        :param dryrun: Do not commit to database.
        :type dryrun: bool
        
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self._getter_wrapper('fill')

    def get_status(self):
        """ Get compilation status """
        return self._getter_wrapper('get_status')

    def get_resources(self):
        """ Get analysis resources """
        return self._getter_wrapper('get_resources')

    def get_full(self):
        """ Get full analysis representation """
        return self._getter_wrapper('get_full')

    @names_to_ids
    def clone(self, dataset_id=None):
        """ Clone current analysis. If dataset_id is provided, new run and
        predictor_ids will be filled for that dataset.
        
        :param dataset_id: Dataset ID
        :type dataset_id: int
        :type dataset_name: str

        :return: :class:`.Analysis` instance.
        :rype: :class:`.Analysis`
        """
        new = Analysis(
            analyses=self._analyses, **self._analyses.clone(self.hash_id))
        if dataset_id is not None:
            new.dataset_id = dataset_id
            new.runs = []
            new.predictors = []
            new.push()
            new.fill()
        return new


class Analyses(Base):
    """ Analyses endpoint class """
    _base_path_ = 'analyses'
    _auto_methods_ = ('get', 'post')
    _convert_names_to_ids_ = True

    def put(self, id, **kwargs):
        """ Put analysis

        :param id: :class:`Analysis` `hash_id`
        :type id: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self._client._put(self._base_path_, id=id, **kwargs)

    def delete(self, id):
        """ Delete analysis

        :param id: :class:`Analysis` `hash_id`
        :type id: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self._client._delete(self._base_path_, id=id)

    def get_bundle(self, id, filename=None):
        """ Get analysis  bundle

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param filename: Optional filename to save bundle to
        :type filename: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        bundle = self.get(id=id, sub_route='bundle')
        if filename is not None:
            if isinstance(filename, str):
                filename = Path(filename)
            with filename.open('wb') as f:
                f.write(bundle)
        else:
            return bundle

    def clone(self, id):
        """ Clone analysis

        :param id: :class:`Analysis` `hash_id`
        :type id: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.post(id=id, sub_route='clone')

    def create_analysis(self, *, name, dataset_name, predictor_names,
                        tasks=None, subjects=None, runs=None, session=None,
                        hrf_variables=None, contrasts=None,
                        dummy_contrasts=True, transformations=None, **kwargs):
        """ Analysis creation "wizard". Builds analysis with a pre-populated
        BIDS Stats Model. 

        :param name: analysis name
        :type name: str
        :param dataset_name: dataset name
        :type dataset_name: str
        :param predictor_names: predictor names to include in model
        :type predictor_names: list
        :param tasks: list of tasks to include
        :type tasks: list
        :param subjects: list of subject identifiers
        :type subjects: list
        :param runs: list of run ids
        :type runs: list
        :param session: session name
        :type session: str
        :param hrf_variables: subset of `predictor_names` to convolve with HRF
        :type hrf_variables: list
        :param contrasts: list of contrast dictionaries
        :type contrasts: list
        :param dummy_contrasts: subset of `predictor_names` to create dummy contrast for
        :type dummy_contrasts: list
        :param transformations: list of transformations
        :type transformations: list
        :param kwargs: arguments to pass to Analysis class
        :type kwargs: dict

        :return: Analysis object
        :rype: :class:`Analysis`
        """

        # Get dataset id
        datasets = self._client.datasets.get(active_only=False)
        dataset = [d for d in datasets if d['name'] == dataset_name]
        if len(dataset) != 1:
            raise ValueError(
                "Dataset name does not match any existing dataset.")
        else:
            dataset = dataset[0]

        # Get task name
        if tasks is not None:
            if not isinstance(tasks, list):
                tasks = [tasks]

            task_ids = []
            for task in tasks:
                search = [t for t in dataset['tasks'] if t['name'] == task]
                if len(search) != 1:
                    raise ValueError(
                        "Task name does not match any tasks in the dataset")
                task_ids.append(search[0]['id'])
        else:
            # All tasks
            tasks = [t['name'] for t in dataset['tasks']]
            task_ids = [t['id'] for t in dataset['tasks']]

        # Get Run IDs
        run_models = self._client.runs.get(
            dataset_id=dataset['id'], task_id=task_ids,
            subject=subjects, number=runs, session=session)

        if len(run_models) < 1:
            raise ValueError("No runs could be found with the given criterion")

        subjects = list(set(r['subject'] for r in run_models))
        runs = list(set(r['number'] for r in run_models if r['number']))
        runs = runs or None

        run_ids = [r['id'] for r in run_models]
        # Get Predictor IDs
        public_preds = self._client.predictors.get(
            run_id=run_ids, name=predictor_names, active_only=False)

        predictors = [p['id'] for p in public_preds]

        # If not all predictors found, search in user private predictors
        private_preds = set(predictor_names) - \
            set([p['name'] for p in public_preds])
        if private_preds:
            # Get Predictor IDs
            for pred in private_preds:
                predictors += [p['id']
                               for p in self._client.user.get_predictors(
                                   run_id=run_ids, name=pred)]

        if len(predictors) != len(predictor_names):
            raise ValueError(
                "Not all named predictors could be found for the "
                "specified runs.")

        # Build model
        if transformations:
            transformations = transformations.copy()
        model = build_model(
            name, predictor_names, tasks,
            subjects=subjects, runs=runs, session=session,
            hrf_variables=hrf_variables,
            transformations=transformations,
            contrasts=contrasts, dummy_contrasts=dummy_contrasts
            )

        analysis = Analysis(analyses=self, dataset_id=dataset['id'],
                            name=name, model=model, runs=run_ids,
                            predictors=predictors, **kwargs)

        return analysis

    def get_analysis(self, id):
        """ Convenience function to fetch and create Analysis object from
        a known analysis id
        
        :param id: :class:`Analysis` `hash_id`
        :type id: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return Analysis(analyses=self, **self.get(id=id))

    def compile(self, id, build=True):
        """ Submit analysis for complilation

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param build: Build pybids object and verify compilation
        :type build: bool

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.post(id=id, sub_route='compile', params=dict(build=build))

    def generate_report(self, id, run_id=None, sampling_rate=None, scale=False):
        """ Submit analysis for report generation

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param run_id: Optional run_id to constrain report.
        :type run_id: list
        :param sampling_rate: Sampling rate for design matrix
        :type sampling_rate: float
        :param scale: Scale design matrix.
        :type scale: bool
    
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.post(id=id, sub_route='report', 
                         params=dict(
                             run_id=run_id, sampling_rate=sampling_rate, scale=scale))

    def get_report(self, id, run_id=None, loop_wait=True):
        """ Get generated reports for analysis
        
        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param run_id: Optional run_id to constrain report.
        :type run_id: list
        :param loop_wait: Wait until report completes before returning response.
        :type loop_wait: bool
    
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        report = self.get(id=id, sub_route='report', run_id=run_id)
        if loop_wait:
            while report['status'] == 'PENDING':
                time.sleep(2)
                report = self.get(id=id, sub_route='report', run_id=run_id)

        return report

    def get_design_matrix(self, id, run_id=None,
                          loop_wait=True):
        """ Get report design_matrix

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param run_id: Optional run_id to constrain report.
        :type run_id: list
        :param loop_wait: Wait until report completes before returning response.
        :type loop_wait: bool
    
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        report = self.get_report(id=id, run_id=run_id, loop_wait=loop_wait)

        if report['status'] == 'OK':
            return report['result']['design_matrix']
        else:
            return None

    def plot_report(self, id, run_id=None, plot_type='design_matrix_plot',
                    loop_wait=True):
        """ Uses altair to plot design_matrix plot generated by report
        
        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param run_id: Optional run_id to constrain report.
        :type run_id: list
        :param plot_type: `design_matrix_plot` or `corr_matrix_plot`
        :type plot_type: str
        :param loop_wait: Wait until report completes before returning response.
        :type loop_wait: bool
    
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        if altair is None:
            raise ImportError("Altair is required to plot_reports")

        report = self.get_report(id=id, run_id=run_id, loop_wait=loop_wait)

        if report['status'] == 'OK':
            for p in report['result'][plot_type]:
                altair.display.vegalite(p)

        return None

    def upload_neurovault(self, id, validation_hash, subject_paths=None,
                          group_paths=None, collection_id=None, force=False,
                          cli_version=None, fmriprep_version=None,
                          estimator=None, n_subjects=None, cli_args=None):
        """ Submit analysis for report generation

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param str validation_hash: Validation hash string.
        :type id: str
        :param subject_paths: List of image paths.
        :type subject_paths: list
        :param group_paths: List of image paths.
        :type group_paths: list
        :param force: Force upload with unique timestamped name.
        :type force: bool
        :param cli_version: neuroscout-cli version at runtime
        :type cli_version: str
        :param fmriprep_version: fmriprep version at runtime
        :type fmriprep_version: str
        :param estimator: estimator used in fitlins (anfi/nilearn)
        :type estimator: str
        :param n_subjects: Number of subjects in analysis.
        :type n_subjects: int
        :param cli_args: Run time CLI args
        :type cli_args: dict
        :type cli_args: dict

        :return: Arguments specified to CLI at runtime
        :rype: dict
        """

        def _ts_first(paths):
            tmaps = [t for t in paths if 'stat-t' in t]
            for t in tmaps:
                paths.remove(t)

            return tmaps + paths

        req = None
        # Do group, then subject level
        if group_paths is not None:
            print("Uploading group images")
            for path in tqdm.tqdm(_ts_first(group_paths)):
                files = {'image_file': open(path, 'rb')}
                req = self.post(
                    id=id, sub_route='upload', files=files, level='GROUP',
                    validation_hash=validation_hash, force=force,
                    fmriprep_version=fmriprep_version, estimator=estimator,
                    cli_version=cli_version, n_subjects=n_subjects, 
                    cli_args=json.dumps(cli_args), collection_id=collection_id)
                if collection_id is None:
                    collection_id = req['collection_id']

        if subject_paths is not None:
            print("Uploading subject images")
            for path in tqdm.tqdm(_ts_first(subject_paths)):
                files = {'image_file': open(path, 'rb')}
                req = self.post(
                    id=id, sub_route='upload', files=files, level='SUBJECT',
                    validation_hash=validation_hash, force=force,
                    fmriprep_version=fmriprep_version, estimator=estimator,
                    cli_version=cli_version, collection_id=collection_id)
                if collection_id is None:
                    collection_id = req['collection_id']

        if req is None:
            print("No images found")

        return req

    def get_uploads(self, id, select='latest', **kwargs):
        """ Get NeuroVault uploads associated with this analysis

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param select: How to select from multiple collections
            Options: "latest", "oldest" or None. If None, returns all results.
        :type select: str
        :param kwargs: Attributes to filter collections on.
            If any attributes are not found, they are ignored.
        :type kwargs: dict

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        uploads = self.get(id=id, sub_route='upload')
        
        # Sort by date
        # Strip off seconds if they are there
        for u in uploads:
            if u['uploaded_at'].count(':') > 1:
                u['uploaded_at'] = u['uploaded_at'][:-3]

        uploads = sorted(uploads, key=lambda x: datetime.datetime.strptime(
                x['uploaded_at'], '%Y-%m-%dT%H:%M'),
                         reverse=(select == 'latest'))

        # Select collections based on filters
        uploads = [
            u for u in uploads
            if all([u.get(k) == v for k, v in kwargs.items() if k in u])
            ]
        
        if not uploads:
            return None

        # Select first item unless all are requested
        if select is not None:
            uploads = [uploads[0]]

        return uploads

    def load_uploads(self, id, select='latest',
                     download_dir=None, collection_filters={}, 
                     image_filters={}):
        """ Load collection upload as NiBabel images and associated meta-data
        You can filter which images are loaded based on either collection
        level attributes or statmap image level attributes. These correspond
        to field returns for `get_uploads` at the collection level or
        `file` level. In addition for images, BIDS entities are parsed
        and available to filter on.

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param select: How to select from multiple collections
            Options: "latest", "oldest" or None. If None, returns all results.
        :type select: str
        :param download_dir: Path to download images. If None, tempdir.
        :type download_str: str
        :param collection_filters: Attributes to filter collections on.
        :type collection_filters: dict
        :param image_filters: Attributes to filter images on.
            If any attributes are not found, they are ignored.
        :type image_filters: dict

        :return: list list of tuples of format (Nifti1Image, kwargs).
        :rype: list
        """
        if download_dir is None:
            download_dir = TMP_DIR
        else:
            download_dir = Path(download_dir)

        # Sort uploads for upload date
        uploads = self.get_uploads(id, **collection_filters)
        
        if not uploads:
            return None

        # Extract entities from file path
        def _get_entities(path):
            di = {}
            for t in ['task', 'contrast', 'stat', 'space']:
                matches = re.findall(f"{t}-(.*?)_", path)
                if matches:
                    di[t] = matches[0]
            return di

        # Filter files, download if necessary and load as Niimg-object
        flat = []
        for u in uploads:
            for f in u.pop('files'):
                f = {**f, **_get_entities(f['basename'])}

                # If file matches kwargs and is in NV
                if f.pop('status') == 'OK' and all(
                 [f.get(k, None) == v  if k in f else False for k, v in image_filters.items()]):
                    # Download and open
                    img_url = "https://neurovault.org/media/images/" \
                        f"{u['collection_id']}/{f['basename']}"
                    f_name = download_dir / \
                        f"{u['collection_id']}_{f['basename']}"

                    if not f_name.exists():
                        print(".", end ="")  
                        with f_name.open('wb') as file:
                            file.write(requests.get(img_url).content)
                    niimg = nib.load(f_name)

                    f.pop('traceback')
                    flat.append((niimg, {**u, **f}))
        return flat

    def plot_uploads(self, id, plot_args={}, **kwargs):
        """ Plot uploads for matching collections using nilearn

        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param plot_args: Plot arguments for nilearn.plotting
        :type plot_args: dict
        :param kwargs: Arguments for load_uploads
        :type kwargs: dict
        
        :return: list of matplotlib objects.
        :rype: list
        """

        images = self.load_uploads(id, **kwargs)

        if images:
            plots = []
            for niimg, _ in images:
                plots.append(
                    nilearn.plotting.plot_stat_map(niimg, **plot_args))

            return plots
        else:
            return None

    def get_full(self, id):
        """ Get full analysis object (including runs and predictors)

        :param id: :class:`Analysis` `hash_id`
        :type id: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.get(id=id, sub_route='full')

    def fill(self, id, partial=True, dryrun=False):
        """ Fill missing fields
        
        :param id: :class:`Analysis` `hash_id`
        :type id: str
        :param partial: Partial fill.
        :type partial: bool
        :param dryrun: Do not commit to database.
        :type dryrun: bool
        
        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.post(id=id, sub_route='fill',
                         params=dict(partial=partial, dryrun=dryrun))

    def get_resources(self, id):
        """ Get analysis resources

        :param id: :class:`Analysis` `hash_id`
        :type id: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.get(id=id, sub_route='resources')

    def get_status(self, id):
        """ Get analysis status

        :param id: :class:`Analysis` `hash_id`
        :type id: str

        :return: Requests response object
        :rype: :class:`requests.Response`
        """
        return self.get(id=id, sub_route='compile')