### Implementation Documentation for Task 1 in IPP 2023/2024

**Name:** Slabik Yaroslav  
**Login:** xslabi01

## Overview

This documentation outlines the `parse.py` script, developed to parse IPPcode24 source code from standard input, ensure its lexical and syntactic correctness, and render it into a standard XML format.

## Philosophy and Approach

The script is designed as a filter, reading from standard input and writing to standard output. The script's structure promotes a clear delineation between input reading, parsing, validation, and XML generation stages.

## Reading Input

The script initiates by reading source code from standard input. It systematically removes comments and unnecessary whitespace to ensure that only relevant code is processed. A vital initial check confirms the presence of the mandatory IPPcode24 header, which signifies the start of the code. Lines are read sequentially until EOF, with each line stripped of trailing newline characters and comments (using `#`). This preprocessing phase is crucial for simplifying subsequent parsing steps.

## Parsing

Parsing involves breaking down the preprocessed input into identifiable tokens. The script employs regular expressions to differentiate between opcodes and operands. Each line of code is split based on whitespace, segregating the opcode from its operands. This tokenization is foundational for the script's lexical analysis, ensuring each token's compliance with IPPcode24's defined syntax. Special attention is given to opcode validation, where the case-insensitive nature of IPPcode24 opcodes is considered, and operand formats are meticulously checked against expected patterns.

## Validating

After parsing, the script validates the syntactic structure of the code. This validation phase includes checking for the correct number and types of operands for each opcode. Utilizing predefined patterns, operands are verified for conformity with their expected data types (e.g., variable identifiers, constants). Error codes specific to IPPcode24 (21 for missing headers, 22 for unknown opcodes, 23 for other lexical or syntax errors) are employed to manage various error conditions effectively. This meticulous validation ensures that the input code not only adheres to lexical standards but also aligns with the syntactic expectations of IPPcode24.

## XML Generation

The validated instructions are then transformed into an XML document that follows the specified XML representation for IPPcode24. Using `xml.etree.ElementTree`, each instruction, along with its operands, is encapsulated within XML elements, maintaining the correct order and capitalization as required. The XML generation process is attentive to IPPcode24's specifications, ensuring accurate representation of the parsed code.