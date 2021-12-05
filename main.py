from lexer import *
from parser import *
from code_generator import *

import os
import sys
from pathlib import Path


def main():
    args = sys.argv
    if len(args) != 2:
        print('Usage: python main.py [INPUT_FILE]')

    input_path = args[1]
    if not os.path.isfile(input_path):
        raise FileNotFoundError(input_path)

    lexer = Lexer(input_path)
    parser = Parser()
    generator = CodeGenerator()

    tokens = lexer.scan()
    tree = parser.parse(tokens)
    code = generator.generate(tree)


if __name__ == '__main__':
    main()
