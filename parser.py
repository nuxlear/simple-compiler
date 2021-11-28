# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.



import re
p_word = re.compile('[a-zA-Z]+')
p_num  = re.compile('[0-9]')

parse_table = {("prog","p_word"): ["word","(",")","block"],("decls","p_word"): ['@'],
               ("decls","IF"): ['@'], ("decls","exit"): ['@'],("decls","$"): ['@'],("decls","int"): ["decls_"],
               ("decls","char"): ["decls_"],("decls_","p_word"): ["slist"],
               ("decls_","IF"): ['@'], ("decls_","EXIT"): ['@'],("decls_","$"): ['@'],("decls_","int"): ["decl","decls_"],
               ("decls_","char"): ["decl","decls_"],("decl","int"): ["vtype","word",";"],("decl","char"): ["vtype","word",";"],
               ("decl","$"): ['@'],("vtype","p_word"): ['@'],("vtype","int"): ["int"],("vtype","char"): ["char"],
               ("vtype","$"): ['@'],("block","IF"): ['@'],("block","ELSE"): ['@'],("block","EXIT"): ['@'],("block","$"): ['@'],("block","{"): ["{","decls","slist","}"],
               ("slist","p_word"): ["stat","slist_"],("slist","IF"): ["stat","slist_"],("slist","EXIT"): ["stat","slist_"],
               ("slist","}"): ['@'],("slist","$"): ['@'],("slist_","p_word"): ["stat","slist_"],
               ("slist_","IF"): ["stat","slist_"],("slist_","EXIT"): ["stat","slist_"],
               ("stat","p_word"): ["word","=","expr",";"],("stat","IF"): ["IF","cond","THEN","block","ELSE","block"],
               ("stat","EXIT"): ["EXIT","expr",";"],("stat","$"): ['@'],("fact","p_num"): ["num"],
               ("fact","p_word"): ["word"],("cond","p_word"): ["expr","<","expr"],("cond","THEN"): ["expr","<","expr"],
               ("cond","p_num"): ["expr","<","expr"],("expr","p_word"): ["fact","expr_"],
               ("expr","p_num"): ["fact","expr_"],("expr_",";"): ['@'],("expr_","<"): ['@'],("expr_","+"): ["+","fact","expr_"],
               ("expr_","*"): ["*","fact","expr_"],("word","p_word"):['p_word'],("num","p_num"):['p_num']
               }
non_ter ={"prog", "decls", "decls_", "decl", "vtype", "block", "slist", "slist_",
          "stat", "cond", "expr", "expr_", "fact", "word", "num"}

def parse(input_list):
    stack = ["$", "decls"]
    cur = None
    i = 0
    j = 0
    while j<80:
        j = j + 1
        print(stack)
        print(input_list[i][1])
        if len(input_list) > i:
            #token, terminal = stream.current()

            if not stack[-1] in non_ter:
                if stack[-1] == input_list[i][1]:
                    stack.pop()
                    i = i + 1

                #else:
                    #raise ValueError('token and grammar rule doesn\'t match: {} with {}'.format(terminal, gram))

            else:
                if p_word.match(input_list[i][1]):
                    key = (stack[-1], "p_word")
                if p_num.match(input_list[i][1]):
                    key = (stack[-1], "p_num")
                if key in parse_table:
                    gram = parse_table[key]
                key = (stack[-1], input_list[i][1])
                if key in parse_table:
                    gram = parse_table[key]

                #else:
                   #raise ValueError(
                        #'Parse Error: expected `{}` in next token.'.format(', '.join(self.first[stack[-1]])))
                stack.pop()
                gram2 = reversed(gram)
                if gram != ['@'] and gram != ['p_word'] and gram != ['p_num']:
                    #stack.extend([(t, cur) for t in gram[::-1]])
                    stack.extend(gram2)
                if gram == ['p_word']:
                    stack.extend(input_list[i][1])
                if gram == ['p_num']:
                    stack.extend(input_list[i][1])

        else:
            if stack[-1] == '$':
                break
            if stack[-1] == '@':
               stack.pop()
            else:
                raise ValueError('Parse Error: un-consumed token: {}'.format(stack[-1]))

    return 1
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parse([('vtype', 'int'), ('word', 'a'), ('semi', ';'), ('vtype', 'char'), ('word', 'b'), ('semi', ';'), ('vtype', 'int'), ('word', 'c'), ('semi', ';'), ('vtype', 'char'), ('word', 'd'), ('semi', ';'), ('vtype', 'int'), ('word', 'F'), ('semi', ';'), ('word', 'd'), ('stat', '='), ('num', '2'),('semi', ';') ,('word', 'c'), ('stat', '='), ('num', '1'),('semi', ';'), ('stat', 'IF'), ('word', 'c'), ('cond', '<'), ('word', 'd'), ('stat', 'THEN'), ('block', '{'), ('word', 'c'), ('stat', '='), ('num', '1'), ('block', '}'), ('stat', 'ELSE'), ('block', '{'), ('word', 'd'), ('stat', '='), ('num', '1'), ('block', '}'), ('word', 'F'), ('stat', '='), ('prog', '('), ('word', 'a'), ('cond', '+'), ('word', 'b'), ('prog', ')'), ('cond', '+'), ('word', 'c'), ('word', 'd'), ('stat', '='), ('word', 'ab'), ('cond', '+'), ('word', 'c')])

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
