"""Build and push images"""

from nboost import __version__, PKG_PATH, IMAGE_MAP
from nboost.logger import set_logger
import subprocess

REGISTRY = 'koursaros/nboost'
VERSION_TAG = '%s:%s-{image}' % (REGISTRY, __version__.__doc__)
LATEST_TAG = '%s:latest-{image}' % REGISTRY
BUILD = 'docker build -t %s -t %s {path}' % (VERSION_TAG, LATEST_TAG)
PUSH = 'docker push %s' % REGISTRY


def execute(command: str):
    """Execute command in subprocess"""
    logger = set_logger('RELEASE')
    logger.info(command)
    subprocess.call(command, shell=True)


def build():
    """Build dockerfiles"""
    for image, path in IMAGE_MAP.items():
        path = PKG_PATH.joinpath(path).absolute()
        execute(BUILD.format(image=image, path=path))


def push():
    """Push images"""
    execute(PUSH)


if __name__ == "__main__":
    build()
    push()
