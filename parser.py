import re
from node import *


class Tree_node:
    def __init__(self, val, parent):
        self.parent = parent
        self.val = val

    def __repr__(self):
        s = f'{self.val}'
        return s


class NonTerminal(Tree_node):
    def __init__(self, val, parent, child=None):
        super().__init__(val, parent)
        self.child = child or []

    def add(self, leaf):
        self.child.append(leaf)

    def __repr__(self):
        s = super().__repr__()
        if len(self.child) > 0:
            s += f' => {self.child}'
        return s


class Terminal(Tree_node):
    def __repr__(self):
        s = super().__repr__()
        return f'`{s}`'


class Parser:
    p_word = re.compile('[a-zA-Z]+')
    p_num = re.compile('[0-9]+')

    parse_table = {("prog", "p_word"): ["word", "(", ")", "block"], ("decls", "p_word"): ["decls_"],
                   ("decls", "IF"): ["decls_"], ("decls", "exit"): ["decls_"], ("decls", "$"): ["decls_"],
                   ("decls", "int"): ["decls_"],
                   ("decls", "char"): ["decls_"],("decls_", "p_word"): ["@"],
                   ("decls_", "IF"): ['@'], ("decls_", "EXIT"): ['@'], ("decls_", "$"): ['@'],
                   ("decls_", "int"): ["decl", "decls_"],
                   ("decls_", "char"): ["decl", "decls_"], ("decl", "int"): ["vtype", "word", ";"],
                   ("decl", "char"): ["vtype", "word", ";"],("decl", "p_word"): ["word", ";"],
                   ("decl", "$"): ['@'], ("vtype", "p_word"): ['@'], ("vtype", "int"): ["int"],
                   ("vtype", "char"): ["char"],
                   ("vtype", "$"): ['@'], ("block", "IF"): ['@'], ("block", "ELSE"): ['@'],
                   ("block", "EXIT"): ['@'],
                   ("block", "$"): ['@'], ("block", "{"): ["{", "decls", "slist", "}"],
                   ("slist", "p_word"): ["stat", "slist_"], ("slist", "IF"): ["stat", "slist_"],
                   ("slist", "EXIT"): ["stat", "slist_"],
                   ("slist", "}"): ['@'], ("slist", "$"): ['@'], ("slist_", "p_word"): ["stat", "slist_"],
                   ("slist_", "IF"): ["stat", "slist_"], ("slist_", "EXIT"): ["stat", "slist_"],
                   ("stat", "p_word"): ["word", "=", "expr", ";"],
                   ("stat", "IF"): ["IF", "cond", "THEN", "block", "ELSE", "block"],
                   ("stat", "EXIT"): ["EXIT", "expr", ";"], ("stat", "$"): ['@'], ("fact", "p_num"): ["num"],
                   ("fact", "p_word"): ["word"], ("cond", "p_word"): ["expr", "<", "expr"],
                   ("cond", "p_num"): ["expr", "<", "expr"], ("expr", "p_word"): ["fact", "expr_"],
                   ("expr_", "THEN"): ['@'],
                   ("expr", "p_num"): ["fact", "expr_"], ("expr_", ";"): ['@'], ("expr_", "<"): ['@'],
                   ("expr_", "+"): ["+", "fact", "expr_"],
                   ("expr_", "*"): ["*", "fact", "expr_"], ("word", "p_word"): ['p_word'],
                   ("num", "p_num"): ['p_num']
                   }
    non_ter = {"prog", "decls", "decls_", "decl", "vtype", "block", "slist", "slist_",
               "stat", "cond", "expr", "expr_", "fact", "word", "num"}

    def parse(self, input_list, debug=False):
        root_node = None
        stack = [Terminal("$", None), NonTerminal("prog", None)]
        i, j = 0, 0

        while True:
            j += 1
            if debug:
                for u in stack:
                    print(u.val, end=' ')
                print()
                if len(input_list) > i:
                    print(input_list[i][1])

            if len(input_list) > i:
                if stack[-1].val not in self.non_ter:
                    if stack[-1].val == input_list[i][1]:
                        nodes = stack.pop()
                        nodes.parent.add(nodes)
                        i += 1

                else:
                    key = None
                    gram = []
                    if self.p_word.match(input_list[i][1]):
                        key = (stack[-1].val, "p_word")
                    if self.p_num.match(input_list[i][1]):
                        key = (stack[-1].val, "p_num")
                    if key in self.parse_table:
                        gram = self.parse_table[key]
                    if key == ("decls_", "p_word"):
                        if input_list[i+1][1] == ";":
                            gram = ["decl", "decls_"]
                    key = (stack[-1].val, input_list[i][1])
                    if key in self.parse_table:
                        gram = self.parse_table[key]

                    nodes = stack.pop()
                    if nodes.parent is None:
                        root_node = nodes
                    else:
                        nodes.parent.add(nodes)

                    gram2 = reversed(gram)
                    if gram not in [['@'], ['p_word'], ['p_num']]:
                        for n in gram2:
                            node_cls = NonTerminal if n in self.non_ter else Terminal
                            d = node_cls(n, nodes)
                            stack.append(d)
                    elif gram != ['@']:
                        d = Terminal(input_list[i][1], nodes)
                        stack.append(d)

            else:
                if stack[-1].val == '$':
                    break
                if stack[-1].val == '@':
                    nodes = stack.pop()
                    nodes.parent.add(nodes)
                else:
                    raise ValueError(f'Invalid syntax')

        return root_node



def Maketree(origin_node):
    if origin_node.val == "word":
        nodes = Word(origin_node.child[0])
        return nodes
    if origin_node.val == "num":
        nodes = Num(origin_node.child[0])
        return nodes
    if origin_node.val == "fact":
        leaf = Maketree(origin_node.child[0])
        nodes = Fact(leaf)
        leaf.set_parent(nodes)
        return nodes
    if origin_node.val == "decl":
        if origin_node.child[1].val == ";":
            leaf = Maketree(origin_node.child[0])
            nodes = Decl(None, leaf)
            leaf.set_parent(nodes)
        else:
            leaf = Maketree(origin_node.child[1])
            nodes = Decl(origin_node.child[0].child[0].val, leaf)
            leaf.set_parent(nodes)
        return nodes
    if origin_node.val == "expr_":
        if not origin_node.child:
            nodes = Epsilon()
            return nodes
        leaf1 = Maketree(origin_node.child[1])
        leaf2 = Maketree(origin_node.child[2])
        nodes = ExprTail(origin_node.child[0].val,leaf1,leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "expr":
        leaf1 = Maketree(origin_node.child[0])
        leaf2 = Maketree(origin_node.child[1])
        nodes = Expr(leaf1,leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "cond":
        leaf1 = Maketree(origin_node.child[0])
        leaf2 = Maketree(origin_node.child[2])
        nodes = CondStat(leaf1, leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "stat":
        if not origin_node.child:
            nodes = Epsilon()
            return nodes
        elif origin_node.child[0].val == "IF":
            leaf1 = Maketree(origin_node.child[1])
            leaf2 = Maketree(origin_node.child[3])
            leaf3 = Maketree(origin_node.child[5])
            nodes = IfElseStat(leaf1,leaf2,leaf3)
            leaf1.set_parent(nodes)
            leaf2.set_parent(nodes)
            leaf3.set_parent(nodes)
        elif origin_node.child[0].val == "EXIT":
            leaf = Maketree(origin_node.child[1])
            nodes = ExitStat(leaf)
            leaf.set_parent(nodes)
        else:
            leaf1 = Maketree(origin_node.child[0])
            leaf2 = Maketree(origin_node.child[2])
            nodes = AssignStat(leaf1, leaf2)
            leaf1.set_parent(nodes)
            leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "slist":
        if not origin_node.child:
            nodes2 = Epsilon()
            nodes3 = Epsilon()
            nodes = Slist(nodes2,nodes3)
            nodes2.set_parent(nodes)
            nodes3.set_parent(nodes)
            return nodes
        leaf1 = Maketree(origin_node.child[0])
        leaf2 = Maketree(origin_node.child[1])
        nodes = Slist(leaf1, leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "slist_":
        if not origin_node.child:
            nodes = Epsilon()
            return nodes
        leaf1 = Maketree(origin_node.child[0])
        leaf2 = Maketree(origin_node.child[1])
        nodes = SlistTail(leaf1, leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "decls_":
        if not origin_node.child:
            nodes = Epsilon()
            return nodes
        leaf1 = Maketree(origin_node.child[0])
        leaf2 = Maketree(origin_node.child[1])
        nodes = DeclsTail(leaf1, leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "decls":
        if not origin_node.child:
            nodes2 = Epsilon()
            nodes = Decls(nodes2)
            nodes2.set_parent(nodes)
            return nodes
        leaf = Maketree(origin_node.child[0])
        nodes = Decls(leaf)
        leaf.set_parent(nodes)
        return nodes
    if origin_node.val == "block":
        leaf1 = Maketree(origin_node.child[1])
        leaf2 = Maketree(origin_node.child[2])
        nodes = Block(leaf1, leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "prog":
        leaf1 = Maketree(origin_node.child[0])
        leaf2 = Maketree(origin_node.child[3])
        nodes = Prog(leaf1, leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes



if __name__ == '__main__':
    p = Parser()
    root = p.parse(
        [('word', 'Main'), ('prog', '('), ('prog', ')'), ('block', '{'), ('vtype', 'int'), ('word', 'a'), ('semi', ';'),
         ('vtype', 'int'), ('word', 'b'), ('semi', ';'), ('vtype', 'int'), ('word', 'c'), ('semi', ';'), ('word', 'd'),
         ('semi', ';'), ('vtype', 'char'), ('word', 'ca'), ('semi', ';'), ('vtype', 'char'), ('word', 'cb'),
         ('semi', ';'), ('word', 'a'), ('stat', '='), ('num', '1'), ('semi', ';'), ('word', 'b'), ('stat', '='),
         ('num', '2'), ('semi', ';'), ('word', 'c'), ('stat', '='), ('num', '3'), ('semi', ';'), ('stat', 'IF'),
         ('word', 'a'), ('cond', '<'), ('word', 'b'), ('stat', 'THEN'), ('block', '{'), ('stat', 'IF'), ('word', 'b'),
         ('cond', '<'), ('word', 'c'), ('stat', 'THEN'), ('block', '{'), ('vtype', 'int'), ('word', 'a'), ('semi', ';'),
         ('word', 'a'), ('stat', '='), ('num', '4'), ('semi', ';'), ('word', 'c'), ('stat', '='), ('word', 'a'),
         ('cond', '*'), ('word', 'b'), ('semi', ';'), ('block', '}'), ('stat', 'ELSE'), ('block', '{'), ('word', 'c'),
         ('stat', '='), ('word', 'a'), ('cond', '+'), ('word', 'b'), ('semi', ';'), ('block', '}'), ('block', '}'),
         ('stat', 'ELSE'), ('block', '{'), ('word', 'c'), ('stat', '='), ('word', 'a'), ('semi', ';'), ('block', '}'),
         ('stat', 'IF'), ('word', 'a'), ('cond', '<'), ('num', '2'), ('stat', 'THEN'), ('block', '{'), ('word', 'ca'),
         ('stat', '='), ('word', 'SUCCESS'), ('semi', ';'), ('block', '}'), ('stat', 'ELSE'), ('block', '{'),
         ('word', 'ca'), ('stat', '='), ('word', 'FAIL'), ('semi', ';'), ('block', '}'), ('stat', 'IF'), ('num', '7'),
         ('cond', '<'), ('word', 'c'), ('stat', 'THEN'), ('block', '{'), ('word', 'cb'), ('stat', '='),
         ('word', 'SUCCESS'), ('semi', ';'), ('block', '}'), ('stat', 'ELSE'), ('block', '{'), ('word', 'cb'),
         ('stat', '='), ('word', 'FAIL'), ('semi', ';'), ('block', '}'), ('word', 'EXIT'), ('num', '0'), ('semi', ';'),
         ('block', '}')],

        debug=False)
    print(root)
    #root2 = Prog(root.child[0],root.child[3])
    root2 = Maketree(root)
    print(root2)

