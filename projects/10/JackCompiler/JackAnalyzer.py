"""JackAnalyzer – driver for the Jack syntax analyzer (Project 10).

Usage:
    python JackAnalyzer.py <file.jack>        -- analyse one file
    python JackAnalyzer.py <directory>        -- analyse every .jack file in the directory

For each .jack file the analyzer produces two output files next to the source:
    <Name>T.xml   – flat token stream (tokenizer output, for Phase-1 testing)
    <Name>.xml    – full parse tree  (compilation engine output)
"""

import os
import sys
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def analyse_file(jack_path: str):
    """Tokenize and parse a single .jack file."""
    base = jack_path[:-5]          # strip ".jack"
    token_out = base + "-analysisT.xml"
    parse_out = base + "-analysis.xml"

    # --- Phase 1: tokenizer output ---
    tokenizer = JackTokenizer(jack_path, output_file=token_out)
    while tokenizer.hasMoreTokens():
        tokenizer.process()
    tokenizer.close()

    # --- Phase 2: compilation engine ---
    # Re-tokenize to get a fresh token list for the parser
    tokenizer2 = JackTokenizer.__new__(JackTokenizer)
    tokenizer2.tokens = tokenizer.tokens
    tokenizer2.current_index = 0
    tokenizer2.current_token = tokenizer.tokens[0] if tokenizer.tokens else None

    engine = CompilationEngine(tokenizer.tokens, parse_out)


def main():
    if len(sys.argv) != 2:
        print("Usage: python JackAnalyzer.py [file.jack or directory]")
        return

    input_path = sys.argv[1]

    if os.path.isfile(input_path) and input_path.endswith(".jack"):
        analyse_file(os.path.abspath(input_path))

    elif os.path.isdir(input_path):
        jack_files = [
            os.path.abspath(os.path.join(input_path, f))
            for f in os.listdir(input_path)
            if f.endswith(".jack")
        ]
        if not jack_files:
            print(f"No .jack files found in {input_path}")
            return
        for jack_file in jack_files:
            analyse_file(jack_file)

    else:
        resolved = os.path.abspath(input_path)
        print("Error: pass a .jack file or a directory containing .jack files.")
        print(f"  Resolved path: {resolved}")


if __name__ == "__main__":
    main()
