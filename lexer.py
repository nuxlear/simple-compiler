import re


class Lexer:
    p_word = re.compile('[a-zA-Z]+')
    p_num = re.compile('[0-9]+')
    
    def __init__(self, input_path):
        self.input_path = input_path

    def scan(self):
        tokenList = []
        with open(self.input_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            tokens = line.strip().split(" ")
            for token in tokens:
                # if token.find('\n') != -1:
                #     token = token[0:-1]

                token_type = gettype(token)
                token_tuple = (token_type, token)

                if token_tuple[0] == "null":
                    if self.p_word.match(token):
                        token_tuple = ("word", token)
                    elif self.p_num.match(token):
                        token_tuple = ("num", token)
                    else:
                        token_tuple = ("null", token)
                        
                if token_tuple[0] != "null":
                    tokenList.append(token_tuple)

        return tokenList


def gettype(token):
    typeDict = {"(": "prog", ")": "prog", "{": "block", "}": "block", "IF": "stat", "THEN": "stat", "ELSE": "stat",
                "=": "stat", ";": "semi", "<": "cond", "+": "cond", "*": "cond", "int": "vtype", "char": "vtype"}
    return typeDict.get(token, "null")


if __name__ == '__main__':
    new_lexer = Lexer('input_code.txt')
    print(new_lexer.scan())
