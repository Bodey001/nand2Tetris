from multiprocessing import current_process
from operator import contains
import os

keyword_table = {
    "class": "CLASS",
    "constructor": "CONSTRUCTOR",
    "function": "FUNCTION",
    "method": "METHOD",
    "field": "FIELD",
    "static": "STATIC",
    "var": "VAR",
    "int": "INT",
    "char": "CHAR",
    "boolean": "BOOLEAN",
    "void": "VOID",
    "true": "TRUE",
    "false": "FALSE",
    "null": "NULL",
    "this": "THIS",
    "let": "LET",
    "do": "DO",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "return": "RETURN",
}
# symbol_tokens = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]

symbol_table = {
    "{": "{",
    "}": "}",
    "(": "(",
    ")": ")",
    "[": "[",
    "]": "]",
    ".": ".",
    ",": ",",
    ";": ";",
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    "|": "|",
    "=": "=",
    "~": "~",
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
    '"': "&quot;",
}

class JackTokenizer():
    def __init__(self, input_file: str):
        # opens the input .jack file and gets ready to tokenize it.
       # Open the file
        with open(input_file, "r") as file:
            raw_lines = file.readlines()

        self.tokens = []

        # Read the file
        for line in raw_lines:
            # Remove comments and whitespaces
            # if the line contains a comment, remove the comment
            if "//" in line:
                line = line.split("//")[0].strip()
            # if the line contains a comment, remove the comment
            elif "/**" in line:
                line = line.split("/**")[0].strip()
            # if the line contains a comment, remove the comment
            elif "/**" in line and "*/" in line:
                line = line.split("/**")[0].strip() + line.split("*/")[1].strip()
            elif "*" in line:
                line = line.split("*")[0].strip()
            elif "*/" in line:
                line = line.split("*/")[1].strip()
            elif '\n' in line:
                line = line.split('\n')[0].strip()
            # if the line is not empty, add the line to the tokens

            if line:
                for symbol in symbol_table:
                    line = line.replace(symbol, f" {symbol} ")
                tokens_per_line = line.split()
                for index, token in enumerate(tokens_per_line):
                    # if the token starts with a quote and the next token endswith a quote, combine the two tokens
                    if token.startswith('"') and tokens_per_line[index + 1].endswith('"'):
                        token = token + " " + tokens_per_line[index + 1]
                        self.tokens.append(token.strip())
                    elif token.endswith('"'):
                        # skip the next token
                        continue
                    else:
                        self.tokens.append(token.strip())


        print("\n\ntokens: ", self.tokens)
        self.current_token = None
        self.current_index = 0

       # opens the output file and gets ready to write to it.
        self.output_file = open(input_file.replace(".jack", "-analysisT.xml"), "w")
        self.output_file.write("<tokens>")

    def hasMoreTokens(self):
        # are there more tokens in the input
        return self.current_index < len(self.tokens)

    def advance(self):
        if self.hasMoreTokens():
            #gets the next token from the input and sets it as the current token
            self.current_token = self.tokens[self.current_index]
            self.current_index += 1

    def tokenType(self):
        # returns the type of the current token
        # if current token is a keyword
        if self.current_token in keyword_table.keys():
            return "KEYWORD"
        # if current token is a symbol
        elif self.current_token in symbol_table.keys():
            return "SYMBOL"
        # if current token is an integer constant betwen 0 and 32767
        elif self.current_token.isdigit() and int(self.current_token) >= 0 and int(self.current_token) <= 32767:
            return "INT_CONST"
        # if current token is an identifier (a sequence of letters, digits, and underscores, not starting with a digit)
        elif self.current_token.isalpha() and not self.current_token.isdigit():
            return "IDENTIFIER"
        # if current token is a string constant (a sequence of characters not including the double quote or newline)
        elif self.current_token.startswith('"') and self.current_token.endswith('"'):
            return "STRING_CONST"
        # if current token is unknown
        else:
            return "UNKNOWN"

    # if tokenType is KEYWORD, returns the keyword of the current token
    def keyword(self):
        # returns the keyword of the current token
        if self.tokenType() == "KEYWORD":
            return f" {self.current_token} "
        else:
            return "UNKNOWN"

    # if tokenType is SYMBOL, returns the symbol of the current token
    def symbol(self):
        # returns the symbol of the current token
        if self.tokenType() == "SYMBOL":
            return f" {symbol_table[self.current_token]} "
        else:
            return "UNKNOWN"

    def identifier(self):
        if self.tokenType() == "IDENTIFIER":
            return f" {self.current_token} "
        else:
            return "UNKNOWN"

    # if tokenType is INT_CONST, returns the integer constant of the current token
    def intVal(self):
        if self.tokenType() == "INT_CONST":
            return f" {int(self.current_token)} "
        else:
            return "UNKNOWN"

    # if tokenType is STRING_CONST, returns the string constant of the current token
    def stringVal(self):
        if self.tokenType() == "STRING_CONST":
            return f" {self.current_token.strip('"')} "
        else:
            return "UNKNOWN"

    def process(self):
        # process the given string
        if self.tokenType() == "KEYWORD":
            self.output_file.write("\n<keyword>")
            self.output_file.write(self.keyword())
            self.output_file.write("</keyword>")
        elif self.tokenType() == "SYMBOL":
            self.output_file.write("\n<symbol>")
            self.output_file.write(self.symbol())
            self.output_file.write("</symbol>")
        elif self.tokenType() == "INT_CONST":
            self.output_file.write("\n<integerConstant>")
            self.output_file.write(str(self.intVal()))
            self.output_file.write("</integerConstant>")
        elif self.tokenType() == "IDENTIFIER":
            self.output_file.write("\n<identifier>")
            self.output_file.write(self.identifier())
            self.output_file.write("</identifier>")
        elif self.tokenType() == "STRING_CONST":
            self.output_file.write("\n<stringConstant>")
            self.output_file.write(self.stringVal())
            self.output_file.write("</stringConstant>")
        else:
            self.output_file.write("\nsyntax error")

    # closes the output file
    def close(self):
        self.output_file.write("\n</tokens>")
        self.output_file.close()
