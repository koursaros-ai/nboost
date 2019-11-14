from setuptools import setup
from pathlib import Path
from nboost import __version__

setup(
    name='nboost',
    packages=['nboost'],
    include_package_data=True,
    version=__version__,
    license='Apache 2.0',
    description='Nboost is a scalable, search-'
                'api-boosting platform for developing and deploying '
                'automated SOTA models more relevant search results.',
    long_description=Path('README.md').read_text('utf8'),
    long_description_content_type='text/markdown',
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
        'termcolor',
        'aiohttp',
        'requests',
        'elasticsearch',
        'tqdm'
    ],
    extras_require={
        'torch': ['torch', 'transformers'],
        'tf': ['tensorflow'],
    },
    entry_points={'console_scripts': [
        'nboost=nboost.cli.__main__:main',
        'nboost-tutorial=nboost.tutorials.cli:main',
        'nboost-benchmark=nboost.benchmarks.cli:main'
    ]},
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
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)