#!/usr/bin/env python3
import argparse
import logging

from blackcat import BlackCat
from util.config import Config

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)
    parser = argparse.ArgumentParser(description='Manage or enable security alerts for github.')
    parser.add_argument('--enable', action='store_true',
                        help='Don\'t run a scan. Instead, enable alerts for all repos.')
    parser.add_argument('--enable-start-page', type=int, default=0, help='Set the start page for an enable run. '
                                                                         'Has no effect if --enable isn\'t set.')
    BlackCat.execute_cli(parser.parse_args(), Config())
