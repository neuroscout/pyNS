""" Miscelaneous utilities """


def build_model(name, variables, task, subject, run=None, session=None,
                hrf_variables=None, transformations=None,
                contrasts=None, auto_contrasts=True):
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
            "AutoContrasts": auto_contrasts,
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

    if run is not None and len(run) > 1:
        model['Steps'].append(
            {
                "AutoContrasts": True,
                "Level": "Subject"
            }
        )

    model['Steps'].append(
        {
            "AutoContrasts": True,
            "Level": "Dataset"
        }
    )

    if run is not None:
        model['Input']['Run'] = run

    if session is not None:
        model['Input']['Session'] = session

    return model
