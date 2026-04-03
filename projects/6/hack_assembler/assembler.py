import argparse
import os.path
from parser import HackParser, A_COMMAND, C_COMMAND, L_COMMAND
from symbol_table import SymbolTable
import code_module

def main():
    # SETUP ARGUMENTS
    arg_parser = argparse.ArgumentParser(description="Hack Assembler")  # Creates an argument parser object to handle user input
    arg_parser.add_argument("source", help="The source .asm file")  # Tells the program to expects one mandatory argument: the source file
    args = arg_parser.parse_args()    # Processes the input and stores the filename in args.source

    source_file = args.source
    if not os.path.exists(source_file):
        print(f"Error: File '{source_file}' not found.")
        return

    # Create output filename (Prog.asm -> Prog.hack)
    output_file = source_file.replace(".asm", "comp.hack")

    # Initialize Symbol Table (adds R0-R15, SCREEN, KBD, etc.)
    table = SymbolTable()

    # ==========================================
    # FIRST PASS: Symbol Table Generation
    # ==========================================
    print("Starting Pass 1: Mapping labels...")
    parser = HackParser(source_file)
    rom_address = 0

    while parser.hasMoreLines():
        parser.advance()
        cmd_type = parser.instructionType()

        if cmd_type == L_COMMAND:
            # Found a label like (LOOP). Map it to the NEXT ROM address.
            symbol = parser.symbol()
            if not table.contains(symbol):
                table.add_entry(symbol, rom_address)
        else:
            # If it's an A or C instruction, it consumes 1 line of ROM.
            rom_address += 1

    # ==========================================
    # SECOND PASS: Code Generation
    # ==========================================
    print("Starting Pass 2: Generating binary code...")
    parser = HackParser(source_file)  # Reload to start from top

    with open(output_file, "w") as f:
        while parser.hasMoreLines():
            parser.advance()
            cmd_type = parser.instructionType()

            # --- Handle A-Instructions (@value or @symbol) ---
            if cmd_type == A_COMMAND:
                symbol = parser.symbol()

                # Case 1: Is it a literal number? (@100)
                if symbol.isdigit():
                    value = int(symbol)

                # Case 2: Is it a symbol? (@sum or @LOOP)
                else:
                    if not table.contains(symbol):
                        # If new variable, assign it the next available RAM address (starts at 16)
                        table.add_variable(symbol)
                    value = table.get_address(symbol)

                # Convert to 16-bit binary (0 + 15 bits of value)
                binary_code = "0" + format(value, "015b")
                f.write(binary_code + "\n")

            # --- Handle C-Instructions (dest=comp;jump) ---
            elif cmd_type == C_COMMAND:
                # Get mnemonics from Parser
                comp_mnemonic = parser.comp()
                dest_mnemonic = parser.dest()
                jump_mnemonic = parser.jump()

                # Get binary bits from CodeWriter
                # Note: We assume code_module handles 'None' or empty strings if necessary
                comp_bits = code_module.comp(comp_mnemonic)
                dest_bits = code_module.dest(dest_mnemonic)
                jump_bits = code_module.jump(jump_mnemonic)

                # Assemble: 111 + comp + dest + jump
                binary_code = "111" + comp_bits + dest_bits + jump_bits
                f.write(binary_code + "\n")

            # --- Handle Labels ---
            elif cmd_type == L_COMMAND:
                # Ignored in Pass 2 (they don't generate machine code)
                pass

    print(f"Success! Output written to {output_file}")


if __name__ == "__main__":
    main()
