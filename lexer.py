# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import re


class lexer:
    def scan(self):
        tokkenList = []
        f = open("test.txt", "r")
        p_word = re.compile('[a-zA-Z]+')
        p_num = re.compile('[0-9]')
        lines = f.readlines()
        
        for line in lines:
            tokkens = line.split(" ")
            for tokken in tokkens:
                if tokken.find('\n') != -1:
                    tokken = tokken[0:-1]
                    
                if p_word.match(tokken):
                    tokken_tuple = ("word", tokken)
                elif p_num.match(tokken):
                    tokken_tuple = ("num", tokken)
                else:
                    tokken_type = gettype(tokken)
                    tokken_tuple = (tokken_type, tokken)
                tokkenList.append(tokken_tuple)
        f.close()

        return tokkenList


def gettype(tokken):
    typeDict = {"(": "prog", ")": "prog", "{": "block", "}": "block", "IF": "stat", "THEN": "stat", "ELSE": "stat",
                "=": "stat", ";": "stat", "<": "cond", "+": "cond", "*": "cond"}
    return typeDict.get(tokken, "null")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    new_lexer = lexer()
    print(new_lexer.scan())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
