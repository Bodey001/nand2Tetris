import re

# Command type
A_COMMAND = 0
C_COMMAND = 1
L_COMMAND = 2

A_COMMAND_PATTERN = re.compile(r'@([0-9a-zA-Z_\.\$:]+)')
L_COMMAND_PATTERN = re.compile(r'\(([0-9a-zA-Z_\.\$:]*)\)')
C_COMMAND_PATTERN = re.compile(r'(?:(A?M?D?)=)?([^;]+)(?:;(.+))?')

class HackParser():

    def __init__(self, filepath: str):
        with open(filepath, 'r') as file:
            raw_lines = file.readlines()

        self.commands = []

        for line in raw_lines:
            # Remove comments and whitespaces
            line = line.split("//")[0].strip()
            if line:
                self.commands.append(line)

        self.current_command = None
        self.current_index = 0

    def hasMoreLines(self):
        return self.current_index < len(self.commands)

    def advance(self):
        if self.hasMoreLines():
            self.current_command = self.commands[self.current_index]
            self.current_index += 1

    def instructionType(self):
        if self.current_command[0] == '@':
            return A_COMMAND
        elif self.current_command[0] == '(' and self.current_command[-1] == ')':
            return L_COMMAND
        else:
            return C_COMMAND

    def symbol(self):
        ins_type = self.instructionType()
        if ins_type == A_COMMAND:
            m = A_COMMAND_PATTERN.match(self.current_command)
            if not m:
                raise Exception("Parsing symbol failed")
            return m.group(1)

        elif ins_type == L_COMMAND:
            m = L_COMMAND_PATTERN.match(self.current_command)
            if not m:
                raise Exception("Parsing symbol failed")
            return m.group(1)

        else:
            raise Exception("Current instruction is not A_COMMAND or L_COMMAND")

    def dest(self):
        ins_type = self.instructionType()
        if ins_type == C_COMMAND:
            m = C_COMMAND_PATTERN.match(self.current_command)
            return m.group(1)
        else:
            raise Exception('Current command is not C_COMMAND')

    def comp(self):
        ins_type = self.instructionType()
        if ins_type == C_COMMAND:
            m = C_COMMAND_PATTERN.match(self.current_command)
            return m.group(2)
        else:
            raise Exception("Current command is not C_COMMAND")

    def jump(self):
        ins_type = self.instructionType()
        if ins_type == C_COMMAND:
            m = C_COMMAND_PATTERN.match(self.current_command)
            return m.group(3)
        else:
            raise Exception("Current command is not C_COMMAND")
