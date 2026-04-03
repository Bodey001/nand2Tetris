# nand2Tetris

Building a modern computer system from first principles, following the [nand2tetris](https://www.nand2tetris.org/) course (The Elements of Computing Systems).

Each project builds on the last, starting from a single NAND gate and culminating in a fully working computer with an operating system and high-level language.

---

## Projects

### Project 0 – Introduction & Setup
Getting familiar with the nand2tetris toolchain and the HDL (Hardware Description Language) used throughout the course.

---

### Project 1 – Boolean Logic
Implemented all fundamental logic gates in HDL, built up from a primitive NAND gate.

| Chip | Description |
|---|---|
| `Not`, `Not16` | Inverter (1-bit and 16-bit) |
| `And`, `And16` | AND gate (1-bit and 16-bit) |
| `Or`, `Or16`, `Or8Way` | OR gate (1-bit, 16-bit, 8-way) |
| `Xor` | Exclusive-OR gate |
| `Mux`, `Mux16`, `Mux4Way16`, `Mux8Way16` | Multiplexer variants |
| `DMux`, `DMux4Way`, `DMux8Way` | Demultiplexer variants |

---

### Project 2 – Boolean Arithmetic
Implemented the arithmetic chips that make up the ALU.

| Chip | Description |
|---|---|
| `HalfAdder` | Adds two bits |
| `FullAdder` | Adds three bits (with carry) |
| `Add16` | 16-bit adder |
| `Inc16` | 16-bit incrementer |
| `ALU` | Full Arithmetic Logic Unit — performs addition, subtraction, bitwise ops, negation, and comparisons based on control bits |

---

### Project 3 – Memory
Built sequential (clocked) memory chips using DFF primitives.

**Part A**
| Chip | Description |
|---|---|
| `Bit` | 1-bit register |
| `Register` | 16-bit register |
| `RAM8` | 8-register RAM |
| `RAM64` | 64-register RAM |
| `PC` | 16-bit Program Counter with load/increment/reset |

**Part B**
| Chip | Description |
|---|---|
| `RAM512` | 512-register RAM |
| `RAM4K` | 4K-register RAM |
| `RAM16K` | 16K-register RAM |

---

### Project 4 – Machine Language
Wrote Hack assembly programs directly in the Hack ISA.

| Program | Description |
|---|---|
| `Mult.asm` | Multiplies R0 and R1 using repeated addition, stores result in R2 |
| `Fill.asm` | Reads the keyboard; fills the screen black when a key is held, clears it when released |

---

### Project 5 – Computer Architecture
Assembled the full Hack computer from the chips built in projects 1–3.

| Chip | Description |
|---|---|
| `Memory` | Unified address space: RAM (16K), Screen (8K), Keyboard |
| `CPU` | Executes A- and C-instructions; manages PC, ALU, and registers |
| `Computer` | Top-level chip wiring CPU, Memory, and ROM together |

---

### Project 6 – Assembler
A two-pass Hack assembler written in **Python** (`projects/6/hack_assembler/`).

- **Parser** (`parser.py`) — strips comments/whitespace, identifies instruction type (A, C, L)
- **Code module** (`code_module.py`) — translates symbolic mnemonics to binary
- **Symbol table** (`symbol_table.py`) — resolves predefined symbols and user-defined labels/variables
- **Main** (`assembler.py`) — orchestrates the two passes and writes the `.hack` output

Tested against: `Add`, `Max`, `Rect`, `Pong`.

---

### Project 7 – VM Translator, Part I
A VM-to-Hack translator written in **Python** (`projects/7/HackVmTranslator/`).

Translates the first subset of the VM language to Hack assembly:

- **Stack arithmetic** — `add`, `sub`, `neg`, `eq`, `gt`, `lt`, `and`, `or`, `not`
- **Memory access** — `push`/`pop` for segments `constant`, `local`, `argument`, `this`, `that`, `temp`, `pointer`, `static`

Tested against: `StackTest`, `SimpleAdd` (StackArithmetic), `BasicTest`, `PointerTest`, `StaticTest` (MemoryAccess).

---

### Project 8 – VM Translator, Part II
Extended the VM translator (`projects/8/HackVmTranslator/`) to handle the full VM language, adding:

**Program Flow commands**
| VM Command | CodeWriter method |
|---|---|
| `label` | `WriteLabel` — emits an assembly label |
| `goto` | `WriteGoto` — unconditional jump |
| `if-goto` | `WriteIf` — pops top of stack; jumps if non-zero |

**Function Calling commands**
| VM Command | CodeWriter method |
|---|---|
| `function` | `WriteFunction` — emits function entry label and zeroes local variables |
| `call` | `WriteCall` — pushes return address + caller's LCL/ARG/THIS/THAT, repositions ARG and LCL, jumps to callee, plants return label |
| `return` | `WriteReturn` — restores caller frame (THAT→THIS→ARG→LCL), moves return value to ARG[0], resets SP, jumps to saved return address |

**Bootstrap**
The `CodeWriter` constructor emits a bootstrap preamble at the top of every multi-file output:
- Sets `SP = 256`
- Calls `Sys.init 0` using the full `WriteCall` sequence so the initial frame is properly pushed onto the stack

The translator accepts either a single `.vm` file or a directory (translating all `.vm` files to a single `.asm` output named after the directory).

Tested against:
- **ProgramFlow**: `BasicLoop`, `FibonacciSeries`
- **FunctionCalls**: `SimpleFunction`, `FibonacciElement`, `NestedCall`, `StaticsTest`
