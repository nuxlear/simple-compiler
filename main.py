from simple_compiler.lexer import *
from simple_compiler.parser import *
from simple_compiler.code_generator import *

import os
import sys


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
    tree = Maketree(parser.parse(tokens))
    symbol = generator._make_symbol_table(tree)
    for k, v in symbol.items():
        print(f'{k}: {v}')
    print()
    code = generator.generate(tree)
    for x in code:
        print(x)


if __name__ == '__main__':
    main()
