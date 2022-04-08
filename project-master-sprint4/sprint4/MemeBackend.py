from MemeParser import Parser
import ply.yacc

from MemeTypeChecking import TypeChecker
from MemeLexer import tokens

import argparse
import sys

# TODO decide if we are making a separate main function or put everytin into if __name__ == '__main__'
# TODO decide if we are doing recursive or for loop style
# It will be a bit easier to do recursive way, I'll start doing that for now
# TODO currently the templates are for normal python code not for the
NEW_LINE = "\n"
# NOTE1: I think for this sprint our goal could be to just output python code not cython
# NOTE2: We could do a work around and do all of the loops as a while loops this will
# currently issue is we are allowing the condition into for loops, while it makes sense in java
# type languages, not so much in python since in python for loops go through iterable or arrays
# kinda like foreach in java
templates = {
    "tab": '    ',
    'main_function': 'def main():',
    'assign_stmt': ' = ',
    'arithmetic_expr': '{} {} {}',  # left op right
    's_print_stmt': 'print(',
    'e_print_stmt': ')',
    's_function_def': 'def ',
    'var_decl': 'cdef ',
    'e_function_def': '):',
    's_array_expr': "[",
    'e_array_expr': "]",
    # 'ARRAY_TYPE': "[]",  # TODO
    # 'TYPE': "[]",  # TODO
    's_for_stmt': 'while ',  # TODO
    'e_for_stmt': ':',  # TODO
    's_if_clause': 'if ',
    'e_if_clause': ':',
    's_elif_clause': 'elif ',
    'e_elif_clause': ':',
    'else_clause': 'else:',
    'return_stmt': 'return ',
    's_function_call': '(',
    'e_function_call': ')',
}


def type_conversion(var_type):
    if var_type == int:
        return 'int '
    elif var_type == float:
        return 'float '
    elif var_type == str:
        return 'str '
    elif var_type == bool:
        return 'bint '


def convert(data, wfile, num_tabs=0):
    """
    This function assumes that the data was already
    somewhat verified and will not throw a lot of errors
    """
    if data['Node'] == 'LITERAL':
        # this is a temporary fix will be fixed with inclusion of types
        if isinstance(data['value'], str):
            wfile.write('"{}"'.format(data['value']))
        else:
            wfile.write('{}'.format(data['value']))
        return
    if data['Node'] == 'BOOL_LITERAL':
        if data['value'] == 'pog':
            wfile.write('True')
        else:
            wfile.write('False')
        return
    if data['Node'] == 'Type':  # i believe the code is currently ignoring this for now
        # TODO this will need to be modified
        wfile.write('{}'.format(data['value']))
        return
    if data['Node'] == 'ID':
        wfile.write(data['value'])
        return
    if data['Node'] == 'main_function':
        wfile.write(NEW_LINE)
        wfile.write(num_tabs * templates['tab'] + templates[data['Node']])
        wfile.write(NEW_LINE)
        for body_elem in data['body']:
            convert(body_elem, wfile, num_tabs + 1)
        wfile.write(NEW_LINE)
        wfile.write(NEW_LINE)
        return
    if data['Node'] == 'assign_stmt':
        wfile.write(num_tabs * templates['tab'])
        if data['type'] == 'reassignment':
            convert(data['name'], wfile)
        elif data['type']['Node'] == 'array_access':
            convert(data['name'], wfile)
            wfile.write(templates['s_array_expr'])
            convert(data['index'], wfile)
            wfile.write(templates['e_array_expr'])
        elif data['type']['Node'] == 'ARRAY_TYPE':
            wfile.write(templates['var_decl'])
            wfile.write('list ')
            convert(data['name'], wfile)
        else:
            wfile.write(templates['var_decl'])
            wfile.write(type_conversion(data['type']['type']))
            convert(data['name'], wfile)

        wfile.write(templates['assign_stmt'])
        convert(data['value'], wfile, 0)
        wfile.write(NEW_LINE)
        return
    if data['Node'] == 'arithmetic_expr':
        convert(data['left'], wfile, 0)
        wfile.write(' ' + data['op'] + ' ')
        convert(data['right'], wfile, 0)
        return
    if data['Node'] == 'bool_expr':
        if data['op'] is None:
            wfile.write(data['left'])  # TODO change this later on ???
        else:
            if not data['left'] is None:
                convert(data['left'], wfile, 0)
                wfile.write(' ')
            wfile.write(data['op'] + ' ')
            convert(data['right'], wfile, 0)
        return
    if data['Node'] == 'print_stmt':
        wfile.write(num_tabs * templates['tab'])
        wfile.write(templates['s_print_stmt'])
        for val in data['values']:
            convert(val, wfile, 0)
        wfile.write(templates['e_print_stmt'])
        wfile.write(NEW_LINE)
        return
    if data['Node'] == 'program':
        # if not data['functions'] is None:
        for function in data['functions']:
            convert(function, wfile)
        convert(data['main'], wfile)
        return
    if data['Node'] == 'parameter':
        convert(data['name'], wfile)
        # wfile.write(data['name'])  # TODO this will need to be changed from just name to include types
        return
    if data['Node'] == 'for_stmt':
        convert(data['parameter'], wfile, num_tabs)
        wfile.write(num_tabs * templates['tab'])
        wfile.write(templates['s_for_stmt'])
        convert(data['condition'], wfile, num_tabs)
        wfile.write(templates['e_for_stmt'])
        wfile.write(NEW_LINE)
        for elem in data['body']:
            convert(elem, wfile, num_tabs + 1)
        convert(data['update'], wfile, num_tabs + 1)
        return
    if data['Node'] == 'return_stmt':
        wfile.write(num_tabs * templates['tab'])
        wfile.write(templates['return_stmt'])
        mx = len(data['values'])
        for i in range(mx):
            convert(data['values'][i], wfile)
            if i + 1 != mx:
                wfile.write(', ')
        if num_tabs != 0:
            wfile.write(NEW_LINE)
        return
    if data['Node'] == 'function_call':
        wfile.write(num_tabs * templates['tab'])
        convert(data['name'], wfile)
        wfile.write(templates['s_function_call'])
        mx = len(data['values'])
        for i in range(mx):
            convert(data['values'][i], wfile)
            if i + 1 != mx:
                wfile.write(', ')
        wfile.write(templates['e_function_call'])
        if num_tabs != 0:
            wfile.write(NEW_LINE)
        return
    if data['Node'] == 'function':
        wfile.write(NEW_LINE)
        wfile.write(templates['s_function_def'])
        convert(data['name'], wfile)
        wfile.write("(")
        # if not data['parameters'] is None:
        mx = len(data['parameters'])
        for i in range(mx):
            convert(data['parameters'][i], wfile)
            if i + 1 != mx:
                wfile.write(', ')
        wfile.write(templates['e_function_def'])
        wfile.write(NEW_LINE)
        for elem in data['body']:
            convert(elem, wfile, num_tabs + 1)
        wfile.write(NEW_LINE)
        wfile.write(NEW_LINE)
        return
    if data['Node'] == 'if_block':
        convert(data['if_clause'], wfile, num_tabs)
        if 'elif_clause' in data:
            for elif_c in data['elif_clause']:
                convert(elif_c, wfile, num_tabs)
        if 'else_clause' in data:
            convert(data['else_clause'], wfile, num_tabs)
        return
    if data['Node'] == 'if_clause':
        wfile.write(num_tabs * templates['tab'])
        wfile.write(templates['s_if_clause'])
        convert(data['condition'], wfile)
        wfile.write(templates['e_if_clause'])
        wfile.write(NEW_LINE)
        for i in data['body']:
            convert(i, wfile, num_tabs + 1)
        return
    if data['Node'] == 'elif_clause':
        wfile.write(num_tabs * templates['tab'])
        wfile.write(templates['s_elif_clause'])
        convert(data['condition'], wfile)
        wfile.write(templates['e_elif_clause'])
        wfile.write(NEW_LINE)
        for i in data['body']:
            convert(i, wfile, num_tabs + 1)
        return
    if data['Node'] == 'else_clause':
        wfile.write(num_tabs * templates['tab'])
        wfile.write(templates['else_clause'])
        wfile.write(NEW_LINE)
        for i in data['body']:
            convert(i, wfile, num_tabs + 1)
        return
    if data['Node'] == 'array_expr':
        wfile.write(templates['s_array_expr'])
        mx = len(data['values'])
        for i in range(mx):
            convert(data['values'][i], wfile)
            if i + 1 != mx:
                wfile.write(', ')
        wfile.write(templates['e_array_expr'])
        return
    if data['Node'] == 'while_stmt':
        wfile.write(num_tabs * templates['tab'])
        wfile.write(templates['s_for_stmt'])
        convert(data['condition'], wfile, 0)
        wfile.write(templates['e_for_stmt'])
        wfile.write(NEW_LINE)
        for elem in data['body']:
            convert(elem, wfile, num_tabs + 1)
        return
    if data['Node'] == 'math_bool_expr':
        convert(data['left'], wfile, 0)
        wfile.write(' ')
        wfile.write(data['op'] + ' ')
        convert(data['right'], wfile, 0)
        return
    if data['Node'] == 'array_access':
        convert(data['name'], wfile)
        wfile.write('[')
        convert(data['index'], wfile)
        wfile.write(']')
        return

    raise TypeError


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]

        with open(filename, 'r') as f:
            data = f.read()

        parser = Parser()
        parser.build()
        p_data = None
        try:
            p_data = parser.parse(data)
        except SyntaxError as e:
            print("**ERROR**", e, "**ERROR**")
            pass

        # TODO: Uncomment this to catch type errors
        # preform type checking
        try:
            type_checker = TypeChecker(p_data)
        except Exception as e:
            print("**ERROR** ", e, "**ERROR**")
            exit(1)
            pass

        if type_checker.error_thrown:
            with open('out.py', 'w') as f:
                f.write('# Error: ' + type_checker.error_thrown)
            exit(1)

        # TODO decide if min function is a mandatory one
        # print(p_data)
        with open('src/out.pyx', 'w') as f:
            convert(p_data, f)
            f.write(NEW_LINE + 'if __name__ == "__main__":' + NEW_LINE)
            f.write(1 * templates['tab'] + 'main()' + NEW_LINE)
            # f.write(1 * templates['tab'] + 'print("Hello")' + NEW_LINE)
    else:
        parser = Parser()
        parser.build()
        while True:
            try:
                s = input('insrt_name > ')
            except EOFError:
                break
            if not s:
                continue
            result = parser.parse(s)
            print(result)
