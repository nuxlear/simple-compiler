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
    input_name = input_path.split('.')[0]

    lexer = Lexer(input_path)
    parser = Parser()
    generator = CodeGenerator()

    tokens = lexer.scan()
    tree = Maketree(parser.parse(tokens))
    out_codes, symbols = generator.generate(tree)

    with open(f'{input_name}.symbol', 'w') as f:
        symbol_list = sorted(list(symbols.values()), key=lambda x: x[0])
        scope = set()
        for symbol in symbol_list:
            if symbol[0] not in scope:
                f.write(f'Scope: {symbol[0]}\n')
                scope.add(symbol[0])
            addr = '' if len(symbol) < 4 else f' [addr: {symbol[3]}]'
            f.write(f'\tSymbol: {symbol[2]} (type: {symbol[1]}){addr}\n')

    with open('myProgram.code', 'w') as f:
        f.writelines([f'{x}\n' for x in out_codes])

    print(f'The number of register used: {generator.max_reg_num + 1}')


if __name__ == '__main__':
    main()
