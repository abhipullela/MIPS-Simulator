import os

# total registers in MIPS ($0 to $31)
REG_COUNT = 32  

# keeping memory small for this project (4 KB)
MEM_SIZE = 4096  

# starting address of data segment (standard MIPS convention)
DATA_BASE = 0x10010000


# file where execution trace (PC etc.) will be stored
DEBUG_FILE = "execution_trace.txt"

# file to store main memory contents
MEMORY_FILE = "main_memory.txt"


# Program Counter → points to next instruction
PC = 0  

# 32 general purpose registers, all initialized to 0
REG = [0] * REG_COUNT  

# instruction memory (each instruction = 4 bytes)
# so we divide total memory size by 4
INST_MEM = [0] * (MEM_SIZE // 4)

# register name → register number mapping for assembler parsing
reg_names = {
    "$zero": 0,
    "$at": 1,
    "$v0": 2, "$v1": 3,
    "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7,
    "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11,
    "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19,
    "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
    "$t8": 24, "$t9": 25,
    "$k0": 26, "$k1": 27,
    "$gp": 28, "$sp": 29,
    "$fp": 30, "$ra": 31
}

def read_word(addr):

    addr -= DATA_BASE  # convert actual address to memory index

    if addr < 0 or addr + 3 >= MEM_SIZE:
        raise Exception("Memory access out of bounds")  # prevent invalid access

    with open(MEMORY_FILE, "r") as f:
        lines = f.readlines()  # read entire memory file

    word_index = addr // 4  # find which word to read
    word_hex = lines[word_index].split(":")[1].strip()  # extract hex value

    return int(word_hex, 16)  # convert hex string to integer


def write_word(addr, val):

    addr -= DATA_BASE  # convert actual address to memory index

    if addr < 0 or addr + 3 >= MEM_SIZE:
        raise Exception("Memory access out of bounds")  # prevent invalid access

    val &= 0xFFFFFFFF  # keep value within 32 bits

    with open(MEMORY_FILE, "r") as f:
        lines = f.readlines()  # read current memory contents

    word_index = addr // 4  # find which word to update
    lines[word_index] = f"{addr:04d}: 0x{val:08X}\n"  # update that line

    with open(MEMORY_FILE, "w") as f:
        f.writelines(lines)  # write back updated memory


# append debug message to trace file
def log_debug(message):
    with open(DEBUG_FILE, "a") as f:
        f.write(message + "\n")

# initialize memory file with zeros
def initialize_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            for i in range(0, MEM_SIZE, 4):
                f.write(f"{i:04d}: 0x00000000\n")
                

# STEP 1 : IF

def fetch():
    global PC

    instr_word_address = PC // 4  # convert PC (byte addr) to instruction index

    if not (0 <= instr_word_address < len(INST_MEM)):
        raise Exception(
            f"Instruction memory access out of bounds: PC={PC} "
            f"(word address {instr_word_address})"
        )  # invalid jump/branch target

    instr = INST_MEM[instr_word_address]  # fetch instruction

    npc = PC + 4  # next sequential PC
    PC = npc  # update PC (can be changed later by branch/jump)

    log_debug(f"IF  : PC = {PC} Instruction = {hex(instr)}")

    return instr, npc


# STEP 2 : ID

def decode(instr, npc):

    opcode = (instr >> 26) & 0x3F
    rs = (instr >> 21) & 0x1F
    rt = (instr >> 16) & 0x1F
    rd = (instr >> 11) & 0x1F
    funct = instr & 0x3F
    shamt = (instr >> 6) & 0x1F  # shift amount (for shift instructions)

    imm = instr & 0xFFFF  # extract 16-bit immediate
    if imm & 0x8000:
        imm -= 0x10000  # sign extend if negative

    log_debug(f"ID  : opcode={opcode} rs={rs} rt={rt} rd={rd} imm={imm}")

    # pass everything forward to EX stage
    return {
        "opcode": opcode,
        "rs": rs,
        "rt": rt,
        "rd": rd,
        "funct": funct,
        "imm": imm,
        "shamt": shamt,
        "npc": npc
    }


# STEP 3 : EX

def execute(info):
    global PC

    opcode = info["opcode"]

    # generate control signals + ALU result
    result = {
        "memRead": False,
        "memWrite": False,
        "regWrite": False,
        "memToReg": False,
        "aluOut": 0,
        "writeReg": 0,
        "ALUSrc": False,
        "RegDst": False,
        "Branch": False,
        "Jump": False,
        "rtVal": REG[info["rt"]]  # store rt value (used by sw)
    }

    # -------- R-TYPE instructions --------
    if opcode == 0:
        result["regWrite"] = True
        result["writeReg"] = info["rd"]

        rsVal = REG[info["rs"]]
        rtVal = REG[info["rt"]]

        if info["funct"] == 12:  # syscall handler
            service = REG[2]  # syscall number in $v0

            if service == 1:  # print int
                print(REG[4], end="")
                result["regWrite"] = False

            elif service == 4:  # print string
                addr = REG[4]
                s = ""
                while True:
                    offset = addr - DATA_BASE
                    if offset < 0 or offset >= MEM_SIZE:
                        break
                    with open(MEMORY_FILE, "r") as f:
                        lines = f.readlines()
                    word_index = offset // 4
                    word = int(lines[word_index].split(":")[1].strip(), 16)
                    byte = (word >> (8 * (3 - (offset % 4)))) & 0xFF
                    if byte == 0:
                        break
                    s += chr(byte)
                    addr += 1
                print(s, end="")
                result["regWrite"] = False

            elif service == 5:  # read int
                REG[2] = int(input())
                result["regWrite"] = False

            elif service == 11:  # print char
                print(chr(REG[4] & 0xFF), end="")
                result["regWrite"] = False

            elif service == 10:  # exit program
                print("\nProgram exited normally.")
                exit(0)

            else:  # unsupported syscall
                print(f"Unsupported syscall: {service}")
                result["regWrite"] = False

            return result  # syscall handled separately

        if info["funct"] == 32:      # add
            result["aluOut"] = rsVal + rtVal
        elif info["funct"] == 34:    # sub
            result["aluOut"] = rsVal - rtVal
        elif info["funct"] == 36:    # and
            result["aluOut"] = rsVal & rtVal
        elif info["funct"] == 37:    # or
            result["aluOut"] = rsVal | rtVal
        elif info["funct"] == 42:    # slt
            result["aluOut"] = int(rsVal < rtVal)
        elif info["funct"] == 33:    # addu
            result["aluOut"] = rsVal + rtVal
        elif info["funct"] == 8:     # jr (jump register)
            PC = REG[info["rs"]]
            result["regWrite"] = False
        elif info["funct"] == 0:     # sll (shift left logical)
            result["aluOut"] = REG[info["rt"]] << info["shamt"]
        elif info["funct"] == 3:     # sra (shift right arithmetic)
            result["aluOut"] = REG[info["rt"]] >> info["shamt"]
        else:
            raise Exception("Unknown funct : ", info["funct"])

    # -------- ADDI / ADDIU --------
    elif opcode == 8 or opcode == 9:
        result["regWrite"] = True
        result["writeReg"] = info["rt"]
        result["aluOut"] = REG[info["rs"]] + info["imm"]

    # -------- MUL --------
    elif opcode == 28:
        result["aluOut"] = REG[info["rs"]] * REG[info["rt"]]
        result["regWrite"] = True
        result["writeReg"] = info["rd"]

    # -------- LW --------
    elif opcode == 35:
        result["aluOut"] = REG[info["rs"]] + info["imm"]  # compute memory address
        result["memRead"] = True
        result["regWrite"] = True
        result["memToReg"] = True
        result["writeReg"] = info["rt"]

    # -------- SW --------
    elif opcode == 43:
        result["aluOut"] = REG[info["rs"]] + info["imm"]  # compute memory address
        result["memWrite"] = True

    # -------- BEQ --------
    elif opcode == 4:
        if REG[info["rs"]] == REG[info["rt"]]:
            PC = info["npc"] + (info["imm"] << 2)  # branch if equal

    # -------- BNE --------
    elif opcode == 5:
        if REG[info["rs"]] != REG[info["rt"]]:
            PC = info["npc"] + (info["imm"] << 2)  # branch if not equal

    # -------- BGEZ --------
    elif opcode == 1:
        if info["rt"] == 1 and REG[info["rs"]] >= 0:
            PC = info["npc"] + (info["imm"] << 2)

    # -------- BGTZ --------
    elif opcode == 7:
        if REG[info["rs"]] > 0:
            PC = info["npc"] + (info["imm"] << 2)

    # -------- J --------
    elif opcode == 2:
        PC = (PC & 0xF0000000) | (info["imm"] << 2)  # absolute jump

    # -------- JAL --------
    elif opcode == 3:
        result["regWrite"] = True
        result["writeReg"] = 31  # store return address in $ra
        result["aluOut"] = info["npc"]
        PC = (PC & 0xF0000000) | (info["imm"] << 2)

    # -------- LUI --------
    elif opcode == 15:
        result["regWrite"] = True
        result["writeReg"] = info["rt"]
        result["aluOut"] = info["imm"] << 16  # load upper 16 bits

    # -------- ORI --------
    elif opcode == 13:
        result["regWrite"] = True
        result["writeReg"] = info["rt"]
        result["aluOut"] = REG[info["rs"]] | (info["imm"] & 0xFFFF)

    else:
        raise Exception("Unknown opcode : ", opcode)

    result["aluOut"] &= 0xFFFFFFFF  # keep ALU result 32-bit

    log_debug(f"EX  : ALUOut={result['aluOut']} memRead={result['memRead']} memWrite={result['memWrite']}")

    return result


# STEP 4 : MEM

def memory_access(result):

    if result["memRead"]:
        result["memOut"] = read_word(result["aluOut"])  # read word from data memory

    if result["memWrite"]:
        write_word(result["aluOut"], result["rtVal"])  # write word to data memory

    log_debug(f"MEM : Read from address {result['aluOut']}")   # log memory read
    log_debug(f"MEM : Write to address {result['aluOut']}")  # log memory write

    return result


# STEP 5 : WB

def write_back(result):

    if result["regWrite"] and result["writeReg"] != 0:  # write only if enabled and not $zero

        if result["memToReg"]:
            value = result["memOut"]  # load value from memory
        else:
            value = result["aluOut"]  # otherwise use ALU result

        value &= 0xFFFFFFFF  # keep value 32-bit
        if value & 0x80000000:
            value -= 0x100000000  # convert to signed

        REG[result["writeReg"]] = value  # update destination register

        log_debug(f"WB  : Register {result['writeReg']} = {REG[result['writeReg']]}")  # log write

    REG[0] = 0  # always keep $zero = 0


def run(max_instr=100000):
    count = 0  # instruction counter

    while count < max_instr:

        instr, npc = fetch()  # IF stage

        if instr == 0:  # stop on empty instruction
            print("Program finished.")
            break

        info = decode(instr, npc)  # ID stage

        result = execute(info)  # EX stage

        result = memory_access(result)  # MEM stage

        write_back(result)  # WB stage

        with open("register_dump.txt", "w") as dump_file:  # dump registers each cycle
            dump_file.write(f"Cycle {count + 1}\n")
            dump_file.write("-----------------------------------------------------\n")

            for reg_name, reg_idx in reg_names.items():
                dump_file.write(
                    f"{reg_name} = "
                    f"{'0x' + hex(REG[reg_idx])[2:].zfill(8)} "
                    f"({REG[reg_idx]})\n"
                )

            dump_file.write(f"\nANSWER = {REG[reg_names['$a0']]}\n")  # final answer in $a0
            dump_file.write("=====================================================\n\n")

        log_debug(f"PC = {PC}")  # log updated PC

        count += 1  # move to next cycle


def load_hex_file(filename):
    with open(filename, "r") as f:
        i = 0  # instruction memory index
        for line in f:
            line = line.strip()

            if not line:
                continue  # skip empty lines

            line = line.replace("0x", "")  # remove hex prefix if present
            INST_MEM[i] = int(line, 16)  # convert hex string to integer
            i += 1

    print(f"Loaded {i} instructions into memory.")  # show number of instructions loaded


if __name__ == "__main__":

    initialize_memory()

    # load_hex_file("merge_sort.hex") # merge sort
    # load_hex_file("second_largest.hex") # second largest number
    load_hex_file("factorial.hex") # second largest number


    STACK_TOP = DATA_BASE + MEM_SIZE
    REG[29] = STACK_TOP

    with open(DEBUG_FILE, "w") as f:
        f.write("----- Execution Trace -----\n\n")

    run()