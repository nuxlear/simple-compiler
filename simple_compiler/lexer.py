import re


class Lexer:
    """
    Lexer
    - 주어진 파일 경로로부터 텍스트를 읽어와 tokenize한다.
    - 띄어쓰기 이슈를 줄이기 위해 re.sub()으로 패턴을 인식해 tokenize한다.
    - 입력된 코드를 List[Tuple(token_type, token)] 형태의 token들로 반환한다.
    """
    p_word = re.compile('[a-zA-Z]+')
    p_num = re.compile('[0-9]+')
    
    def __init__(self, input_path):
        self.input_path = input_path

    def scan(self):
        tokenList = []
        with open(self.input_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            tokens = re.sub(r"([(){}<=+*;]|\w+)", r" \1 ", line.strip()).split(" ")
            for token in tokens:
                if token == "":
                    continue

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
    new_lexer = Lexer('../input_code.txt')
    print(new_lexer.scan())
