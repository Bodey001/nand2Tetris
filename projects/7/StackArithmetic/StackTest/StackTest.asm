// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_155
D;JEQ
@SP
A=M-1
M=0
@END_StackTest.asm_155
0;JMP
(TRUE_StackTest.asm_155)
@SP
A=M-1
M=-1
(END_StackTest.asm_155)
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_459
D;JEQ
@SP
A=M-1
M=0
@END_StackTest.asm_459
0;JMP
(TRUE_StackTest.asm_459)
@SP
A=M-1
M=-1
(END_StackTest.asm_459)
// push constant 16
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 17
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
// eq
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_763
D;JEQ
@SP
A=M-1
M=0
@END_StackTest.asm_763
0;JMP
(TRUE_StackTest.asm_763)
@SP
A=M-1
M=-1
(END_StackTest.asm_763)
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_1071
D;JLT
@SP
A=M-1
M=0
@END_StackTest.asm_1071
0;JMP
(TRUE_StackTest.asm_1071)
@SP
A=M-1
M=-1
(END_StackTest.asm_1071)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 892
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_1383
D;JLT
@SP
A=M-1
M=0
@END_StackTest.asm_1383
0;JMP
(TRUE_StackTest.asm_1383)
@SP
A=M-1
M=-1
(END_StackTest.asm_1383)
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 891
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
// lt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_1695
D;JLT
@SP
A=M-1
M=0
@END_StackTest.asm_1695
0;JMP
(TRUE_StackTest.asm_1695)
@SP
A=M-1
M=-1
(END_StackTest.asm_1695)
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_2015
D;JGT
@SP
A=M-1
M=0
@END_StackTest.asm_2015
0;JMP
(TRUE_StackTest.asm_2015)
@SP
A=M-1
M=-1
(END_StackTest.asm_2015)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32767
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_2335
D;JGT
@SP
A=M-1
M=0
@END_StackTest.asm_2335
0;JMP
(TRUE_StackTest.asm_2335)
@SP
A=M-1
M=-1
(END_StackTest.asm_2335)
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 32766
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
// gt
@SP
AM=M-1
D=M
A=A-1
D=M-D
@TRUE_StackTest.asm_2655
D;JGT
@SP
A=M-1
M=0
@END_StackTest.asm_2655
0;JMP
(TRUE_StackTest.asm_2655)
@SP
A=M-1
M=-1
(END_StackTest.asm_2655)
// push constant 57
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 31
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 53
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
// push constant 112
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// neg
@SP
A=M-1
M=-M
// and
@SP
AM=M-1
D=M
A=A-1
M=M&D
// push constant 82
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
// or
@SP
AM=M-1
D=M
A=A-1
M=M|D
// not
@SP
A=M-1
M=!M
