from setuptools import setup, find_packages
from pathlib import Path
from nboost import __version__

setup(
    name='nboost',
    packages=find_packages(),
    include_package_data=True,
    version=__version__.__doc__,
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
        'elasticsearch',
        'distributed',
        'cloud-native',
        'neural',
        'inference',
    ],
    install_requires=[
        'termcolor',
        'requests',
        'elasticsearch',
        'tqdm',
        'jsonpath-ng',
        'flask',
        'nltk'
    ],
    extras_require={
        'pt': ['torch', 'transformers==2.2.1'],
        'tf': ['tensorflow==1.15', 'sentencepiece'],
        'all': ['torch', 'tensorflow==1.15', 'transformers==2.2.1'],
    },
    entry_points={'console_scripts': [
        'nboost=nboost.__main__:main',
        'nboost-index=nboost.indexers.__main__:main'
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