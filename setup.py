from setuptools import setup, find_packages
PACKAGES = find_packages()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pyns',
      version='0.4.7',
      description='Neuroscout API wrapper',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/neuroscout/pyns',
      author='Alejandro de la Vega',
      author_email='aleph4@gmail.com',
      install_requires=['requests>=2.21', 'pyjwt~=1.7.1', 'tqdm>=4.30.0'],
      license='MIT',
      packages=PACKAGES,
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      zip_safe=False)
