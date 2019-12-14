"""__main__ cli entrypoint"""
from nboost.proxy import Proxy
from nboost.cli import set_parser


def main():
    """Entrypoint for nboost"""
    parser = set_parser()
    args = parser.parse_args()
    proxy = Proxy(**vars(args))
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.close()


if __name__ == '__main__':
    main()
