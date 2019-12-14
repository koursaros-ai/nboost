from abc import abstractmethod
from typing import Generator
from nboost.helpers import count_lines
from nboost.logger import set_logger
from nboost import PKG_PATH
from pathlib import Path
from tqdm import tqdm
import csv


class BaseIndexer:
    """An object that sends a csv to a given search api."""

    def __init__(self, file: str, name: str = 'nboost', id_col: int = 0,
                 field_col: int = 1, field_name: str = 'passage',
                 host: str = '0.0.0.0', port: int = 9200, delim: str = '\t',
                 shards: int = 3, verbose: bool = False, **_):
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
        self.name = name
        self.id_col = id_col
        self.field_col = field_col
        self.field_name = field_name
        self.host = host
        self.port = port
        self.delim = delim
        self.shards = shards
        self.logger = set_logger(self.__class__.__name__, verbose=verbose)

    def csv_generator(self) -> Generator:
        """yield the `--id_col` and `--field_col` from the `--file` csv"""
        pkg_path = PKG_PATH.joinpath('resources').joinpath(self.file)
        cwd_path = Path().joinpath(self.file).absolute()

        if pkg_path.exists():
            path = pkg_path
        elif cwd_path.exists():
            path = cwd_path
        else:
            self.logger.error('Could not find %s or %s', pkg_path, cwd_path)
            raise SystemExit

        self.logger.info('Estimating completion size...')
        num_lines = count_lines(path)
        with path.open() as file:
            with tqdm(total=num_lines, desc=path.name) as pbar:
                for line in csv.reader(file, delimiter=self.delim):
                    pbar.update()
                    yield line[self.id_col], line[self.field_col]

    @abstractmethod
    def index(self):
        """send the csv to the index"""
