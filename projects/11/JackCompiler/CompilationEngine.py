import re
from SymbolTable import SymbolTable
from VMWriter import VMWriter

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static",
    "var", "int", "char", "boolean", "void", "true", "false", "null",
    "this", "let", "do", "if", "else", "while", "return",
}

SYMBOLS = set("{}()[].,;+-*/|=~<>&")

OPS = {
    '+': 'add',
    '-': 'sub',
    '*': 'call Math.multiply 2',
    '/': 'call Math.divide 2',
    '&': 'and',
    '|': 'or',
    '<': 'lt',
    '>': 'gt',
    '=': 'eq'
}

UNARY_OPS = {
    '-': 'neg',
    '~': 'not'
}

class CompilationEngine:
    def __init__(self, tokens: list, output_file: str):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = tokens[0] if tokens else None

        self.symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_file)

        self.class_name = ""
        self.label_counter = 0

        self.compileClass()
        self.vm_writer.close()

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

    def _consume(self, expected=None):
        tok = self.current_token
        if expected and tok != expected:
            raise SyntaxError(f"Expected {expected}, got {tok}")
        self._advance()
        return tok

    def _get_label(self, prefix):
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    # ------------------------------------------------------------------
    # Program structure
    # ------------------------------------------------------------------

    def compileClass(self):
        """class className '{' classVarDec* subroutineDec* '}'"""
        self._consume('class')
        self.class_name = self._consume() # className
        self._consume('{')

        while self.current_token in ('static', 'field'):
            self.compileClassVarDec()

        while self.current_token in ('constructor', 'function', 'method'):
            self.compileSubroutine()

        self._consume('}')

    def compileClassVarDec(self):
        """('static' | 'field') type varName (',' varName)* ';'"""
        kind = self._consume().upper() # 'static' or 'field'
        type_str = self._consume()     # type
        name = self._consume()         # varName
        self.symbol_table.define(name, type_str, kind)

        while self.current_token == ',':
            self._consume(',')
            name = self._consume()
            self.symbol_table.define(name, type_str, kind)

        self._consume(';')

    def compileSubroutine(self):
        """('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody"""
        self.symbol_table.reset()

        subroutine_type = self._consume() # 'constructor' / 'function' / 'method'
        if subroutine_type == 'method':
            self.symbol_table.define('this', self.class_name, 'ARG')

        return_type = self._consume()     # return type
        subroutine_name = self._consume() # subroutineName

        self._consume('(')
        self.compileParameterList()
        self._consume(')')

        # subroutineBody: '{' varDec* statements '}'
        self._consume('{')

        while self.current_token == 'var':
            self.compileVarDec()

        n_locals = self.symbol_table.varCount('VAR')
        self.vm_writer.writeFunction(f"{self.class_name}.{subroutine_name}", n_locals)

        if subroutine_type == 'constructor':
            n_fields = self.symbol_table.varCount('FIELD')
            self.vm_writer.writePush('CONST', n_fields)
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('POINTER', 0)
        elif subroutine_type == 'method':
            self.vm_writer.writePush('ARG', 0)
            self.vm_writer.writePop('POINTER', 0)

        self.compileStatements()
        self._consume('}')

    def compileParameterList(self):
        """((type varName) (',' type varName)*)?"""
        if self.current_token != ')':
            type_str = self._consume()
            name = self._consume()
            self.symbol_table.define(name, type_str, 'ARG')

            while self.current_token == ',':
                self._consume(',')
                type_str = self._consume()
                name = self._consume()
                self.symbol_table.define(name, type_str, 'ARG')

    def compileVarDec(self):
        """'var' type varName (',' varName)* ';'"""
        self._consume('var')
        type_str = self._consume()
        name = self._consume()
        self.symbol_table.define(name, type_str, 'VAR')

        while self.current_token == ',':
            self._consume(',')
            name = self._consume()
            self.symbol_table.define(name, type_str, 'VAR')

        self._consume(';')

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def compileStatements(self):
        """(letStatement | ifStatement | whileStatement | doStatement | returnStatement)*"""
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

    def compileLet(self):
        """'let' varName ('[' expression ']')? '=' expression ';'"""
        self._consume('let')
        var_name = self._consume()

        is_array = False
        if self.current_token == '[':
            is_array = True
            self._consume('[')
            self.compileExpression()
            self._consume(']')

            # push base address
            kind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)
            self.vm_writer.writePush(kind, index)

            # add base + offset
            self.vm_writer.writeArithmetic('add')

        self._consume('=')
        self.compileExpression()
        self._consume(';')

        if is_array:
            # pop value to temp 0
            self.vm_writer.writePop('TEMP', 0)
            # pop address to pointer 1 (THAT)
            self.vm_writer.writePop('POINTER', 1)
            # push value from temp 0
            self.vm_writer.writePush('TEMP', 0)
            # pop to THAT 0
            self.vm_writer.writePop('THAT', 0)
        else:
            kind = self.symbol_table.kindOf(var_name)
            index = self.symbol_table.indexOf(var_name)
            self.vm_writer.writePop(kind, index)

    def compileIf(self):
        """'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?"""
        label_true = self._get_label("IF_TRUE")
        label_false = self._get_label("IF_FALSE")
        label_end = self._get_label("IF_END")

        self._consume('if')
        self._consume('(')
        self.compileExpression()
        self._consume(')')

        self.vm_writer.writeIf(label_true)
        self.vm_writer.writeGoto(label_false)
        self.vm_writer.writeLabel(label_true)

        self._consume('{')
        self.compileStatements()
        self._consume('}')

        if self.current_token == 'else':
            self.vm_writer.writeGoto(label_end)
            self.vm_writer.writeLabel(label_false)
            self._consume('else')
            self._consume('{')
            self.compileStatements()
            self._consume('}')
            self.vm_writer.writeLabel(label_end)
        else:
            self.vm_writer.writeLabel(label_false)

    def compileWhile(self):
        """'while' '(' expression ')' '{' statements '}'"""
        label_exp = self._get_label("WHILE_EXP")
        label_end = self._get_label("WHILE_END")

        self.vm_writer.writeLabel(label_exp)

        self._consume('while')
        self._consume('(')
        self.compileExpression()
        self._consume(')')

        self.vm_writer.writeArithmetic('not')
        self.vm_writer.writeIf(label_end)

        self._consume('{')
        self.compileStatements()
        self._consume('}')

        self.vm_writer.writeGoto(label_exp)
        self.vm_writer.writeLabel(label_end)

    def compileDo(self):
        """'do' subroutineCall ';'"""
        self._consume('do')
        self._compileSubroutineCall()
        self._consume(';')
        self.vm_writer.writePop('TEMP', 0)

    def compileReturn(self):
        """'return' expression? ';'"""
        self._consume('return')
        if self.current_token != ';':
            self.compileExpression()
        else:
            self.vm_writer.writePush('CONST', 0)
        self._consume(';')
        self.vm_writer.writeReturn()

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def compileExpression(self):
        """term (op term)*"""
        self.compileTerm()
        while self.current_token in OPS:
            op = self._consume()
            self.compileTerm()

            if op == '*':
                self.vm_writer.writeCall('Math.multiply', 2)
            elif op == '/':
                self.vm_writer.writeCall('Math.divide', 2)
            else:
                self.vm_writer.writeArithmetic(OPS[op])


    def compileTerm(self):
        """integerConstant | stringConstant | keywordConstant
           | varName | varName '[' expression ']' | subroutineCall
           | '(' expression ')' | unaryOp term
        """
        tt = self._tokenType()
        tok = self.current_token

        if tt == 'INT_CONST':
            self.vm_writer.writePush('CONST', int(tok))
            self._advance()

        elif tt == 'STRING_CONST':
            string_val = tok[1:-1]
            self.vm_writer.writePush('CONST', len(string_val))
            self.vm_writer.writeCall('String.new', 1)
            for char in string_val:
                self.vm_writer.writePush('CONST', ord(char))
                self.vm_writer.writeCall('String.appendChar', 2)
            self._advance()

        elif tt == 'KEYWORD':
            if tok == 'true':
                self.vm_writer.writePush('CONST', 1)
                self.vm_writer.writeArithmetic('neg')
            elif tok in ('false', 'null'):
                self.vm_writer.writePush('CONST', 0)
            elif tok == 'this':
                self.vm_writer.writePush('POINTER', 0)
            self._advance()

        elif tt == 'IDENTIFIER':
            next_tok = self._peek_next()
            if next_tok == '[':
                # varName '[' expression ']'
                var_name = self._consume()
                self._consume('[')
                self.compileExpression()
                self._consume(']')

                kind = self.symbol_table.kindOf(var_name)
                index = self.symbol_table.indexOf(var_name)
                self.vm_writer.writePush(kind, index)
                self.vm_writer.writeArithmetic('add')
                self.vm_writer.writePop('POINTER', 1)
                self.vm_writer.writePush('THAT', 0)

            elif next_tok == '(' or next_tok == '.':
                # subroutineCall
                self._compileSubroutineCall()
            else:
                # plain varName
                var_name = self._consume()
                kind = self.symbol_table.kindOf(var_name)
                index = self.symbol_table.indexOf(var_name)
                self.vm_writer.writePush(kind, index)

        elif tok == '(':
            self._consume('(')
            self.compileExpression()
            self._consume(')')

        elif tok in UNARY_OPS:
            op = self._consume()
            self.compileTerm()
            self.vm_writer.writeArithmetic(UNARY_OPS[op])

    def compileExpressionList(self) -> int:
        """(expression (',' expression)*)?
        Returns the number of expressions compiled.
        """
        n_args = 0
        if self.current_token != ')':
            self.compileExpression()
            n_args += 1
            while self.current_token == ',':
                self._consume(',')
                self.compileExpression()
                n_args += 1
        return n_args

    # ------------------------------------------------------------------
    # Subroutine call helper
    # ------------------------------------------------------------------

    def _compileSubroutineCall(self):
        """subroutineName '(' expressionList ')'
           | (className | varName) '.' subroutineName '(' expressionList ')'
        """
        first_name = self._consume()

        n_args = 0
        func_name = ""

        if self.current_token == '.':
            self._consume('.')
            sub_name = self._consume()

            kind = self.symbol_table.kindOf(first_name)
            if kind != 'NONE':
                # It's a method call on an object (varName.subName)
                type_str = self.symbol_table.typeOf(first_name)
                index = self.symbol_table.indexOf(first_name)
                self.vm_writer.writePush(kind, index)
                func_name = f"{type_str}.{sub_name}"
                n_args += 1
            else:
                # It's a function call (ClassName.subName)
                func_name = f"{first_name}.{sub_name}"
        else:
            # It's a method call on 'this' (subName)
            self.vm_writer.writePush('POINTER', 0)
            func_name = f"{self.class_name}.{first_name}"
            n_args += 1

        self._consume('(')
        n_args += self.compileExpressionList()
        self._consume(')')

        self.vm_writer.writeCall(func_name, n_args)
