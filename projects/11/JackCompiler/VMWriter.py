class VMWriter:
    """
    A helper module that encapsulates the syntax of the VM language,
    allowing the engine to emit VM commands using simple method calls.
    """

    def __init__(self, output_file: str):
        """Creates a new file and prepares it for writing."""
        self._out = open(output_file, 'w')

    def writePush(self, segment: str, index: int):
        """
        Writes a VM push command.
        Valid segments: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP.
        """
        seg = self._map_segment(segment)
        self._out.write(f"push {seg} {index}\n")

    def writePop(self, segment: str, index: int):
        """Writes a VM pop command."""
        seg = self._map_segment(segment)
        self._out.write(f"pop {seg} {index}\n")

    def writeArithmetic(self, command: str):
        """
        Writes a VM arithmetic/logical command.
        Valid commands: ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT.
        """
        self._out.write(f"{command.lower()}\n")

    def writeLabel(self, label: str):
        """Writes a VM label command."""
        self._out.write(f"label {label}\n")

    def writeGoto(self, label: str):
        """Writes a VM unconditional goto command."""
        self._out.write(f"goto {label}\n")

    def writeIf(self, label: str):
        """Writes a VM conditional if-goto command."""
        self._out.write(f"if-goto {label}\n")

    def writeCall(self, name: str, nArgs: int):
        """Writes a VM call command."""
        self._out.write(f"call {name} {nArgs}\n")

    def writeFunction(self, name: str, nLocals: int):
        """Writes a VM function command."""
        self._out.write(f"function {name} {nLocals}\n")

    def writeReturn(self):
        """Writes a VM return command."""
        self._out.write("return\n")

    def close(self):
        """Closes the output file."""
        self._out.close()

    def _map_segment(self, segment: str) -> str:
        """Maps Jack segments/kinds to VM segments."""
        seg = segment.upper()
        if seg == 'CONST':
            return 'constant'
        if seg == 'ARG':
            return 'argument'
        if seg == 'LOCAL' or seg == 'VAR':
            return 'local'
        if seg == 'STATIC':
            return 'static'
        if seg == 'THIS' or seg == 'FIELD':
            return 'this'
        if seg == 'THAT':
            return 'that'
        if seg == 'POINTER':
            return 'pointer'
        if seg == 'TEMP':
            return 'temp'
        return segment.lower()
