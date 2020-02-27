from abc import abstractmethod
from typing import Generator
from nboost.helpers import count_lines
from nboost.logger import set_logger
from nboost.indexers import defaults
from nboost import PKG_PATH
from pathlib import Path
from tqdm import tqdm
import csv


class BaseIndexer:
    """An object that sends a csv to a given search api."""

    def __init__(self, file: type(defaults.file) = defaults.file,
                 index_name: type(defaults.index_name) = defaults.index_name,
                 id_col: type(defaults.id_col) = defaults.id_col,
                 host: type(defaults.host) = defaults.host,
                 port: type(defaults.port) = defaults.port,
                 delim: type(defaults.delim) = defaults.delim,
                 shards: type(defaults.shards) = defaults.shards,
                 verbose: type(defaults.verbose) = defaults.verbose, **_):
        """
        :param name: name of the index
        :param id_col: column number of the id
        :param field_col: column number of the field data
        :param field_name: name of the field
        :param host: host of the search api server
        :param port: port the the server
        :param shards: number of shards for the index
        """
        self.file = file
        self.index_name = index_name
        self.id_col = id_col
        self.host = host
        self.port = port
        self.delim = delim
        self.shards = shards
        self.logger = set_logger(self.__class__.__name__, verbose=verbose)

    def csv_generator(self) -> Generator:
        """Check for the csv in the current working directory first, then
        search for it in the package.

        Generates id_col and dict of {<column name>: <column value>}
        """

        cwd_path = Path().joinpath(self.file).absolute()
        pkg_path = PKG_PATH.joinpath('resources').joinpath(self.file)

        if cwd_path.exists():
            path = cwd_path
        elif pkg_path.exists():
            path = pkg_path
        else:
            self.logger.error('Could not find %s or %s', pkg_path, cwd_path)
            raise SystemExit

        self.logger.info('Estimating completion size...')
        num_lines = count_lines(path)
        with path.open() as file:
            with tqdm(total=num_lines, desc=path.name) as pbar:
                for line in csv.DictReader(file, delimiter=self.delim):
                    cid = None

                    if self.id_col:
                        try: cid = line.popitem(last=False)[1] # Python 3.5 bug in some versions
                        except: cid = line.popitem()[1]

                    yield cid, dict(line)

                    pbar.update()

    @abstractmethod
    def index(self):
        """uses the csv_generator() to send the csv to the index"""
