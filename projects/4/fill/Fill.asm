// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, the
// program clears the screen, i.e. writes "white" in every pixel.

// R0: Previous State (0=Released, 1=Pressed)
// R1: Current State  (0=Released, 1=Pressed)


    // define screen size
    @8192
    D=A
    @number_of_pixel
    M=D

    @R0
    M=0     // Screen starts empty
(LOOP)
    @KBD
    D=M
    @KEY_PUSHED
    D;JNE   // if KBD != 0 goto KEY_PUSHED

(KEY_NOT_PUSHED)
    @R1
    M=0
    @CHECK_STATE_CHANGE
    0;JMP

(KEY_PUSHED)
    @R1
    M=1

(CHECK_STATE_CHANGE)
    @R0
    D=M
    @R1
    D=D-M
    @LOOP
    D;JEQ   // If R0 == R1 (no change), goto LOOP

    // State changed! Update R0 to match R1
    @R1
    D=M
    @R0
    M=D

    // Reset loop index 'i' to 0
    @i
    M=0

    // Decide which loop to run
    @R1
    D=M
    @EMPTY_SCREEN_LOOP
    D;JEQ   // If R1 is 0, go to Empty loop

(FILL_SCREEN_LOOP)
    @i
    D=M
    @number_of_pixel
    D=D-M
    @LOOP
    D;JEQ   // If i == 8192, exit to main LOOP

    // Calculate Address: SCREEN + i
    @SCREEN
    D=A
    @i
    A=D+M   // Valid syntax: A = SCREEN + i
    M=-1    // Draw Black

    @i
    M=M+1
    @FILL_SCREEN_LOOP
    0;JMP

(EMPTY_SCREEN_LOOP)
    @i
    D=M
    @number_of_pixel
    D=D-M
    @LOOP
    D;JEQ   // If i == 8192, exit to main LOOP

    // Calculate Address: SCREEN + i
    @SCREEN
    D=A
    @i
    A=D+M   // Valid syntax: A = SCREEN + i
    M=0     // Draw White

    @i
    M=M+1
    @EMPTY_SCREEN_LOOP
    0;JMP
