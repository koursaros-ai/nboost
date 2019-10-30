import termcolor
import argparse


def set_parser():
    # create the top-level parser
    parser = argparse.ArgumentParser(
        description='%s: Neural semantic search ranking for Elasticsearch.' % (
                        termcolor.colored('Koursaros AI', 'cyan', attrs=['underline'])),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--verbose', action='store_true', default=False, help='turn on detailed logging')
    parser.add_argument('--client', type=str, default='BaseClient', help='which client to use')
    parser.add_argument('--model', type=str, default='BaseModel', help='which model to use')
    parser.add_argument('--server_host', type=str, default='127.0.0.1', help='host of the server')
    parser.add_argument('--server_port', type=int, default=9200, help='port of the server')
    parser.add_argument('--proxy_host', type=str, default='127.0.0.1', help='host of the proxy')
    parser.add_argument('--proxy_port', type=int, default=53001, help='port of the proxy')
    parser.add_argument('--multiplier', type=int, default=10, help='factor to increase results by')
    return parser
