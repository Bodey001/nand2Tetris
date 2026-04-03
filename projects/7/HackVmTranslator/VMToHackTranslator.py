import argparse
import os
from Parser import HackParser
from CodeWriter import CodeWriter


def main():
    # SETUP ARGUMENTS
    arg_parser = argparse.ArgumentParser(
        description="Hack VM Translator"
    )  # Creates an argument parser object to handle user input
    arg_parser.add_argument(
        "source", help="The source .vm file"
    )  # Tells the program to expects one mandatory argument: the source file
    args = (
        arg_parser.parse_args()
    )  # Processes the input and stores the filename in args.source

    source_file = args.source
    if not os.path.exists(source_file):
        print(f"Error: File '{source_file}' not found.")
        return

    # Create output filename (Prog.asm -> Prog.hack)
    output_file = source_file.replace(".vm", ".asm")

    # ==========================================
    # PARSING THE PROGRAM
    # ==========================================
    print("Parsing the source file")
    parser = HackParser(source_file)

    print("Writing to the output file")
    writer = CodeWriter(output_file)

    while parser.hasMoreLines():
        parser.advance()
        command_type = parser.commandType()

        if command_type == "C_ARITHMETIC":
            command = parser.arg1()
            writer.WriteArithmetic(command)
        elif command_type in ["C_PUSH", "C_POP"]:
            segment = parser.arg1()
            index = parser.arg2()
            writer.WritePushPop(command_type, segment, index)

    writer.close()

    print(f"Success! Output written to {output_file}")


if __name__ == "__main__":
    main()
