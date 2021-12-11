import re
from simple_compiler.node import *


class TreeNode:
    """
    TreeNode
    - Parsing Tree의 node 객체.
    - Parser가 토큰을 처리하면서 TreeNode 타입의 트리 구조를 만들어 낸다.
    - 이후 Maketree() 함수를 통해 Syntax Tree 형태로 변환한다.
    """
    def __init__(self, val, parent):
        self.parent = parent
        self.val = val

    def __repr__(self):
        s = f'{self.val}'
        return s


class NonTerminalTN(TreeNode):
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


class TerminalTN(TreeNode):
    def __repr__(self):
        s = super().__repr__()
        return f'{s}'


class Parser:
    """
    Parser
    - 정해진 Grammar에 맞게 token들을 이해하고 Parsed Tree를 만들어낸다.
    - Grammar에 맞지 않아 parsing에 실패하는 경우 ValueError를 raise해 잘못된 syntax가 사용되었다는 것을 알린다.
    """
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
               ("fact", "p_word"): ["word"], ("cond", "p_word"): ["expr", "<", "expr"],("term_", "THEN"): ['@'],
               ("cond", "p_num"): ["expr", "<", "expr"], ("expr", "p_word"): ["term", "expr_"],
               ("expr_", "THEN"): ['@'],("term", "p_word"): ["fact", "term_"],("term", "p_num"): ["fact", "term_"],
               ("expr", "p_num"): ["term", "expr_"], ("expr_", ";"): ['@'], ("expr_", "<"): ['@'],
               ("expr_", "+"): ["+", "term", "expr_"],("term_", ";"): ['@'], ("term_", "<"): ['@'],
               ("term_", "*"): ["*", "fact", "term_"], ("word", "p_word"): ['p_word'],
               ("num", "p_num"): ['p_num']
               }
    non_ter = {"prog", "decls", "decls_", "decl", "vtype", "block", "slist", "slist_",
               "stat", "cond", "expr", "expr_", "fact", "word", "num", "term", "term_"}

    def parse(self, input_list, debug=False):
        root_node = None
        stack = [TerminalTN("$", None), NonTerminalTN("prog", None)]
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
                            node_cls = NonTerminalTN if n in self.non_ter else TerminalTN
                            d = node_cls(n, nodes)
                            stack.append(d)
                    elif gram != ['@']:
                        d = TerminalTN(input_list[i][1], nodes)
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
    """
    Maketree
    - Parsed Tree의 각 노드를 세부적인 타입으로 나뉘어져 있는 Syntax Tree 꼴로 변환해
      이후 code generation 작업이 원활하도록 하는 함수.
    :param origin_node: TreeNode 타입의 Parsed Tree
    :return: Node 타입의 Syntax Tree
    """
    if origin_node.val == "word":
        nodes = Word(origin_node.child[0].val)
        return nodes
    if origin_node.val == "num":
        nodes = Num(origin_node.child[0].val)
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
    if origin_node.val == "term_":
        if not origin_node.child:
            nodes = Epsilon()
            return nodes
        leaf1 = Maketree(origin_node.child[1])
        leaf2 = Maketree(origin_node.child[2])
        nodes = TermTail(origin_node.child[0].val,leaf1,leaf2)
        leaf1.set_parent(nodes)
        leaf2.set_parent(nodes)
        return nodes
    if origin_node.val == "term":
        leaf1 = Maketree(origin_node.child[0])
        leaf2 = Maketree(origin_node.child[1])
        nodes = Term(leaf1,leaf2)
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

    code = root2.traverse()
    for x in code:
        if x[0] == 'cond':
            print(x[0])
            print('T:', x[1])
            print('F:', x[2])
            continue
        print(x)

