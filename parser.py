# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



import re


class arser:
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
        stack = ["$", "prog"]
        cur = None
        i = 0
        j = 0
        while j<160:
            j = j + 1
            print(stack)
            if len(input_list) > i:
                print(input_list[i][1])
            if len(input_list) > i:
                #token, terminal = stream.current()

                if not stack[-1] in self.non_ter:
                    if stack[-1] == input_list[i][1]:
                        stack.pop()
                        i = i + 1

                    #else:
                        #raise ValueError('token and grammar rule doesn\'t match: {} with {}'.format(terminal, gram))

                else:
                    if self.p_word.match(input_list[i][1]):
                        key = (stack[-1], "p_word")
                    if self.p_num.match(input_list[i][1]):
                        key = (stack[-1], "p_num")
                    if key in self.parse_table:
                        gram = self.parse_table[key]
                    key = (stack[-1], input_list[i][1])
                    if key in self.parse_table:
                        gram = self.parse_table[key]

                    #else:
                       #raise ValueError(
                            #'Parse Error: expected `{}` in next token.'.format(', '.join(self.first[stack[-1]])))
                    stack.pop()
                    gram2 = reversed(gram)
                    if gram != ['@'] and gram != ['p_word'] and gram != ['p_num']:
                        #stack.extend([(t, cur) for t in gram[::-1]])
                        stack.extend(gram2)
                    if gram == ['p_word']:
                        stack.append(input_list[i][1])
                    if gram == ['p_num']:
                        stack.append(input_list[i][1])

            else:
                if stack[-1] == '$':
                    break
                if stack[-1] == '@':
                   stack.pop()
                else:
                    print("haha")

        return 1
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    p = Parser();
    p.parse([('word', 'func'), ('prog', '('), ('prog', ')'), ('block', '{'), ('vtype', 'int'), ('word', 'a'), ('semi', ';'), ('vtype', 'int'), ('word', 'b'), ('semi', ';'), ('vtype', 'int'), ('word', 'c'), ('semi', ';'),  ('vtype', 'int'), ('word', 'dd'), ('semi', ';'),  ('word', 'a'), ('stat', '='), ('num', '3'), ('semi', ';'),  ('word', 'b'), ('stat', '='), ('num', '2'), ('semi', ';'), ('stat', 'IF'), ('word', 'a'), ('cond', '<'), ('word', 'b'), ('stat', 'THEN'), ('block', '{'), ('word', 'c'), ('stat', '='), ('num', '1'), ('semi', ';'), ('block', '}'), ('stat', 'ELSE'), ('block', '{'), ('word', 'c'), ('stat', '='), ('num', '2'), ('semi', ';'), ('block', '}'),  ('word', 'dd'), ('stat', '='), ('word', 'a'), ('cond', '+'), ('word', 'c'), ('semi', ';'), ('block', '}')])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
