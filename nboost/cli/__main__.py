from . import create_proxy


def main():
    proxy = create_proxy()
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.close()


if __name__ == '__main__':
    main()
