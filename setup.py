from setuptools import setup

from tvmfuzz import __version__

setup(
    name='tvmfuzz',
    version=__version__,
    url='https://github.com/UniverseFly/TVMFuzz/',
    packages=['tvmfuzz'],
    package_data={
        "tvmfuzz": ["tvmfuzz_settings.ini"]
    }
)
