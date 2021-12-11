from simple_compiler.node import *
# from parser import *
from typing import List


class OpNode:
    def __init__(self, op, left=None, right=None, parent=None):
        self.op = op
        self.parent = parent
        self.left = left
        self.right = right
        self.regnum = None

    def __repr__(self):
        return f'Op({self.op}, {self.left}, {self.right})'


class ValNode:
    def __init__(self, val, parent=None):
        self.val = val
        self.parent = parent
        self.regnum = None

    def __repr__(self):
        return f'Val({self.val})'


class CodeGenerator:
    def __init__(self):
        self.cond_jump_counter = 0
        self.max_reg_num = 0

    def generate(self, tree: Node):
        symbols, _ = self._make_symbol_table(tree)
        inter_repr = self._make_intermediate_repr(tree)
        parsed_repr = self._parse_repr(inter_repr)
        out_code = self._make_instructions(parsed_repr)

        return list(itertools.chain.from_iterable(out_code)), symbols

    def _make_symbol_table(self, tree: Node):
        dtype_size = {'int': 4, 'char': 1}

        id_counter = 0
        symbol_table = {}
        base_addr = 1000

        assert isinstance(tree, Prog), ValueError('Making symbol table must be executed on `Prog` node. ')
        symbol_table[id_counter] = (0, 'FUNCTION', tree.word)
        id_counter += 1

        blocks = self._find_block_nodes(tree)
        words = self._find_word_nodes(tree)

        for bid, block in enumerate(blocks, 1):
            lines = block.decls.traverse()
            for line in lines:
                dsize = dtype_size[line[1]]
                if base_addr % dsize != 0:
                    base_addr = (base_addr + dsize - 1) // dsize * dsize
                addr = base_addr
                base_addr += dsize

                symbol_table[id_counter] = (bid, line[1].upper(), line[2], addr)
                target_words = self._find_word_by_block_and_name(words, block, line[2])
                for w in target_words:
                    w.symbol_id = id_counter
                    w.addr = addr

                id_counter += 1

        return symbol_table, words

    def _find_block_nodes(self, node):
        blocks = []
        if isinstance(node, Block):
            blocks.append(node)

        child = node.get_child()
        for x in child:
            blocks += self._find_block_nodes(x)
        return blocks

    def _find_word_by_block_and_name(self, words: List[Word], block: Block, name_word: Word):
        ans = []
        for word in words:
            if word.val != name_word.val:
                continue
            if self._find_block_of_word(word) == block:
                ans.append(word)
        return ans

    def _find_block_of_word(self, word: Word):
        node = word
        while node is not None:
            if isinstance(node, Block):
                for decl in node.decls.traverse():
                    if decl[2].val == word.val:
                        return node
            node = node.parent
        return node

    def _find_word_nodes(self, node):
        words = []
        if isinstance(node, Word):
            words.append(node)

        child = node.get_child()
        for x in child:
            words += self._find_word_nodes(x)
        return words

    def _make_intermediate_repr(self, tree: Node):
        code = tree.traverse()
        return code

    def _parse_repr(self, code):
        results = []
        for x in code:
            if x[0] in ['begin', 'end', 'assign', 'cond', 'exit']:
                result = self._make_eval_tree(x)
                results.append(result)
        return results

    def _make_eval_tree(self, line):
        root = None
        if line[0] in ['begin', 'end']:
            left = ValNode(line[1])
            root = OpNode(line[0], left)
            left.parent = root

        if line[0] == 'assign':
            left = ValNode(line[1])
            right = self._make_expr_node(line[2])
            root = OpNode('=', left, right)
            left.parent = right.parent = root

        if line[0] == 'cond':
            ll = self._make_expr_node(line[1][1])
            lr = self._make_expr_node(line[1][2])
            l = OpNode('<', ll, lr)
            ll.parent = lr.parent = l

            true_list = self._parse_repr(line[2])
            false_list = self._parse_repr(line[3])
            r = OpNode('tf', true_list, false_list)

            root = OpNode('cond', l, r)
            l.parent = r.parent = root

        if line[0] == 'exit':
            left = self._make_expr_node(line[1])
            root = OpNode('exit', left)
            left.parent = root

        return root

    def _make_expr_node(self, expr):
        terms = []
        for term in expr:
            terms.append(self._make_term_node(term))

        if len(terms) == 1:
            return terms[0]

        root = None
        while len(terms) > 1:
            l = terms.pop(0)
            r = terms.pop(0)
            op = OpNode('+', l, r)
            l.parent = r.parent = op
            root = op
            terms.insert(0, op)
        return root

    def _make_term_node(self, term):
        facts = []
        for fact in term:
            facts.append(ValNode(fact))

        if len(facts) == 1:
            return facts[0]

        root = None
        while len(facts) > 1:
            l = facts.pop(0)
            r = facts.pop(0)
            op = OpNode('*', l, r)
            l.parent = r.parent = op
            root = op
            facts.insert(0, op)
        return root

    def _make_instructions(self, parsed_repr):
        insts = []
        for root in parsed_repr:
            self._allocate_register(root)
            inst = self._convert_parsed_repr_to_inst(root)
            insts.append(inst)
        return insts

    def _allocate_register(self, node):
        if node.op == 'cond':
            self._set_regnum(node.left, 0)
            for x in node.right.left:
                self._allocate_register(x)
            for x in node.right.right:
                self._allocate_register(x)
            return
        if node.op == '=':
            self._set_regnum(node.right, 0)
            return
        self._set_regnum(node, 0)

    def _set_regnum(self, node, counter):
        node.regnum = counter
        if counter > self.max_reg_num:
            self.max_reg_num = counter
        if isinstance(node, ValNode):
            return
        if node.left is not None:
            self._set_regnum(node.left, counter)
        if node.right is not None:
            self._set_regnum(node.right, counter + 1)

    def _convert_parsed_repr_to_inst(self, node):
        insts = []
        if isinstance(node, list):
            for x in node:
                insts.extend(self._convert_parsed_repr_to_inst(x))

        if isinstance(node, ValNode):
            if isinstance(node.val, Word) and node.val.symbol_id is not None:
                insts.append(f'LD\tR{node.regnum}, ({node.val.addr})')
            else:
                insts.append(f'LD\tR{node.regnum}, {node.val.val}')

        if isinstance(node, OpNode):
            if node.op == 'begin':
                insts.append(f'BEGIN\t{node.left.val}')

            if node.op == 'end':
                insts.append('EXIT:')
                insts.append(f'END\t{node.left.val}')

            if node.op == '=':
                insts.extend(self._convert_parsed_repr_to_inst(node.right))
                insts.append(f'ST\tR{node.right.regnum}, ({node.left.val.addr})')

            if node.op == '+':
                insts.extend(self._convert_parsed_repr_to_inst(node.left))
                insts.extend(self._convert_parsed_repr_to_inst(node.right))
                insts.append(f'ADD\tR{node.regnum}, R{node.left.regnum}, R{node.right.regnum}')

            if node.op == '*':
                insts.extend(self._convert_parsed_repr_to_inst(node.left))
                insts.extend(self._convert_parsed_repr_to_inst(node.right))
                insts.append(f'MUL\tR{node.regnum}, R{node.left.regnum}, R{node.right.regnum}')

            if node.op == '<':
                insts.extend(self._convert_parsed_repr_to_inst(node.left))
                insts.extend(self._convert_parsed_repr_to_inst(node.right))
                insts.append(f'LT\tR{node.regnum}, R{node.left.regnum}, R{node.right.regnum}')

            if node.op == 'exit':
                insts.extend(self._convert_parsed_repr_to_inst(node.left))
                insts.append(f'JUMP\tEXIT')

            if node.op == 'cond':
                cnt = self.cond_jump_counter
                self.cond_jump_counter += 1
                end_label = f'END{cnt}'
                else_label = f'ELSE{cnt}'

                insts.extend(self._convert_parsed_repr_to_inst(node.left))
                insts.append(f'JUMPF\tR{node.left.regnum}, {else_label}')
                insts.extend(self._convert_parsed_repr_to_inst(node.right.left))    # true_list
                insts.append(f'JUMP\t{end_label}')
                insts.append(f'{else_label}:')
                insts.extend(self._convert_parsed_repr_to_inst(node.right.right))   # false_list
                insts.append(f'{end_label}:')

        return insts
