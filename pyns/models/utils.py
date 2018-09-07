""" Miscelaneous utilities """

def build_model(variables, task, subject, run=None, session=None,
                hrf_variables=None, transformations=None,
                contrasts=None, auto_contrasts=True):
    """ Builds a basic two level BIDS-Model """
    hrf_variables = hrf_variables or []
    transformations = transformations or []
    contrasts = contrasts or []

    if not set(variables) >= set(hrf_variables):
        raise ValueError("HRF Variables must be a subset of all variables")

    model = {
        "blocks": [
          {
            "auto_contrasts": auto_contrasts,
            "contrasts": contrasts,
            "level": "run",
            "model": {
              "HRF_variables": hrf_variables,
              "variables": variables
            },
            "transformations": transformations
          },
          {
            "auto_contrasts": True,
            "level": "dataset"
          }
        ],
        "input": {
          "subject": subject,
          "task": task,
        }
    }

    if run is not None:
        model['input']['run'] = run

    if session is not None:
        model['input']['session'] = run

    return model
