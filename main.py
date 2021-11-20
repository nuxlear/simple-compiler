from lexer import *
from parser import *
from code_generator import *

import os
import sys
from pathlib import Path


def main():
    args = sys.argv
    if len(args) > 1 or len(args) == 0:
        print('Usage: python main.py [INPUT_FILE]')

    # TODO: add lexer, parser, code generator


if __name__ == '__main__':
    main()
