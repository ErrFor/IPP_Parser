import sys
import re
import xml.etree.ElementTree as ET

def read_input():
    lines = []
    try:
        for line in sys.stdin:
            line = line.strip()
            if line:  # Игнорирование пустых строк
                lines.append(line)
    except EOFError:
        print("Ошибка: не обнаружен ввод. Убедитесь, что программа запущена с корректным вводом.", file=sys.stderr)
        sys.exit(21)  # Используйте соответствующий вашей спецификации код ошибки
    except Exception as e:
        print(f"Неожиданная ошибка при чтении ввода: {e}", file=sys.stderr)
        sys.exit(21)  # Используйте другой код ошибки, если требуется по спецификации

    if not lines:
        print("Ошибка: пустой ввод. Введите код IPPcode24.", file=sys.stderr)
        sys.exit(21)  # Аналогично, соответствующий код ошибки

    return lines


def classify_token(token):
    # Определение ключевых слов IPPcode24
    keywords = {"MOVE", "CREATEFRAME", "PUSHFRAME", "POPFRAME", "DEFVAR", "CALL", "RETURN", "PUSHS", "POPS", "ADD", "SUB", "MUL", "DIV", "LT", "GT", "EQ", "AND", "OR",
                "NOT", "INT2CHAR", "STRI2INT", "READ", "WRITE", "CONCAT", "STRLEN", "GETCHAR", "SETCHAR", "TYPE", "LABEL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ", "EXIT",
                "DPRINT", "BREAK"}
    # Проверка на ключевое слово
    if token.upper() in keywords:
        return ("keyword", token.upper())
    
    # Проверка на идентификатор (примерный паттерн)
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
        return ("identifier", token)
    
    # Проверка на число (целое)
    if re.match(r'^-?\d+$', token):
        return ("integer", int(token))
    
    # Все остальное считается неизвестным
    return ("unknown", token)

def lexical_analysis(lines):
    tokens = []
    for line in lines:
        # Игнорирование комментариев и разбиение на токены
        line = re.sub(r'#.*$', '', line).strip()
        if not line:
            continue
        line_tokens = re.split(r'\s+', line)
        
        # Классификация каждого токена в строке
        classified_tokens = []
        for token in line_tokens:
            classified_token = classify_token(token)
            if classified_token[0] == "unknown":
                print(f"Лексическая ошибка: неизвестный токен '{token}'", file=sys.stderr)
                sys.exit(23)
            classified_tokens.append(classified_token)
        
        tokens.append(classified_tokens)
    return tokens



def syntax_analysis(tokens):
    # Список для хранения ошибок
    errors = []
    
    # Примерная проверка синтаксиса для каждой строки (инструкции)
    for line in tokens:
        # Проверка типа инструкции
        if line[0][0] == "keyword":
            instruction = line[0][1]
            # Пример проверки синтаксиса для инструкции MOVE
            if instruction == "MOVE":
                if len(line) != 3 or line[1][0] != "identifier" or line[2][0] not in ["identifier", "integer"]:
                    errors.append(f"Синтаксическая ошибка в инструкции {instruction}")
            # Можно добавить аналогичные проверки для других инструкций
        else:
            errors.append("Ожидалась инструкция")
    
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        sys.exit(23)

# Пример использования:
# tokens = [['keyword', 'MOVE'], ['identifier', 'var1'], ['integer', 5]]
# syntax_analysis(tokens)


import xml.etree.ElementTree as ET

def generate_xml(tokens):
    # Создание корневого элемента
    program = ET.Element("program")
    program.set('language', 'IPPcode24')

    # Для каждой инструкции в токенах
    for token_line in tokens:
        # Предположим, что первый токен - это тип инструкции
        instruction_element = ET.SubElement(program, "instruction", order=str(token_line[0][1]), opcode=token_line[0][0])
        
        # Добавление аргументов как дочерние элементы
        for i, token in enumerate(token_line[1:], start=1):
            arg_element = ET.SubElement(instruction_element, f"arg{i}", type=token[0])
            arg_element.text = str(token[1])

    # Генерация и возврат строкового представления XML
    return ET.tostring(program, encoding='unicode')

# Пример использования:
# tokens = [[('keyword', 'MOVE'), ('identifier', 'var1'), ('integer', 5)]]
# xml_output = generate_xml(tokens)
# print(xml_output)

def print_help():
    help_message = """
    Использование: python3 [название_вашего_скрипта].py [--help]
    Этот скрипт анализирует код на языке IPPcode24, считывая его из стандартного ввода,
    и генерирует его XML представление на стандартный вывод.

    Параметры:
    --help              Выводит это сообщение о помощи и завершает выполнение программы.
    """
    print(help_message)
    sys.exit(0)

def main():
    if "--help" in sys.argv[1:]:
        print_help()

    lines = read_input()
    tokens = lexical_analysis(lines)
    syntax_analysis(tokens)
    xml_root = generate_xml(tokens)
    print(ET.tostring(xml_root, encoding='unicode'))

if __name__ == "__main__":
    main()
