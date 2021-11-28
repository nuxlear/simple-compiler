# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import re


class Node:

    def __init__(self, val, parent):
        self.parent = parent
        self.val = val

        self.child = []

    def add(self, leaf):
        self.child.append(leaf)


class Parser():
    p_word = re.compile('[a-zA-Z]+')
    p_num = re.compile('[0-9]')

    parse_table = {("prog", "p_word"): ["word", "(", ")", "block"], ("decls", "p_word"): ['@'],
                   ("decls", "IF"): ['@'], ("decls", "exit"): ['@'], ("decls", "$"): ['@'],
                   ("decls", "int"): ["decls_"],
                   ("decls", "char"): ["decls_"], ("decls_", "p_word"): ["slist"],
                   ("decls_", "IF"): ['@'], ("decls_", "EXIT"): ['@'], ("decls_", "$"): ['@'],
                   ("decls_", "int"): ["decl", "decls_"],
                   ("decls_", "char"): ["decl", "decls_"], ("decl", "int"): ["vtype", "word", ";"],
                   ("decl", "char"): ["vtype", "word", ";"],
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

    def parse(self, input_list):
        a = Node("$", None)
        b = Node("prog", None)
        stack = []
        stack.append(a)
        stack.append(b)
        i = 0
        j = 0
        while True:
            j = j + 1
            for u in stack:
                print(u.val, end=' ')
            print()
            if len(input_list) > i:
                print(input_list[i][1])
            if len(input_list) > i:
                if not stack[-1].val in self.non_ter:
                    if stack[-1].val == input_list[i][1]:
                        nodes = stack.pop()
                        nodes.parent.add(nodes)
                        i = i + 1
                else:
                    if self.p_word.match(input_list[i][1]):
                        key = (stack[-1].val, "p_word")
                    if self.p_num.match(input_list[i][1]):
                        key = (stack[-1].val, "p_num")
                    if key in self.parse_table:
                        gram = self.parse_table[key]
                    key = (stack[-1].val, input_list[i][1])
                    if key in self.parse_table:
                        gram = self.parse_table[key]
                    nodes = stack.pop()
                    if nodes.parent == None:
                        root_node = nodes
                    else:
                        nodes.parent.add(nodes)
                    gram2 = reversed(gram)
                    if gram != ['@'] and gram != ['p_word'] and gram != ['p_num']:
                        for n in gram2:
                            d = Node(n,nodes)
                            stack.append(d)
                    if gram == ['p_word']:
                        d = Node(input_list[i][1], nodes)
                        stack.append(d)
                        #stack.append(input_list[i][1])
                    if gram == ['p_num']:
                        d = Node(input_list[i][1], nodes)
                        stack.append(d)
                        #stack.append(input_list[i][1])

            else:
                if stack[-1].val == '$':
                    break
                if stack[-1].val == '@':
                   nodes = stack.pop()
                   nodes.parent.add(nodes)
                else:
                    print("haha")

        return root_node


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    p = Parser()
    root = p.parse(
        [('word', 'func'), ('prog', '('), ('prog', ')'), ('block', '{'), ('vtype', 'int'), ('word', 'a'), ('semi', ';'),
         ('vtype', 'int'), ('word', 'b'), ('semi', ';'), ('vtype', 'int'), ('word', 'c'), ('semi', ';'),
         ('vtype', 'int'), ('word', 'dd'), ('semi', ';'), ('word', 'a'), ('stat', '='), ('num', '3'), ('semi', ';'),
         ('word', 'b'), ('stat', '='), ('num', '2'), ('semi', ';'), ('stat', 'IF'), ('word', 'a'), ('cond', '<'),
         ('word', 'b'), ('stat', 'THEN'), ('block', '{'), ('word', 'c'), ('stat', '='), ('num', '1'), ('semi', ';'),
         ('block', '}'), ('stat', 'ELSE'), ('block', '{'), ('word', 'c'), ('stat', '='), ('num', '2'), ('semi', ';'),
         ('block', '}'), ('word', 'dd'), ('stat', '='), ('word', 'a'), ('cond', '+'), ('word', 'c'), ('semi', ';'),
         ('block', '}')])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
