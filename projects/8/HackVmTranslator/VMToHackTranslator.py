import argparse
import os
import sys
from Parser import HackParser
from CodeWriter import CodeWriter


def main():
    # check if the translator's input is a folder or  a file
    # if the translator's input is a folder, we need to create multiple Parser for each file
    # and a single CodeWriter to write to a single output file
    # the output file will be the name of the folder with the .asm extension
    # the output file will contain the code for all the source files
    # the output file will be written to the same directory as the source files
    # if the translator's input is a file, we need to create a single Parser and a single CodeWriter
    # the output file will be the name of the file with the .asm extension

    if len(sys.argv) != 2:
        print("Usage: python VMToHackTranslator.py [file.vm or directory]")
        return

    input_path = sys.argv[1]
    vm_files = []


    # Check is the input is a folder or a file
    if os.path.isfile(input_path) and input_path.endswith(".vm"):
        # add the absolute path of the file to the list of vm files
        vm_files.append(os.path.abspath(input_path))
        # create the output file name by replacing the .vm extension with .asm
        output_file = os.path.abspath(input_path).replace(".vm", ".asm")

    elif os.path.isdir(input_path):
        # add the absolute path of the files in the folder to the list of vm files
        for file in os.listdir(input_path):
            if file.endswith(".vm"):
                vm_files.append(os.path.abspath(os.path.join(input_path, file)))
        # create the output file name by adding the folder name to the .asm extension
        folder_name = os.path.basename(input_path)
        output_file = os.path.join(input_path, folder_name + ".asm")
    else:
        resolved = os.path.abspath(input_path)
        print("Error: Invalid input. Pass a .vm file or a directory containing .vm files.")
        print(f"  Resolved path (not found or not valid): {resolved}")
        return

    # create a single output file writer for all the vm files
    writer = CodeWriter(output_file)

    # process each vm file
    for vm_file in vm_files:
        # extract the file name from the absolute path
        file_name = os.path.basename(vm_file).replace(".vm", "")
        # set the file name in the writer
        writer.setFileName(file_name)
        # print the file name and the file path
        print(f"Processing file: {file_name} at {vm_file}")
        # create a parser for the vm file
        parser = HackParser(vm_file)
        # process the vm file
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
            elif command_type == "C_LABEL":
                label = parser.arg1()
                writer.WriteLabel(label)
            elif command_type == "C_GOTO":
                label = parser.arg1()
                writer.WriteGoto(label)
            elif command_type == "C_IF":
                label = parser.arg1()
                writer.WriteIf(label)
            elif command_type == "C_FUNCTION":
                function_name = parser.arg1()
                n_vars = parser.arg2()
                writer.WriteFunction(function_name, n_vars)
            elif command_type == "C_RETURN":
                writer.WriteReturn()
            elif command_type == "C_CALL":
                function_name = parser.arg1()
                n_args = parser.arg2()
                writer.WriteCall(function_name, n_args)


    writer.close()

    print(f"Success! Output written to {output_file}")





    # # SETUP ARGUMENTS
    # arg_parser = argparse.ArgumentParser(
    #     description="Hack VM Translator"
    # )  # Creates an argument parser object to handle user input
    # arg_parser.add_argument(
    #     "source", help="The source .vm file"
    # )  # Tells the program to expects one mandatory argument: the source file
    # args = (
    #     arg_parser.parse_args()
    # )  # Processes the input and stores the filename in args.source

    # source_file = args.source
    # if not os.path.exists(source_file):
    #     print(f"Error: File '{source_file}' not found.")
    #     return

    # # Create output filename (Prog.asm -> Prog.hack)
    # output_file = source_file.replace(".vm", ".asm")

    # ==========================================
    # PARSING THE PROGRAM
    # ==========================================



if __name__ == "__main__":
    main()
