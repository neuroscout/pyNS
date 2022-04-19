# pyNS 🌲
![Python package](https://github.com/neuroscout/pyNS/workflows/Python%20package/badge.svg)
[![codecov](https://codecov.io/gh/neuroscout/pyns/branch/master/graph/badge.svg)](https://codecov.io/gh/neuroscout/pyns)
[![docs](https://readthedocs.org/projects/pyns/badge/?version=latest)](https://pyns.readthedocs.io/en/latest/)

The Neuroscout API wrapper for Python.

### Overview
pyNS is a python library to easily interact with the Neuroscout API.
pyNS enables interations with the Neuroscout API in applications such as [neuroscout-cli](https://github.com/neuroscout/neuroscout-cli/), as well as advanced usage of Neuroscout that goes beyond what is possible with the [web application](https://neuroscout.org).

### Installation
Use `pip` to install it:

    pip install pyns

## Documentation 📚
Full documentation can be found at [readthedocs] (https://pyns.readthedocs.io/en/latest/).

For API docs , check out the [Swagger API UI](http://neuroscout.org/swagger-ui/): 

For a tutorial see this [jupyter notebook example](./examples/Tutorial.ipynb).
You can also follow the Neuroscout Paper's analyses in this interactive [jupyter book](https://neuroscout.github.io/neuroscout-paper/intro.html)

### Testing
We use pytest for testing, and betamax to record HTTP requests used in test into cassettes.

To re-run tests locally set the`USER_TEST_EMAIL` and `USER_TEST_PWD` environment variables with valid API credentials.
