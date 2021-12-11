from simple_compiler.node import *
# from parser import *


class CodeGenerator:
    def generate(self, tree: Node):
        symbols = self._make_symbol_table(tree)
        return tree.traverse()

    def _make_symbol_table(self, tree: Node):
        id_counter = 0
        symbol_table = {}

        assert isinstance(tree, Prog), ValueError('Making symbol table must be executed on `Prog` node. ')
        symbol_table[id_counter] = (0, 'FUNCTION', tree.word.val)
        id_counter += 1

        blocks = self._find_block_nodes(tree)
        for bid, block in enumerate(blocks, 1):
            lines = block.decls.traverse()
            for line in lines:
                symbol_table[id_counter] = (bid, line[1].upper(), line[2])
                id_counter += 1

        return symbol_table

    def _find_block_nodes(self, node):
        blocks = []
        if isinstance(node, Block):
            blocks.append(node)

        child = node.get_child()
        for x in child:
            blocks += self._find_block_nodes(x)
        return blocks

    def _make_intermediate_repr(self, tree: Node):
        code = tree.traverse()
        # TODO: find symbols
        # TODO: make indirect triples
