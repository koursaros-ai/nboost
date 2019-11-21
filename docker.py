"""Build and push images"""

from nboost import __version__, PKG_PATH, IMAGE_MAP
from nboost.base.logger import set_logger
import subprocess

REPO = 'koursaros/nboost'

CONTEXT = {
    image: dict(
        path=PKG_PATH.joinpath(path).absolute(),
        tag='%s:%s-%s' % (REPO, __version__, image)
    ) for image, path in IMAGE_MAP.items()
}


def execute(command: str):
    """Execute command in subprocess"""
    logger = set_logger('RELEASE')
    logger.info(command)
    subprocess.call(command, shell=True)


def build():
    """Build dockerfiles"""
    for ctx in CONTEXT.values():
        execute('docker build -t %s %s' % (ctx['tag'], ctx['path']))


def push():
    """Push images"""
    for ctx in CONTEXT.values():
        execute('docker push %s' % ctx['tag'])


if __name__ == "__main__":
    build()
    push()
