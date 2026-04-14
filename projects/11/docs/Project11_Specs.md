# Project 11: Jack Compiler API Specification & Implementation Guide

This document outlines the architectural specification, module API, and recommended development stages for the Nand2Tetris Project 11 Compiler.

---

## 1. `JackTokenizer.py`
**Status:** Complete.
Reuse the exact `JackTokenizer.py` from Project 10. Its responsibility remains solely to read the `.jack` input file, remove comments/whitespace, and feed a stream of parsed tokens to the compilation engine.

---

## 2. `SymbolTable.py`
**Purpose:** Acts as the compiler's memory. It tracks variable declarations across two scopes: Class-level scope (`STATIC`, `FIELD`) and Subroutine-level scope (`ARG`, `VAR`).

### API Specification
* **`__init__(self)`**
  * Creates a new empty symbol table.
* **`reset(self)`**
  * Empties the subroutine-level symbol table and resets the `ARG` and `VAR` indexes to 0.
  * *Must be called every time compilation of a new subroutine begins.*
* **`define(self, name: str, type: str, kind: str)`**
  * Defines (adds to the table) a new variable of the given `name`, `type`, and `kind` (`STATIC`, `FIELD`, `ARG`, or `VAR`).
  * Assigns it the next available index for that kind and increments the index.
* **`varCount(self, kind: str) -> int`**
  * Returns the number of variables of the given `kind` currently defined in the table.
* **`kindOf(self, name: str) -> str`**
  * Returns the kind of the named identifier (`STATIC`, `FIELD`, `ARG`, `VAR`).
  * If the identifier is not found, returns `NONE`.
* **`typeOf(self, name: str) -> str`**
  * Returns the type of the named variable (e.g., `int`, `boolean`, `Square`).
* **`indexOf(self, name: str) -> int`**
  * Returns the index assigned to the named variable.

---

## 3. `VMWriter.py`
**Purpose:** A helper module that encapsulates the syntax of the VM language, allowing the engine to emit VM commands using simple method calls rather than manual string formatting.

### API Specification
* **`__init__(self, output_file: str)`**
  * Creates a new file and prepares it for writing.
* **`writePush(self, segment: str, index: int)`**
  * Writes a VM `push` command.
  * Valid segments: `CONST`, `ARG`, `LOCAL`, `STATIC`, `THIS`, `THAT`, `POINTER`, `TEMP`.
* **`writePop(self, segment: str, index: int)`**
  * Writes a VM `pop` command.
* **`writeArithmetic(self, command: str)`**
  * Writes a VM arithmetic/logical command.
  * Valid commands: `ADD`, `SUB`, `NEG`, `EQ`, `GT`, `LT`, `AND`, `OR`, `NOT`.
* **`writeLabel(self, label: str)`**
  * Writes a VM `label` command.
* **`writeGoto(self, label: str)`**
  * Writes a VM unconditional `goto` command.
* **`writeIf(self, label: str)`**
  * Writes a VM conditional `if-goto` command.
* **`writeCall(self, name: str, nArgs: int)`**
  * Writes a VM `call` command.
* **`writeFunction(self, name: str, nLocals: int)`**
  * Writes a VM `function` command.
* **`writeReturn(self)`**
  * Writes a VM `return` command.
* **`close(self)`**
  * Closes the output file.

---

## 4. `CompilationEngine.py`
**Purpose:** Translates the parsed token stream into VM code. It uses the `SymbolTable` to look up variable properties and the `VMWriter` to emit the final instructions.

### API Specification
* **`__init__(self, input_file, output_file)`**
  * Initializes a `JackTokenizer`, a `SymbolTable`, and a `VMWriter`.
  * Begins compilation by calling `compileClass()`.
* **`compileClass(self)`**
  * Compiles a complete class structure.
* **`compileClassVarDec(self)`**
  * Compiles a `static` or `field` declaration. Updates the SymbolTable.
* **`compileSubroutine(self)`**
  * Compiles a complete `method`, `function`, or `constructor`.
  * *Note: Calls `SymbolTable.reset()` at the start.*
* **`compileParameterList(self)`**
  * Compiles a parameter list. Updates the SymbolTable.
* **`compileSubroutineBody(self)`**
  * Compiles a subroutine's body (variable declarations followed by statements).
* **`compileVarDec(self)`**
  * Compiles a `var` declaration. Updates the SymbolTable.
* **`compileStatements(self)`**
  * Compiles a sequence of statements. (Does not consume the enclosing `{}`).
* **`compileLet(self)`**
  * Compiles a `let` statement. Evaluates the expression, then emits a `pop` to the target variable.
* **`compileIf(self)`**
  * Compiles an `if` statement, including an optional `else` clause. Generates unique VM labels for flow control.
* **`compileWhile(self)`**
  * Compiles a `while` statement. Generates unique VM labels for looping.
* **`compileDo(self)`**
  * Compiles a `do` statement. Calls the specified subroutine and emits `pop temp 0` to discard the returned void value.
* **`compileReturn(self)`**
  * Compiles a `return` statement. Explicitly pushes `constant 0` if the function returns `void`.
* **`compileExpression(self)`**
  * Compiles an expression. Emits VM code to compute the value and leave it at the top of the stack.
* **`compileTerm(self)`**
  * Compiles a specific term. Resolves variables, array indices, or subroutine calls.
* **`compileExpressionList(self) -> int`**
  * Compiles a comma-separated list of expressions.
  * *Returns the number of expressions compiled* (used as `nArgs` for `call` commands).

---

## 5. `JackCompiler.py`
**Purpose:** The main driver program that sets up and invokes all other compiler modules.

### API Specification
* **`main()`**
  * Accepts a file name (`Xxx.jack`) or a directory containing `.jack` files.
  * For each source file, creates an output file named `Xxx.vm`.
  * Instantiates the `CompilationEngine` to parse the input file and emit the translated VM code into the output file.

---

## Implementation & Testing Stages

To successfully morph your Project 10 Syntax Analyzer into the final Project 11 Compiler, it is highly recommended to follow these development stages:

### Stage 0: Foundation
* **Backup Project 10:** Make a clean backup copy of your working Syntax Analyzer code developed in Project 10. You will modify this codebase heavily, so preserving the original is crucial.

### Stage 1: The Symbol Table (XML Verification)
Before generating any VM code, ensure your compiler accurately tracks variable state and scope.
* **Build the Module:** Implement the `SymbolTable` API.
* **Extend the XML Output:** Temporarily modify your `CompilationEngine`. Whenever an `identifier` is encountered, instead of simply outputting `<identifier> foo </identifier>`, query your Symbol Table and output the following augmented information (using markup tags of your choice):
  * `name` (e.g., "foo")
  * `category` (field, static, var, arg, class, subroutine)
  * `index` (the running index assigned by the table)
  * `usage` (whether the identifier is presently being *declared* or *used*)
* **Test the Table:** Run this extended syntax analyzer on the Project 10 test programs. If the augmented XML outputs the correct categories and indexes for every variable, your compiler successfully understands the semantics of Jack. You are now ready to switch to full-scale VM compilation.

### Stage 2: VM Generation & The Testing Loop
Gradually replace the passive XML output routines with active `VMWriter` instructions. Verify your progress using the following loop:
1. **Compile:** Run your compiler on a provided test program folder. This should generate one `.vm` file for every `.jack` file in the folder.
2. **Inspect:** Open and visually inspect the generated `.vm` files. Look for obvious errors like missing commands or poorly formatted syntax. Fix your compiler and return to Step 1. *(Note: All provided `.jack` test programs are guaranteed to be error-free).*
3. **Emulate:** Load the entire test program folder into the **VM Emulator**, and run the loaded code. Each of the six supplied test programs (Seven, ConvertToBin, Square, Average, Pong, ComplexArrays) contains specific execution guidelines.
4. **Debug:** If the program behaves unexpectedly or an error message is displayed by the VM Emulator, trace the problematic VM instruction back to your compiler logic, apply the fix, and go back to Step 1.
