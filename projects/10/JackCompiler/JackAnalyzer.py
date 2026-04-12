# takes in a .jack file or a folder containing .jack files, analyses it and print to .xml files
# the .xml files will contain the analysis of the .jack file
# the .xml files will be named like the .jack file but with the .xml extension
# the .xml files will be written to the same directory as the .jack files

import os
import sys
from JackTokenizer import JackTokenizer


def main():
    # check if the analyzer's input is a folder or a file
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py [file.jack or directory]")
        return

    input_path = sys.argv[1]
    jack_files = []


    # Check if the input is a folder or a file
    if os.path.isfile(input_path) and input_path.endswith(".jack"):
        # add the absolute path of the file to the list of jack files
        jack_files.append(os.path.abspath(input_path))
        # create the output file name by replacing the .jack with -analysisT.xml
        output_file = os.path.abspath(input_path).replace(".jack", "-analysisT.xml")

    elif os.path.isdir(input_path):
        # add the absolute path of the files in the folder to the list of jack files
        for file in os.listdir(input_path):
            if file.endswith(".jack"):
                jack_files.append(os.path.abspath(os.path.join(input_path, file)))
        # create the output file name by adding the folder name to -analysisT.xml
        folder_name = os.path.basename(input_path)
        output_file = os.path.join(input_path, folder_name + "-analysisT.xml")
    else:
        resolved = os.path.abspath(input_path)
        print("Error: Invalid input. Pass a .jack file or a directory containing .jack files.")
        print(f"  Resolved path (not found or not valid): {resolved}")
        return

    # create a tokenizer for each jack file
    for jack_file in jack_files:
        tokenizer = JackTokenizer(jack_file)
        # tokenize the jack file
        while tokenizer.hasMoreTokens():
            tokenizer.advance()
            tokenizer.process()

if __name__ == "__main__":
    main()  # run the main function
