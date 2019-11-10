from setuptools import setup, find_packages
from pathlib import Path

setup(
    name='nboost',
    packages=find_packages(),
    include_package_data=True,
    version='0.0.1',
    license='MIT',
    description='Nboost is a scalable, search-'
                'api-boosting platform for developing and deploying '
                'automated SOTA models more relevant search results.',
    long_description=Path('README.md').read_text('utf8'),
    author='Koursaros',
    author_email='cole.thienes@gmail.com',
    url='https://github.com/koursaros-ai/nboost',
    # download_url='https://github.com/koursaros-ai/nboost/archive/0.0.1.tar.gz',
    keywords=[
        'aiohttp',
        'elasticsearch',
        'distributed',
        'cloud-native',
        'neural',
        'inference',
    ],
    install_requires=[
        'torch',
        'transformers',
        'termcolor',
        'aiohttp'
    ],
    entry_points={'console_scripts': ['nboost=nboost.cli.__main__:main']},
    classifiers=[
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)