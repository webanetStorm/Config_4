import json
import struct

# Constants
COMMAND_SIZE = 5  # Each command is 5 bytes


# Assembler
def assemble(input_file: str, binary_output: str, log_file: str):
    with open(input_file, "r") as infile, open(binary_output, "wb") as binfile, open(log_file, "w") as logfile:
        commands = []
        for line in infile:
            parts = line.strip().split()
            if not parts:
                continue

            command, *operands = parts
            if command == "LOAD_CONST":
                a = int(operands[0]) << 0
                b = int(operands[1]) << 5
                instruction = a | b
            elif command == "LOAD_MEM":
                a = int(operands[0]) << 0
                instruction = a
            elif command == "STORE_MEM":
                a = int(operands[0]) << 0
                b = int(operands[1]) << 5
                instruction = a | b
            elif command == "MIN":
                a = int(operands[0]) << 0
                b = int(operands[1]) << 5
                c = int(operands[2]) << 19
                instruction = a | b | c
            else:
                raise ValueError(f"Unknown command: {command}")

            # Convert to bytes
            bin_instruction = struct.pack("<I", instruction)[:COMMAND_SIZE]
            binfile.write(bin_instruction)

            # Log
            commands.append({"command": command, "operands": operands, "instruction": bin_instruction.hex()})

        # Write log
        json.dump(commands, logfile, indent=4)


# Interpreter
def interpret(binary_file: str, result_file: str, memory_range: tuple):
    memory = [0] * 256
    stack = []

    with open(binary_file, "rb") as binfile, open(result_file, "w") as resfile:
        while True:
            chunk = binfile.read(COMMAND_SIZE)
            if not chunk:
                break

            # Decode instruction
            instruction = int.from_bytes(chunk, "little")
            opcode = instruction & 0x1F
            operand_b = (instruction >> 5) & 0xFFFFF
            operand_c = (instruction >> 19) & 0xFFFFF

            if opcode == 3:  # LOAD_CONST
                stack.append(operand_b)
            elif opcode == 13:  # LOAD_MEM
                stack.append(memory[stack.pop()])
            elif opcode == 19:  # STORE_MEM
                value = stack.pop()
                address = stack.pop()
                memory[address] = value
            elif opcode == 27:  # MIN
                value = stack.pop()
                address = operand_c + operand_b
                memory[address] = min(stack.pop(), value)
            else:
                raise ValueError(f"Unknown opcode: {opcode}")

        # Save results from memory range
        memory_result = memory[memory_range[0]:memory_range[1]]
        json.dump({"memory": memory_result}, resfile, indent=4)


# Test Program
def main():
    # Assemble the input program
    assemble(
        input_file="program.txt",
        binary_output="program.bin",
        log_file="program_log.json"
    )

    # Interpret the binary file
    interpret(
        binary_file="program.bin",
        result_file="result.json",
        memory_range=(0, 10)  # Adjust as needed
    )


if __name__ == "__main__":
    main()
