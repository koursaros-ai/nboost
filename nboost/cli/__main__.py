from . import create_proxy

if __name__ == '__main__':
    proxy = create_proxy()
    try:
        proxy.start()
    except KeyboardInterrupt:
        proxy.close()
