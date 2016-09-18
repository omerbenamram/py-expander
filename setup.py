from setuptools import setup, find_packages


setup(
    name='pyexpander',
    version='0.1dev',
    packages=find_packages(),
    long_description=open('README.md').read(),
    install_requires=['logbook', 'guessit', 'subliminal', 'babelfish'],
    entry_points={
      'console_scripts': [
          'pyexpand = pyexpander:main',
      ]
    }
)
