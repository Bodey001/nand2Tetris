class SymbolTable:
    """
    Acts as the compiler's memory. It tracks variable declarations across two scopes:
    Class-level scope (STATIC, FIELD) and Subroutine-level scope (ARG, VAR).
    """

    def __init__(self):
        """Creates a new empty symbol table."""
        self.class_table = {}
        self.subroutine_table = {}
        self.counts = {
            'STATIC': 0,
            'FIELD': 0,
            'ARG': 0,
            'VAR': 0
        }

    def reset(self):
        """
        Empties the subroutine-level symbol table and resets the ARG and VAR indexes to 0.
        Must be called every time compilation of a new subroutine begins.
        """
        self.subroutine_table.clear()
        self.counts['ARG'] = 0
        self.counts['VAR'] = 0

    def define(self, name: str, type: str, kind: str):
        """
        Defines (adds to the table) a new variable of the given name, type, and kind
        (STATIC, FIELD, ARG, or VAR). Assigns it the next available index for that kind
        and increments the index.
        """
        index = self.counts[kind]
        self.counts[kind] += 1
        
        if kind in ('STATIC', 'FIELD'):
            self.class_table[name] = {'type': type, 'kind': kind, 'index': index}
        elif kind in ('ARG', 'VAR'):
            self.subroutine_table[name] = {'type': type, 'kind': kind, 'index': index}

    def varCount(self, kind: str) -> int:
        """Returns the number of variables of the given kind currently defined in the table."""
        return self.counts.get(kind, 0)

    def kindOf(self, name: str) -> str:
        """
        Returns the kind of the named identifier (STATIC, FIELD, ARG, VAR).
        If the identifier is not found, returns NONE.
        """
        if name in self.subroutine_table:
            return self.subroutine_table[name]['kind']
        if name in self.class_table:
            return self.class_table[name]['kind']
        return 'NONE'

    def typeOf(self, name: str) -> str:
        """Returns the type of the named variable (e.g., int, boolean, Square)."""
        if name in self.subroutine_table:
            return self.subroutine_table[name]['type']
        if name in self.class_table:
            return self.class_table[name]['type']
        return ''

    def indexOf(self, name: str) -> int:
        """Returns the index assigned to the named variable."""
        if name in self.subroutine_table:
            return self.subroutine_table[name]['index']
        if name in self.class_table:
            return self.class_table[name]['index']
        return -1
