## IAS Machine Simulator & Assembler

***Authors***
- Abhinav Pullela (IC2025021)
- Y B Siddharth (BC2025116)

## Project Overview
This project implements a simplified **MIPS 5-stage pipeline processor simulator** in Python.

It simulates the following pipeline stages:

IF → ID → EX → MEM → WB

The simulator loads machine code from a `.hex` file, executes it instruction-by-instruction, maintains register and memory state, and generates cycle-by-cycle register dumps and execution trace.

-----------

## Concepts and Technologies Used

### Core Concepts

- **MIPS Architecture**
  - 32 registers, R/I/J instruction formats
  - `$zero` register enforcement

- **5-Stage Pipeline**
  - IF → ID → EX → MEM → WB

- **Instruction Decoding**
  - Opcode, rs, rt, rd, funct extraction
  - Immediate sign-extension

- **ALU Operations**
  - Arithmetic (add, sub, mul)
  - Logical (and, or)
  - Comparison (slt)

- **Memory System**
  - Byte-addressable data memory
  - Word-aligned access
  - File-based persistent memory

- **Control Logic**
  - Branch and jump handling
  - Control signals (memRead, memWrite, regWrite)

- **Syscall Emulation**
  - Basic console I/O
  - Program termination

-----------

### Technologies Used

- **Python 3**
- Bitwise operations
- File I/O
- Bytearray for memory simulation
- Modular function-based design


-----------

## Module Explanation

### 1. MIPS Architecture Features Implemented

#### 1.1 Register File
- 32 General Purpose Registers ($0 – $31)
- $zero register permanently enforced as 0
- Register name mapping for assembly parsing

#### 1.2 Instruction Formats
- R-type
- I-type
- J-type

Instruction decoding includes:
- Opcode extraction
- rs, rt, rd extraction
- funct field handling
- Immediate sign-extension (16 → 32 bit)

#### 1.3 ALU Operations Supported
- Arithmetic
 - - add, addu, sub, addi
 - - mul
- Logical
 - - and, or, ori
- Comparison
 - - slt
- Shift
 - - sll, sra

All ALU results are masked to 32 bits.

#### 1.4 Control Flow Instructions
- beq
- bne
- bgez
- bgtz
- j
- jal
- jr

Branch and jump instructions update the Program Counter (PC) appropriately.

#### 1.5 Memory System
- Word-aligned memory access
- Byte-addressable addressing logic
- Persistent memory stored in main_memory.txt
- Bounds checking for memory safety

Memory operations:
- lw
- sw

Memory is initialized using:
    initialize_memory()

#### 1.6 Syscall Emulation
The simulator supports basic syscall handling:

| -Syscall- |	 --Function--   |
| 1	        | Print Integer   |
| 4	        | Print String    |
| 5	        | Read Integer    |
| 11	      | Print Character |
| 10 	      | Exit Program    |

Syscall number is read from $v0

---

### 2. Pipeline Stage Modules

Each stage is implemented as an independent function.

#### IF – Instruction Fetch
- Fetches instruction using `PC`
- Updates `PC = PC + 4`
- Performs bounds checking

#### ID – Instruction Decode
- Extracts opcode, rs, rt, rd, funct
- Performs sign extension of immediate
- Passes decoded fields forward

#### EX – Execute
- Performs ALU operations
- Handles control flow logic
- Generates control signals :
   - memRead
   - memWrite
   - regWrite
   - memToReg
- Implements syscall functionality

#### MEM – Memory Access
- Executes `lw` and `sw`
- Interacts with persistent memory file

#### WB – Write Back
- Writes ALU or memory result into registers
- Enforces `$zero = 0`
- Handles signed conversion

---

### 3. Execution Controller

#### `run(max_instr=100000)`
- Controls full instruction cycle
- Executes stages in order:
    IF → ID → EX → MEM → WB
- Stops when instruction 0x00000000 is encountered
- Generates register dump every cycle
- Logs PC updates

---

### 4. Loader

#### `load_hex_file(filename)`
- Reads `.hex` file
- Converts hex instructions to integers
- Loads into instruction memory

---

### 5. Debug & Output Files

The simulator automatically generates:
| ------- FILE ------- | ------------ PURPOSE ---------------- |
| execution_trace.txt  | Logs pipeline activity and PC updates |
| register_dump.txt    | Register values after each cycle      |
| main_memory.txt      | Persistent data memory                |

These files are auto-created during execution and can be deleted before running

---

### 6. Global Architecture Components

The simulator defines:

- PC → Program Counter
- REG[32] → Register File
- INST_MEM → Instruction Memory
- DATA_BASE → Base address for data segment
- MEM_SIZE → Total memory size
- Register name mappings

This section initializes the simulated CPU state.

---

Each module corresponds to a logical hardware component of a MIPS processor, implemented in software.

-----------

## Setup Instructions

Make sure you are inside the project directory in the terminal, then run:

```bash
--- change the filename in the required position for choosing which program to run
python assignment2_py.py
(Use python3 if required by your system.)


*FILE-STRUCTURE

MIPS/
│ README.md
│ assignment2_py.py
│ Student_Report.pdf
│
│ factorial.asm
│ factorial.hex
│ merge_sort.asm
│ merge_sort.hex
│ second_largest.asm
│ second_largest.hex
│
│ execution_trace.txt        (auto-generated)
│ register_dump.txt          (auto-generated)
│ main_memory.txt            (auto-generated)