""" Miscelaneous utilities """


def build_model(name, variables, task, subject, run=None, session=None,
                hrf_variables=None, transformations=None,
                contrasts=None, dummy_contrasts=True):
    """ Builds a basic two level BIDS-Model """
    hrf_variables = hrf_variables or []
    transformations = transformations or []
    contrasts = contrasts or []

    if not set(variables) >= set(hrf_variables):
        raise ValueError("HRF Variables must be a subset of all variables")

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
          "Subject": subject,
          "Task": task
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
        for s in model['Steps']:
            s.pop('DummyContrasts')

    if run is not None:
        model['Input']['Run'] = run

    if session is not None:
        model['Input']['Session'] = session

    return model
