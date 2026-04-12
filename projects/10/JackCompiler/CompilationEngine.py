"""CompilationEngine – recursive descent parser for the Jack language.

Takes a list of tokens produced by JackTokenizer and writes a structured
XML parse tree to the given output file.
"""

import re

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static",
    "var", "int", "char", "boolean", "void", "true", "false", "null",
    "this", "let", "do", "if", "else", "while", "return",
}

SYMBOLS = set("{}()[].,;+-*/|=~<>&")

# Symbols that need XML escaping when written to the output file
_XML_ESCAPE = {'<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot'}

# Binary operators
OPS = set('+-*/&|<>=')


class CompilationEngine:
    # ------------------------------------------------------------------
    # Construction & teardown
    # ------------------------------------------------------------------

    def __init__(self, tokens: list, output_file: str):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = tokens[0] if tokens else None
        self._indent = 0
        self._out = open(output_file, 'w')
        self.compileClass()
        self._out.close()

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _advance(self):
        self.current_index += 1
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
        else:
            self.current_token = None

    def _peek_next(self):
        """Return the token AFTER the current one without advancing."""
        i = self.current_index + 1
        return self.tokens[i] if i < len(self.tokens) else None

    def _tokenType(self):
        tok = self.current_token
        if tok is None:
            return None
        if tok in KEYWORDS:
            return 'KEYWORD'
        if tok in SYMBOLS:
            return 'SYMBOL'
        if re.match(r'^\d+$', tok) and 0 <= int(tok) <= 32767:
            return 'INT_CONST'
        if tok.startswith('"') and tok.endswith('"'):
            return 'STRING_CONST'
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', tok):
            return 'IDENTIFIER'
        return None

    def _xml_sym(self, sym):
        return _XML_ESCAPE.get(sym, sym)

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def _open(self, tag):
        """Write an opening structural tag and increase indentation."""
        self._out.write('  ' * self._indent + f'<{tag}>\n')
        self._indent += 1

    def _close(self, tag):
        """Decrease indentation and write a closing structural tag."""
        self._indent -= 1
        self._out.write('  ' * self._indent + f'</{tag}>\n')

    def _write_token(self, tag, value):
        self._out.write('  ' * self._indent + f'<{tag}> {value} </{tag}>\n')

    def _process(self):
        """Write the current token to the XML output and advance."""
        tt = self._tokenType()
        tok = self.current_token
        if tt == 'KEYWORD':
            self._write_token('keyword', tok)
        elif tt == 'SYMBOL':
            self._write_token('symbol', self._xml_sym(tok))
        elif tt == 'INT_CONST':
            self._write_token('integerConstant', tok)
        elif tt == 'IDENTIFIER':
            self._write_token('identifier', tok)
        elif tt == 'STRING_CONST':
            self._write_token('stringConstant', tok[1:-1])
        self._advance()

    # ------------------------------------------------------------------
    # Program structure
    # ------------------------------------------------------------------

    def compileClass(self):
        """class className '{' classVarDec* subroutineDec* '}'"""
        self._open('class')
        self._process()                    # 'class'
        self._process()                    # className
        self._process()                    # '{'
        while self.current_token in ('static', 'field'):
            self.compileClassVarDec()
        while self.current_token in ('constructor', 'function', 'method'):
            self.compileSubroutine()
        self._process()                    # '}'
        self._close('class')

    def compileClassVarDec(self):
        """('static' | 'field') type varName (',' varName)* ';'"""
        self._open('classVarDec')
        self._process()                    # 'static' or 'field'
        self._process()                    # type
        self._process()                    # varName
        while self.current_token == ',':
            self._process()                # ','
            self._process()                # varName
        self._process()                    # ';'
        self._close('classVarDec')

    def compileSubroutine(self):
        """('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody"""
        self._open('subroutineDec')
        self._process()                    # 'constructor' / 'function' / 'method'
        self._process()                    # return type
        self._process()                    # subroutineName
        self._process()                    # '('
        self.compileParameterList()
        self._process()                    # ')'
        self._compileSubroutineBody()
        self._close('subroutineDec')

    def compileParameterList(self):
        """((type varName) (',' type varName)*)?"""
        self._open('parameterList')
        if self.current_token != ')':
            self._process()                # type
            self._process()                # varName
            while self.current_token == ',':
                self._process()            # ','
                self._process()            # type
                self._process()            # varName
        self._close('parameterList')

    def _compileSubroutineBody(self):
        """{' varDec* statements '}'"""
        self._open('subroutineBody')
        self._process()                    # '{'
        while self.current_token == 'var':
            self.compileVarDec()
        self.compileStatements()
        self._process()                    # '}'
        self._close('subroutineBody')

    def compileVarDec(self):
        """'var' type varName (',' varName)* ';'"""
        self._open('varDec')
        self._process()                    # 'var'
        self._process()                    # type
        self._process()                    # varName
        while self.current_token == ',':
            self._process()                # ','
            self._process()                # varName
        self._process()                    # ';'
        self._close('varDec')

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def compileStatements(self):
        """(letStatement | ifStatement | whileStatement | doStatement | returnStatement)*"""
        self._open('statements')
        while self.current_token in ('let', 'if', 'while', 'do', 'return'):
            if self.current_token == 'let':
                self.compileLet()
            elif self.current_token == 'if':
                self.compileIf()
            elif self.current_token == 'while':
                self.compileWhile()
            elif self.current_token == 'do':
                self.compileDo()
            elif self.current_token == 'return':
                self.compileReturn()
        self._close('statements')

    def compileLet(self):
        """'let' varName ('[' expression ']')? '=' expression ';'"""
        self._open('letStatement')
        self._process()                    # 'let'
        self._process()                    # varName
        if self.current_token == '[':
            self._process()                # '['
            self.compileExpression()
            self._process()                # ']'
        self._process()                    # '='
        self.compileExpression()
        self._process()                    # ';'
        self._close('letStatement')

    def compileIf(self):
        """'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?"""
        self._open('ifStatement')
        self._process()                    # 'if'
        self._process()                    # '('
        self.compileExpression()
        self._process()                    # ')'
        self._process()                    # '{'
        self.compileStatements()
        self._process()                    # '}'
        if self.current_token == 'else':
            self._process()                # 'else'
            self._process()                # '{'
            self.compileStatements()
            self._process()                # '}'
        self._close('ifStatement')

    def compileWhile(self):
        """'while' '(' expression ')' '{' statements '}'"""
        self._open('whileStatement')
        self._process()                    # 'while'
        self._process()                    # '('
        self.compileExpression()
        self._process()                    # ')'
        self._process()                    # '{'
        self.compileStatements()
        self._process()                    # '}'
        self._close('whileStatement')

    def compileDo(self):
        """'do' subroutineCall ';'"""
        self._open('doStatement')
        self._process()                    # 'do'
        self._compileSubroutineCall()
        self._process()                    # ';'
        self._close('doStatement')

    def compileReturn(self):
        """'return' expression? ';'"""
        self._open('returnStatement')
        self._process()                    # 'return'
        if self.current_token != ';':
            self.compileExpression()
        self._process()                    # ';'
        self._close('returnStatement')

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def compileExpression(self):
        """term (op term)*"""
        self._open('expression')
        self.compileTerm()
        while self.current_token in OPS:
            self._process()                # op
            self.compileTerm()
        self._close('expression')

    def compileTerm(self):
        """integerConstant | stringConstant | keywordConstant
           | varName | varName '[' expression ']' | subroutineCall
           | '(' expression ')' | unaryOp term
        """
        self._open('term')
        tt = self._tokenType()

        if tt == 'INT_CONST':
            self._process()

        elif tt == 'STRING_CONST':
            self._process()

        elif tt == 'KEYWORD':
            # keywordConstant: true, false, null, this
            self._process()

        elif tt == 'IDENTIFIER':
            next_tok = self._peek_next()
            if next_tok == '[':
                # varName '[' expression ']'
                self._process()            # varName
                self._process()            # '['
                self.compileExpression()
                self._process()            # ']'
            elif next_tok == '(' or next_tok == '.':
                # subroutineCall inside a term
                self._compileSubroutineCall()
            else:
                # plain varName
                self._process()

        elif self.current_token == '(':
            # '(' expression ')'
            self._process()                # '('
            self.compileExpression()
            self._process()                # ')'

        elif self.current_token in ('-', '~'):
            # unaryOp term
            self._process()                # unaryOp
            self.compileTerm()

        self._close('term')

    def compileExpressionList(self):
        """(expression (',' expression)*)?"""
        self._open('expressionList')
        if self.current_token != ')':
            self.compileExpression()
            while self.current_token == ',':
                self._process()            # ','
                self.compileExpression()
        self._close('expressionList')

    # ------------------------------------------------------------------
    # Subroutine call helper (shared by compileDo and compileTerm)
    # ------------------------------------------------------------------

    def _compileSubroutineCall(self):
        """subroutineName '(' expressionList ')'
           | (className | varName) '.' subroutineName '(' expressionList ')'
        Written inline (no enclosing tag) so it can be embedded in doStatement
        and term without an extra wrapper.
        """
        self._process()                    # subroutineName / className / varName
        if self.current_token == '.':
            self._process()                # '.'
            self._process()                # subroutineName
        self._process()                    # '('
        self.compileExpressionList()
        self._process()                    # ')'
