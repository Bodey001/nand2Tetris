CommandTable = {
    "add": "C_ARITHMETIC",
    "sub": "C_ARITHMETIC",
    "neg": "C_ARITHMETIC",
    "eq": "C_ARITHMETIC",
    "gt": "C_ARITHMETIC",
    "lt": "C_ARITHMETIC",
    "and": "C_ARITHMETIC",
    "or": "C_ARITHMETIC",
    "not": "C_ARITHMETIC",
    "push": "C_PUSH",
    "pop": "C_POP",
    "label": "C_LABEL",
    "goto": "C_GOTO",
    "if-goto": "C_IF",
    "function": "C_FUNCTION",
    "return": "C_RETURN",
    "call": "C_CALL",
}


class HackParser():
    def __init__(self, filepath: str):
        # Open th file
        with open(filepath, "r") as file:
            raw_lines = file.readlines()

        self.commands = []

        # Read the file
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

    def commandType(self):
        # Parse the command
        command = self.current_command.split(" ")[0]
        if command in CommandTable:
            return CommandTable[command]
        else:
            raise Exception("Unknown command type")

    def arg1(self):
        command_type = self.commandType()
        if command_type == "C_RETURN":
            raise Exception("C_RETURN does not have arg1")
        elif command_type == "C_ARITHMETIC":
            return self.current_command
        else:
            return self.current_command.split(" ")[1]

    def arg2(self):
        command_type = self.commandType()
        if command_type in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            return int(self.current_command.split(" ")[2])
        else:
            raise Exception("Current command does not have arg2")
