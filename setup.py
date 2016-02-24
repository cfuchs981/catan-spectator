from distutils.core import setup

with open("README.md", "r") as fp:
    long_description = fp.read()

with open('VERSION', 'r') as fp:
    version = fp.read()

setup(name="catanlog",
      version=version,
      author="Ross Anderson",
      author_email="ross.anderson@ualberta.ca",
      url="https://github.com/rosshamish/catanlog/",
      download_url = 'https://github.com/rosshamish/catan-spectator/tarball/'+version,
      description='Transcribe games of Settlers of Catan for research purposes, replay purposes, broadcast purposes, etc.',
      long_description=long_description,
      keywords=[],
      classifiers=[],
      license="GPLv3",

      py_modules=["catanlog"],
      install_requires=[
          'hexgrid',
          'parse',
      ],
      )