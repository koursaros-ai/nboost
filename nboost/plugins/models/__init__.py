from pathlib import Path
from typing import Type
from nboost.helpers import import_class, download_file, extract_tar_gz
from nboost.plugins.models.base import ModelPlugin
from nboost.maps import CLASS_MAP, MODULE_MAP, URL_MAP
from nboost.logger import set_logger


def resolve_model(data_dir: Path, model_dir: str, model_cls: str, **kwargs):
    """Dynamically import class from a module in the CLASS_MAP. This is used
    to manage dependencies within nboost. For example, you don't necessarily
    want to import pytorch models everytime you boot up tensorflow..."""

    logger = set_logger('resolve_model')
    data_dir.mkdir(parents=True, exist_ok=True)
    model_dir = data_dir.joinpath(model_dir).absolute()

    if model_dir.exists():
        logger.info('Using model cache from %s', model_dir)

        if model_dir.name in CLASS_MAP:
            model_cls = CLASS_MAP[model_dir.name]
        elif model_cls not in MODULE_MAP:
            raise ImportError('Class "%s" not in %s.' % CLASS_MAP.keys())

        module = MODULE_MAP[model_cls]
        model = import_class(module, model_cls)  # type: Type[ModelPlugin]
        return model(model_dir=str(model_dir), **kwargs)
    else:
        if model_dir.name in CLASS_MAP:
            model_cls = CLASS_MAP[model_dir.name]
            module = MODULE_MAP[model_cls]
            if model_dir.name in URL_MAP: # DOWNLOAD AND CACHE
                url = URL_MAP[model_dir.name]
                binary_path = data_dir.joinpath(Path(url).name)

                if binary_path.exists():
                    logger.info('Found model cache in %s', binary_path)
                else:
                    logger.info('Downloading "%s" model.', model_dir)
                    download_file(url, binary_path)

                if binary_path.suffixes == ['.tar', '.gz']:
                    logger.info('Extracting "%s" from %s', model_dir, binary_path)
                    extract_tar_gz(binary_path, data_dir)
            else: # pass along to plugin maybe it can resolve it
                model_dir = model_dir.name

            model = import_class(module, model_cls)  # type: Type[ModelPlugin]
            return model(model_dir=str(model_dir), **kwargs)
        else:
            if model_cls in MODULE_MAP:
                module = MODULE_MAP[model_cls]
                model = import_class(module, model_cls)  # type: Type[ModelPlugin]
                return model(model_dir=model_dir.name, **kwargs)
            else:
                raise ImportError('model_dir %s not found in %s. You must '
                                  'set --model class to continue.'
                                  % (model_dir.name, CLASS_MAP.keys()))