import getopt
import re
import sys
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

# Attempt to parse command-line arguments
try:
    opts, _ = getopt.getopt(sys.argv[1:], "h", ["help"])
except getopt.GetoptError as err:
    # Exit with error code 10 if command-line arguments are invalid
    exit(10)

# Process command-line options
for o, a in opts:
    if o in ("-h", "--help") and len(sys.argv) == 2:            # If help option is provided and is the only argument
        print(
            """        Skript typu filtr (parse.py v jazyce Python 3.10) načte ze standardního vstupu zdrojový kód v IPPcode24, zkontroluje lexikální a syntaktickou správnost kódu a vypíše na standardní
        výstup XML reprezentaci programu.

        Tento skript bude pracovat s těmito parametry:
        • --help/-h, pro zobrazení nápovědy.
        • python3.10 papse.py parametry, kde parametry závisí na dané úloze. 

        Chybové návratové kódy specifické pro analyzátor:
        • 21 - chybná nebo chybějící hlavička ve zdrojovém kódu zapsaném v IPPcode24;
        • 22 - neznámý nebo chybný operační kód ve zdrojovém kódu zapsaném v IPPcode24;
        • 23 - jiná lexikální nebo syntaktická chyba zdrojového kódu zapsaného v IPPcode24.
        """
        )
        sys.exit(0)
    else:
        # Exit with error code if options are invalid
        sys.exit(10)

def read_source_code():                                         # Reads source code from standard input, handling comments and checking for a specific header                                                     
    code_lines = []
    header_found = False

    try:
        while True:
            line = input().rstrip("\n")                         # Read a line from standard input
            line = re.sub(r"#.*", "", line).strip()             # Remove comments and trailing spaces

            if not header_found:
                if line.upper() == ".IPPCODE24":
                    header_found = True
                    continue
                elif line == "":                                # Skip empty lines before finding the header
                    continue
                else:
                    sys.exit(21)                                

            if not line:                                        # Skip empty lines after finding the header
                continue

            code_lines.append(line)

    except EOFError:
        pass

    return code_lines

def lexical_analysis(code_lines):                               # Lexical analysis of the source code                      
    instructions = []
    opcode_pattern = r"^[A-Za-z0-9_$&%*!?/-]+[0-9]*$"
    operand_pattern = r"^(GF|LF|TF)@[A-Za-z0-9_$&%*!?/-]+$|^(int@-?\+?\d+|bool@(true|false)|string@[^@\s]*|nil@nil)$|^[\w$&%*!?/-]+$"

    for line in code_lines:
        tokens = re.split(r"\s+", line)                          # Split the line into tokens
        opcode = tokens[0].upper()
        if not re.match(opcode_pattern, opcode):
            sys.exit(23)                                         # Exit with an error code for invalid opcodes             
        
        operands = tokens[1:]
        for operand in operands:
            if not re.match(operand_pattern, operand):
                sys.exit(23)                                     # Exit with an error code for invalid operands             
        instructions.append([opcode] + operands)
    
    return instructions


def validate_operands(opcode, operands):                         # Validate operands based on the opcode and expected operand types       
    var_pattern = re.compile(r"^(GF|LF|TF)@([a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*)$")
    symb_pattern = re.compile(r"^(GF|LF|TF)@([a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*)$|^(int@-?\d+|bool@(true|false)|string@[^@\s]*|nil@nil)$")
    label_pattern = re.compile(r"^([a-zA-Z_$&%*!?-][a-zA-Z0-9_$&%*!?-]*)$")
    type_pattern = re.compile(r"^(int|bool|string|nil)$")


    operand_types = {                                            # Mapping from operand types to their validation patterns                       
        "var": var_pattern,
        "symb": symb_pattern,
        "label": label_pattern,
        "type": type_pattern
    }

    expected_opcodes = {
        ".IPPCODE24": [],
        "CREATEFRAME":[],
        "PUSHFRAME":  [],
        "POPFRAME":   [],
        "RETURN":     [],
        "BREAK":      [],
        "DEFVAR":     ["var"],
        "POPS":       ["var"],
        "CALL":       ["label"],
        "LABEL":      ["label"],
        "JUMP":       ["label"],
        "PUSHS":      ["symb"],
        "WRITE":      ["symb"],
        "EXIT":       ["symb"],
        "DPRINT":     ["symb"],
        "MOVE":       ["var", "symb"],
        "STRLEN":     ["var", "symb"],
        "TYPE":       ["var", "symb"],
        "NOT":        ["var", "symb"],
        "INT2CHAR":   ["var", "symb"],
        "INT2FLOAT":  ['var', 'symb'],
        "FLOAT2INT":  ['var', 'symb'],
        "READ":       ["var", "type"],
        "ADD":        ["var", "symb", "symb"],
        "SUB":        ["var", "symb", "symb"],
        "MUL":        ["var", "symb", "symb"],
        "IDIV":       ["var", "symb", "symb"],
        "LT":         ["var", "symb", "symb"],
        "GT":         ["var", "symb", "symb"],
        "EQ":         ["var", "symb", "symb"],
        "AND":        ["var", "symb", "symb"],
        "OR":         ["var", "symb", "symb"],
        "STRI2INT":   ["var", "symb", "symb"],
        "CONCAT":     ["var", "symb", "symb"],
        "GETCHAR":    ["var", "symb", "symb"],
        "SETCHAR":    ["var", "symb", "symb"],
        "JUMPIFEQ":   ["label", "symb", "symb"],
        "JUMPIFNEQ":  ["label", "symb", "symb"],
    }
    
    if opcode not in expected_opcodes:
        sys.exit(22)                                            # Exit with an error code for unknown opcodes   
    expected = expected_opcodes[opcode]
    
    if len(operands) != len(expected):
        sys.exit(23)                                            # Exit with an error code for incorrect number of operands    
    
    for operand, expected_type in zip(operands, expected):
        if not operand_types[expected_type].match(operand):
            sys.exit(23)                                        # Exit with an error code for invalid operand types             
    
    for operand in operands:
        if not is_valid_string(operand):
            sys.exit(23)                                        # Exit with an error code for invalid string operands

def is_valid_string(operand):                                   # Check if a string operand is valid       
    if operand.startswith("string@"):                                           
        content = operand[7:]                                   
        return not re.search(r"\\(?!\\|\d{3})", content)        
    return True

def syntactic_analysis(instructions):                           # Perform syntactic analysis on the parsed instructions
    for instruction in instructions:
        opcode, *operands = instruction
        validate_operands(opcode, operands)

def determine_operand_type(operand, is_second_arg=False):
    if "@" in operand:
        operand_type, operand_value = operand.split("@", 1)
        if operand_type in ["GF", "LF", "TF"]:                  # Check if type is one of the frame variables (Global, Local, Temporary)
            return "var", operand  
        elif operand_type in ["int", "bool", "string", "nil"]:  # Check if type is one of the basic data types (int, bool, string, nil)
            return operand_type, operand_value                  
    elif is_second_arg and operand in ["int", "bool", "string", "nil"]:
        return "type", operand                                  # If the operand is the second argument and is one of the basic data types, it is a type
    else:
        return "label", operand                                 # Otherwise, the operand is a label     

def generate_xml(instructions):                                 # Generate an XML document from the parsed instructions
    program = Element('program')
    program.set('language', 'IPPcode24')
    
    for i, instruction in enumerate(instructions, 1):
        opcode, *operands = instruction
        xml_instruction = SubElement(program, 'instruction', order=str(i), opcode=opcode)
        for j, operand in enumerate(operands, 1):
            is_second_arg = j > 1
            operand_type, operand_value = determine_operand_type(operand, is_second_arg)
            
            arg = SubElement(xml_instruction, f'arg{j}', type=operand_type)
            arg.text = operand_value
    
    
    xml_str = tostring(program).decode('utf-8')                 # Convert the XML element tree to a string

    dom = parseString(xml_str)                              
    pretty_xml_str = dom.toprettyxml(indent="   ", newl="\n", encoding='UTF-8').decode('UTF-8')
    
    return pretty_xml_str

def main():                                                     # Main function                      
    
    source_code_lines = read_source_code()                      # Read and preprocess source code
    
    instructions = lexical_analysis(source_code_lines)          # Perform lexical analysis
    
    syntactic_analysis(instructions)                            # Perform syntactic analysis
    
    xml_document = generate_xml(instructions)                   # Generate XML document
    
    print(xml_document)                                         # Print the generated XML document


if __name__ == "__main__":
    main()