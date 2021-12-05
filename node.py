from typing import Optional


def indent(lines):
    return [f'\t{x}' for x in lines]


class Node:
    def __init__(self, parent=None):
        self.parent: Node = parent

    def set_parent(self, parent):
        self.parent: Node = parent

    def traverse(self):
        raise NotImplemented

    def __repr__(self):
        return '\n'.join(map(str, self.repr_lines()))

    def repr_lines(self):
        raise NotImplemented


class Epsilon(Node):
    def traverse(self):
        return []

    def repr_lines(self):
        return []


class NonTerminal(Node):
    pass


class Prog(NonTerminal):
    def __init__(self, word, block):
        super(Prog, self).__init__()
        self.word: Word = word
        self.block: Optional[Block, Epsilon] = block

    def traverse(self):
        name = self.word.val
        return [('begin', name)] + self.block.traverse() + [('end', name)]

    def repr_lines(self):
        return [f'{self.word} ()'] + indent(self.block.repr_lines())


class Block(NonTerminal):
    def __init__(self, decls, slist, parent=None):
        super(Block, self).__init__(parent=parent)
        self.decls: Decls = decls
        self.slist: Slist = slist

    def traverse(self):
        return self.decls.traverse() + self.slist.traverse()

    def repr_lines(self):
        return ['{'] + indent(self.decls.repr_lines()) + indent(self.slist.repr_lines()) + ['}']


class Decls(NonTerminal):
    def __init__(self, decls_, parent=None):
        super(Decls, self).__init__(parent=parent)
        self.decls_: Optional[DeclsTail, Epsilon] = decls_

    def traverse(self):
        return self.decls_.traverse()

    def repr_lines(self):
        return self.decls_.repr_lines()


class DeclsTail(NonTerminal):
    def __init__(self, decl, decls_, parent=None):
        super(DeclsTail, self).__init__(parent=parent)
        self.decl: Decl = decl
        self.decls_: Optional[DeclsTail, Epsilon] = decls_

    def traverse(self):
        return self.decl.traverse() + self.decls_.traverse()

    def repr_lines(self):
        return self.decl.repr_lines() + self.decls_.repr_lines()


class Decl(NonTerminal):
    def __init__(self, vtype, word, parent=None):
        super(Decl, self).__init__(parent=parent)
        assert vtype in ['int', 'char', None], ValueError(f'Invalid vtype: {vtype}')
        self.vtype: Optional[str, None] = vtype
        self.word: Word = word

    def traverse(self):
        return [('decl', self.vtype, self.word.traverse())]

    def repr_lines(self):
        type_str = self.vtype + ' ' if self.vtype is not None else ''
        return [f'{type_str}{self.word.val};']


class Slist(NonTerminal):
    def __init__(self, stat, slist_, parent=None):
        super(Slist, self).__init__(parent=parent)
        self.stat: Optional[Stat, Epsilon] = stat
        self.slist_: Optional[SlistTail, Epsilon] = slist_

    def traverse(self):
        return self.stat.traverse() + self.slist_.traverse()

    def repr_lines(self):
        return self.stat.repr_lines() + self.slist_.repr_lines()


class SlistTail(NonTerminal):
    def __init__(self, stat, slist_, parent=None):
        super(SlistTail, self).__init__(parent=parent)
        self.stat: Optional[Stat, Epsilon] = stat
        self.slist_: Optional[SlistTail, Epsilon] = slist_

    def traverse(self):
        return self.stat.traverse() + self.slist_.traverse()

    def repr_lines(self):
        return self.stat.repr_lines() + self.slist_.repr_lines()


class Stat(NonTerminal):
    pass


class IfElseStat(Stat):
    def __init__(self, cond, true_block, false_block, parent=None):
        super(IfElseStat, self).__init__(parent=parent)
        self.cond: CondStat = cond
        self.true_block: Optional[Block, Epsilon] = true_block
        self.false_block: Optional[Block, Epsilon] = false_block

    def traverse(self):
        return [('cond', self.cond.traverse(), self.true_block.traverse(), self.false_block.traverse())]

    def repr_lines(self):
        return ['IF'] + self.cond.repr_lines() + \
               ['THEN'] + self.true_block.repr_lines() + \
               ['ELSE'] + self.false_block.repr_lines()


class CondStat(NonTerminal):
    def __init__(self, first_expr, second_expr, parent=None):
        super(CondStat, self).__init__(parent=parent)
        self.first_expr: Expr = first_expr
        self.second_expr: Expr = second_expr

    def traverse(self):
        return [('lt', self.first_expr.traverse(), self.second_expr.traverse())]

    def repr_lines(self):
        return [f'{self.first_expr.repr_lines()} < {self.second_expr.repr_lines()}']


class AssignStat(Stat):
    def __init__(self, word, expr, parent=None):
        super(AssignStat, self).__init__(parent=parent)
        self.word: Word = word
        self.expr: Expr = expr

    def traverse(self):
        return [('assign', self.word.val, self.expr.traverse())]

    def repr_lines(self):
        return [f'{self.word.val} = {self.expr};']


class ExitStat(Stat):
    def __init__(self, expr, parent=None):
        super(ExitStat, self).__init__(parent=parent)
        self.expr: Expr = expr

    def traverse(self):
        return [('exit', self.expr.traverse())]

    def repr_lines(self):
        return [f'EXIT {self.expr}']


class Expr(NonTerminal):
    def __init__(self, fact, expr_, parent=None):
        super(Expr, self).__init__(parent=parent)
        self.fact: Fact = fact
        self.expr_: Optional[ExprTail, Epsilon] = expr_

    def traverse(self):
        return self.fact.traverse() + self.expr_.traverse()

    def repr_lines(self):
        return self.fact.repr_lines() + self.expr_.repr_lines()


class ExprTail(NonTerminal):
    def __init__(self, op, fact, expr_, parent=None):
        super(ExprTail, self).__init__(parent=parent)
        assert op in ['+', '*'], ValueError(f'Invalid op: {op}')
        self.op: str = op
        self.fact: Fact = fact
        self.expr_: Optional[ExprTail, Epsilon] = expr_

    def traverse(self):
        op_table = {'+': 'add', '*': 'mul'}
        return (op_table[self.op],) + self.fact.traverse() + self.expr_.traverse()

    def repr_lines(self):
        return [self.op] + self.fact.repr_lines() + self.expr_.repr_lines()


class Fact(NonTerminal):
    def __init__(self, value, parent=None):
        super(Fact, self).__init__(parent=parent)
        self.value: Optional[Word, Num] = value

    def traverse(self):
        return (self.value.traverse(),)

    def repr_lines(self):
        return [self.value]


class Terminal(Node):
    def __init__(self, val, parent=None):
        super(Terminal, self).__init__(parent=parent)
        self.val: Optional[str, int] = val

    def traverse(self):
        return self.val

    def repr_lines(self):
        return [self.val]


class Word(Terminal):
    pass


class Num(Terminal):
    pass
