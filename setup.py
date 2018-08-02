from setuptools import setup, find_packages
PACKAGES = find_packages()

setup(name='pyns',
      version='0.0.1',
      description='Neuroscout API wrapper',
      url='http://github.com/neuroscout/pynv',
      author='Alejandro de la Vega',
      author_email='delavega@utexas.edu',
      license='MIT',
      packages=PACKAGES,
      zip_safe=False)
