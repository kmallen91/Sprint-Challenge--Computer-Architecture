"""CPU functionality."""

import sys

# OP Codes
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101

SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.flag = {}

    def load(self, file_name):
        """Load a program into memory."""

        try:
            address = 0
            # open the file
            with open(file_name) as f:
                for line in f:
                    # strip out white space, and split at a inline comment
                    cleaned_line = line.strip().split("#")
                    # grab the number
                    value = cleaned_line[0].strip()

                    # check if value is blank or not, if it is skip onto the next line
                    if value != "":
                        # convert from binary to num
                        num = int(value, 2)
                        self.ram[address] = num
                        address += 1
                    else:
                        continue

        except FileNotFoundError:
            print("ERR: FILE NOT FOUND")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag['E'] = 1
            else:
                self.flag['E'] = 0

            if self.reg[reg_a] < self.reg[reg_b]:
                self.flag['L'] = 1
            else:
                self.flag['L'] = 0

            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag['G'] = 1
            else:
                self.flag['G'] = 0
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def run(self):
        """Run the CPU."""
        while True:
            op = self.ram_read(self.pc)
            if op == PRN:
                index = self.ram[self.pc + 1]
                print(self.reg[index])
                self.pc += 2

            elif op == LDI:
                index = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.reg[index] = value
                self.pc += 3

            elif op == HLT:
                return False

            elif op == MUL:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                # call ALU
                self.alu("MUL", reg_a, reg_b)
                self.pc += 3

            elif op == ADD:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.alu("ADD", reg_a, reg_b)
                self.pc += 3

            elif op == PUSH:
                # decrement SP
                self.reg[SP] -= 1
                # get current mem address SP points to
                stack_addr = self.reg[SP]
                # grab a reg number from the instruction
                reg_num = self.ram_read(self.pc + 1)
                # get the value out of the register
                val = self.reg[reg_num]
                # write the reg value to a postition in the stack
                self.ram_write(stack_addr, val)
                self.pc += 2

            elif op == POP:
                # get the value out of memory
                stack_val = self.ram_read(self.reg[SP])
                # get the register number from the instruction in memory
                reg_num = self.ram_read(self.pc + 1)
                # set the value of a register to the value held in the stack
                self.reg[reg_num] = stack_val
                # increment the SP
                self.reg[SP] += 1
                self.pc += 2

            elif op == CALL:
                # decrement the SP
                self.reg[SP] -= 1
                # get the current memory address that SP points to
                stack_addr = self.reg[SP]
                # get the return memory address
                return_addr = self.pc + 2
                # push the return address onto the stack
                self.ram_write(stack_addr, return_addr)
                # set PC to the value in the register
                reg_num = self.ram_read(self.pc + 1)
                self.pc = self.reg[reg_num]

            elif op == RET:
                # pop the return memory address off the stack
                # store the poped memory address in the PC
                self.pc = self.ram_read(self.reg[SP])
                self.reg[SP] += 1

            elif op == CMP:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.alu("CMP", reg_a, reg_b)
                self.pc += 3

            elif op == JMP:
                reg_a = self.ram_read(self.pc + 1)
                self.pc = self.reg[reg_a]

            elif op == JNE:
                reg_a = self.ram_read(self.pc + 1)
                if self.flag['E'] == 0:
                    self.pc = self.reg[reg_a]
                else:
                    self.pc += 2

            elif op == JEQ:
                reg_a = self.ram_read(self.pc + 1)
                if self.flag['E'] == 1:
                    self.pc = self.reg[reg_a]
                else:
                    self.pc += 2

            else:
                print("ERR: UNKNOWN COMMAND:\t", op)
