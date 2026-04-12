import re
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
}

# Characters that are symbols (raw, for splitting)
SYMBOL_CHARS = set("{}()[].,;+-*/|=~<>&")


def _tokenize_line(line):
    """Split a single stripped line into tokens, handling string literals atomically."""
    tokens = []
    i = 0
    while i < len(line):
        ch = line[i]

        # String literal: consume everything up to the closing quote
        if ch == '"':
            j = line.index('"', i + 1)
            tokens.append(line[i:j + 1])
            i = j + 1

        # Symbol: emit as its own token
        elif ch in SYMBOL_CHARS:
            tokens.append(ch)
            i += 1

        # Whitespace: skip
        elif ch in (' ', '\t'):
            i += 1

        # Identifier or keyword or integer constant: consume run of non-special chars
        else:
            j = i
            while j < len(line) and line[j] not in SYMBOL_CHARS and line[j] not in (' ', '\t', '"'):
                j += 1
            tokens.append(line[i:j])
            i = j

    return tokens


class JackTokenizer:
    def __init__(self, input_file: str, output_file: str = None):
        """Tokenize the input .jack file.

        output_file: path for the *T.xml token output. If None, derived from input_file.
        """
        with open(input_file, "r") as f:
            raw_lines = f.readlines()

        self.tokens = []

        in_block_comment = False
        for raw in raw_lines:
            line = raw.rstrip('\n')

            # Handle block comments that span multiple lines
            if in_block_comment:
                if '*/' in line:
                    line = line[line.index('*/') + 2:]
                    in_block_comment = False
                else:
                    continue

            # Inline block comment  /* ... */ on one line
            while '/*' in line:
                before = line[:line.index('/*')]
                rest = line[line.index('/*'):]
                if '*/' in rest:
                    after = rest[rest.index('*/') + 2:]
                    line = before + after
                else:
                    line = before
                    in_block_comment = True
                    break

            # Strip single-line comment
            if '//' in line:
                # Be careful not to strip // inside a string literal
                # Scan character-by-character to find // outside quotes
                in_str = False
                for idx, ch in enumerate(line):
                    if ch == '"':
                        in_str = not in_str
                    elif ch == '/' and not in_str and idx + 1 < len(line) and line[idx + 1] == '/':
                        line = line[:idx]
                        break

            line = line.strip()
            if not line:
                continue

            self.tokens.extend(_tokenize_line(line))

        self.current_index = 0
        self.current_token = self.tokens[0] if self.tokens else None

        # Open token output file
        if output_file is None:
            output_file = input_file.replace(".jack", "T.xml")
        self._output_path = output_file
        self._out = open(output_file, "w")
        self._out.write("<tokens>\n")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def hasMoreTokens(self):
        """True when current_token has not yet been consumed."""
        return self.current_index < len(self.tokens)

    def advance(self):
        """Move to the next token (increment index first, then read)."""
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = None

    # ------------------------------------------------------------------
    # Token classification
    # ------------------------------------------------------------------

    def tokenType(self):
        tok = self.current_token
        if tok is None:
            return "UNKNOWN"
        if tok in keyword_table:
            return "KEYWORD"
        if tok in symbol_table:
            return "SYMBOL"
        if tok.lstrip('-').isdigit() and 0 <= int(tok) <= 32767:
            return "INT_CONST"
        if tok.startswith('"') and tok.endswith('"'):
            return "STRING_CONST"
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', tok):
            return "IDENTIFIER"
        return "UNKNOWN"

    def keyword(self):
        if self.tokenType() == "KEYWORD":
            return self.current_token
        return None

    def symbol(self):
        """Return the raw symbol character (not HTML-escaped)."""
        if self.tokenType() == "SYMBOL":
            return self.current_token
        return None

    def identifier(self):
        if self.tokenType() == "IDENTIFIER":
            return self.current_token
        return None

    def intVal(self):
        if self.tokenType() == "INT_CONST":
            return int(self.current_token)
        return None

    def stringVal(self):
        if self.tokenType() == "STRING_CONST":
            return self.current_token[1:-1]  # strip surrounding quotes
        return None

    # ------------------------------------------------------------------
    # Token output (writes to *T.xml)
    # ------------------------------------------------------------------

    def process(self):
        """Write the current token to the T.xml file and advance."""
        tt = self.tokenType()
        if tt == "KEYWORD":
            self._out.write(f"<keyword> {self.keyword()} </keyword>\n")
        elif tt == "SYMBOL":
            xml_sym = symbol_table[self.current_token]
            self._out.write(f"<symbol> {xml_sym} </symbol>\n")
        elif tt == "INT_CONST":
            self._out.write(f"<integerConstant> {self.intVal()} </integerConstant>\n")
        elif tt == "IDENTIFIER":
            self._out.write(f"<identifier> {self.identifier()} </identifier>\n")
        elif tt == "STRING_CONST":
            self._out.write(f"<stringConstant> {self.stringVal()} </stringConstant>\n")
        else:
            self._out.write(f"<!-- UNKNOWN token: {self.current_token} -->\n")
        self.advance()

    def close(self):
        self._out.write("</tokens>\n")
        self._out.close()
