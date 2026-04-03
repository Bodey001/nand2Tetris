import os

RegisterTable = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}

class CodeWriter():
    def __init__(self, output_file):
        self.output_file = output_file
        self.file = open(output_file, "w")

        self.file_name = os.path.basename(output_file)

    def WriteArithmetic(self, command):
        # Write the command to the output file
        # Handle binary arithmetic commands (add, sub, and, or)
        if command in ["add", "sub", "and", "or"]:
            self.file.write(f"// {command}\n")
            self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\n")
            if command == "add":
                self.file.write("M=M+D\n")
            elif command == "sub":
                self.file.write("M=M-D\n")
            elif command == "and":
                self.file.write("M=M&D\n")
            elif command == "or":
                self.file.write("M=M|D\n")

        # Handle unary arithmetic commands (neg, not)
        elif command in ["neg", "not"]:
            self.file.write(f"// {command}\n")
            self.file.write("@SP\nA=M-1\n")
            if command == "neg":
                self.file.write("M=-M\n")
            elif command == "not":
                self.file.write("M=!M\n")

        # Handle comparison commands (eq, gt, lt)
        elif command in ["eq", "gt", "lt"]:
            self.file.write(f"// {command}\n")
            self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n")

            # Labels
            unique_id = self.file.tell()
            true_label = f"TRUE_{self.file_name}_{unique_id}"
            end_label = f"END_{self.file_name}_{unique_id}"

            if command == "eq":
                self.file.write(f"@{true_label}\nD;JEQ\n")
            elif command == "gt":
                self.file.write(f"@{true_label}\nD;JGT\n")
            elif command == "lt":
                self.file.write(f"@{true_label}\nD;JLT\n")

            self.file.write("@SP\nA=M-1\nM=0\n")
            self.file.write(f"@{end_label}\n0;JMP\n")
            self.file.write(f"({true_label})\n")
            self.file.write("@SP\nA=M-1\nM=-1\n")
            self.file.write(f"({end_label})\n")

    def WritePushPop(self, command, segment, index):
        # Write the command to the output file
        if command == "C_PUSH":
            self.file.write(f"// push {segment} {index}\n")
            if segment == "constant":
                self.file.write(f"@{index}\nD=A\n")
            elif segment in ["local", "argument", "this", "that"]:
                base = RegisterTable[segment]
                self.file.write(f"@{base}\nD=M\n@{index}\nA=D+A\nD=M\n")
            elif segment == "temp":
                self.file.write(f"@{5 + int(index)}\nD=M\n")
            elif segment == "pointer":
                self.file.write(f"@{'THIS' if str(index) == '0' else 'THAT'}\nD=M\n")
            elif segment == "static":
                self.file.write(f"@{self.file_name}.{index}\nD=M\n")
            self.file.write("@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        elif command == "C_POP":
            self.file.write(f"// pop {segment} {index}\n")
            if segment in ["local", "argument", "this", "that"]:
                base = RegisterTable[segment]
                self.file.write(f"@{base}\nD=M\n@{index}\nD=D+A\n@R13\nM=D\n")
            elif segment == "temp":
                self.file.write(f"@{5 + int(index)}\nD=A\n@R13\nM=D\n")
            elif segment == "pointer":
                self.file.write(f"@{'THIS' if str(index) == '0' else 'THAT'}\nD=A\n@R13\nM=D\n")
            elif segment == "static":
                self.file.write(f"@{self.file_name}.{index}\nD=A\n@R13\nM=D\n")
            self.file.write("@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")

    def close(self):
        self.file.close()
