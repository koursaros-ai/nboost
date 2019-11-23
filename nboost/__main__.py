"""__main__ cli entrypoint"""
from .cli import create_proxy


def main():
    """Entrypoint for nboost"""
    proxy = create_proxy()
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.close()


if __name__ == '__main__':
    main()
