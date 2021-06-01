from setuptools import setup

from TVMFuzz import __version__

setup(
    name='TVMFuzz',
    version=__version__,
    url='https://github.com/UniverseFly/TVMFuzz/',
    packages=['TVMFuzz'],
    package_data={
        "TVMFuzz": ["tvmfuzz_settings.ini"]
    }
)
