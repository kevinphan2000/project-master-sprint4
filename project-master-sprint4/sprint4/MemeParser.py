from ply import yacc
from MemeLexer import Lexer
from MemeLexer import tokens
import argparse
import sys
import json


class Parser:
    precedence = (
        ('left', 'COMMA'),
        ('left', 'AND'),
        ('left', 'EQOP', 'NEQ'),
        ('left', 'MINUSEQ'),
        ('left', 'PLUSEQ'),
        ('left', 'TIMESEQ'),
        ('left', 'DIVIDEEQ'),
        ('left', 'LESS', 'LESSEQ'),
        ('left', 'GREATER', 'GREATEREQ'),
        ('left', 'OR'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'POW', 'MOD'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'LPAREN', 'RPAREN'),
        ('left', 'LBRACE', 'RBRACE'),
        ('left', 'LBRACKET', 'RBRACKET'),
        ('right', 'NOT')
    )

    '''
    Program Entry Point
    -- The function that is named main is the entry point to the program.
    -- It will be called in the python __name__ == '__main__' block
    '''

    #################################
    # Program Start
    #################################
    def p_program(self, p):
        '''
        program : main_function function_list_or_empty
        '''
        p[0] = {'Node': 'program', 'main': p[1], 'functions': p[2]}
        # if len(p) == 3:
        #     p[0] = ast.Program("PROGRAM", p[1], p[2])
        # else:
        #     p[0] = ast.Program("PROGRAM", p[1], None)

    def p_main_function(self, p):
        '''
        main_function : FUNCTION RTYPE MAIN LPAREN parameter_list_or_empty RPAREN LBRACE stmt_list_or_empty RBRACE
        '''
        p[0] = {'Node': 'main_function', 'rtype': p[2],
                'name': p[3], 'parameters': p[5], 'body': p[8]}
        # p[0] = ast.FuncDecl('MAIN', None, p[7], p[2], None)

    def p_function_list_or_empty(self, p):
        '''
        function_list_or_empty : function function_list_or_empty
                                | empty
        '''
        if len(p) == 2:
            p[0] = []
        else:
            p[0] = [p[1]] + p[2]

    def p_function(self, p):
        '''
        function : FUNCTION RTYPE id_expr LPAREN parameter_list_or_empty RPAREN LBRACE stmt_list_or_empty RBRACE
        '''
        p[0] = {'Node': 'function', 'rtype': p[2],
                'name': p[3], 'parameters': p[5], 'body': p[8]}

    def p_RTYPE(self, p):
        '''
        RTYPE : INTEGER
                | DOUBLE
                | STRING
                | BOOLEAN
                | VOID
        '''
        p[0] = p[1]
        # p[0] = ast.ValStmt(p[1])

    def p_TYPE(self, p):
        '''
        TYPE : INTEGER
                | DOUBLE
                | STRING
                | BOOLEAN
                | LBRACKET TYPE RBRACKET
                | NULL
        '''
        if len(p) == 2:
            p[0] = {'Node': 'TYPE', 'type': p[1]}
        else:
            p[0] = {'Node': 'ARRAY_TYPE', 'type': p[2]}

    def p_VAL(self, p):
        '''
        VAL : INT
            | DOUB
            | STR
            | BOOL
            | NULL
        '''
        p[0] = {'Node': 'LITERAL', 'value': p[1]}
        
    def p_M_VAL(self, p):
        '''
        M_VAL : INT
            | DOUB
        '''
        p[0] = {'Node': 'LITERAL', 'value': p[1]}

    def p_parameter_list_or_empty(self, p):
        '''
        parameter_list_or_empty : parameter COMMA parameter_list_or_empty
                                | parameter
                                | empty
        '''
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_parameter(self, p):
        '''
        parameter : TYPE id_expr
        '''
        p[0] = {'Node': 'parameter', 'type': p[1], 'name': p[2]}

    def p_stmt_list_or_empty(self, p):
        '''
        stmt_list_or_empty : stmt stmt_list_or_empty
                            | empty
        '''
        # This removes the ending Nones and removes the recursive definition of the elements
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[2] is None:
                p[0] = [p[1]]
            else:
                p[0] = [p[1]] + p[2]
        # p[0] = p[1:]

    def p_stmt(self, p):
        '''
        stmt : assign_stmt SEMI
            | if_stmt
            | while_stmt
            | for_stmt
            | print_stmt SEMI
            | return_stmt SEMI
            | CONTINUE SEMI
            | BREAK SEMI
            | function_call SEMI
        '''
        p[0] = p[1]

    def p_assign_stmt(self, p):
        '''
        assign_stmt : TYPE id_expr ASSIGN expr
                    | id_expr ASSIGN expr
                    | array_access ASSIGN expr
        '''
        if len(p) == 5:
            p[0] = {'Node': 'assign_stmt', 'type': p[1], 'name': p[2], 'value': p[4]}
        elif 'index' in p[1]:
            p[0] = {'Node': 'assign_stmt', 'type': p[1], 'name': p[1]['name'], 'index': p[1]['index'], 'value': p[3]}
        else:
            p[0] = {'Node': 'assign_stmt', 'type': 'reassignment', 'name': p[1], 'value': p[3]}

    def p_ASSIGN(self, p):
        '''
        ASSIGN : EQ
                | MINUSEQ
                | PLUSEQ
                | TIMESEQ
                | DIVIDEEQ
        '''
        p[0] = {'Node': 'ASSIGN', 'value': p[1]}

    def p_if_stmt(self, p):
        '''
        if_stmt : if_clause elif_clause_list_or_empty else_clause_or_empty
        '''
        if p[2] == [] and p[3] is None:
            p[0] = {'Node': 'if_block', 'if_clause': p[1]}
        elif p[2] != [] and p[3] is None:
            p[0] = {'Node': 'if_block', 'if_clause':  p[1], 'elif_clause': p[2]}
        elif p[2] == [] and p[3] is not None:
            p[0] = {'Node': 'if_block', 'if_clause':  p[1], 'else_clause': p[3]}
        else:
            p[0] = {'Node': 'if_block', 'if_clause':  p[1], 'elif_clause': p[2], 'else_clause': p[3]}

        # p[0] = {'Node': 'if_block', 'if_clause': p[1], 'elif_clauses': p[2], 'else_clause': p[3]}

    def p_if_clause(self, p):
        '''
        if_clause : IF LPAREN expr RPAREN LBRACE stmt_list_or_empty RBRACE
        '''
        p[0] = {'Node': 'if_clause', 'condition': p[3], 'body': p[6]}

    def p_elif_clause_list_or_empty(self, p):
        '''
        elif_clause_list_or_empty : elif_clause elif_clause_list_or_empty
                                    | empty
        '''
        if len(p) == 2:
            p[0] = []
        else:
            p[0] = [p[1]] + p[2]

    def p_elif_clause(self, p):
        '''
        elif_clause : ELIF LPAREN expr RPAREN LBRACE stmt_list_or_empty RBRACE
        '''
        p[0] = {'Node': 'elif_clause', 'condition': p[3], 'body': p[6]}

    def p_else_clause_or_empty(self, p):
        '''
        else_clause_or_empty : ELSE LBRACE stmt_list_or_empty RBRACE
                               | empty
        '''
        if len(p) == 2:
            p[0] = None
        else:
            p[0] = {'Node': 'else_clause', 'body': p[3]}

    def p_while_stmt(self, p):
        '''
        while_stmt : WHILE LPAREN expr RPAREN LBRACE stmt_list_or_empty RBRACE
        '''
        p[0] = {'Node': 'while_stmt', 'condition': p[3], 'body': p[6]}

    def p_for_stmt(self, p):
        '''
        for_stmt : FOR LPAREN assign_stmt SEMI expr SEMI assign_stmt RPAREN LBRACE stmt_list_or_empty RBRACE
        '''
        p[0] = {'Node': 'for_stmt', 'parameter': p[3], 'condition': p[5], 'update': p[7], 'body': p[10]}

    def p_print_stmt(self, p):
        '''
        print_stmt : PRINT LPAREN expr_list_or_empty RPAREN
        '''
        p[0] = {'Node': 'print_stmt', 'values': p[3]}

    def p_expr_list_or_empty(self, p):
        '''
        expr_list_or_empty : expr COMMA expr_list_or_empty
                            | expr
                            | empty
        '''
        if len(p) == 2:
            if p[1] is None:
                p[0] = []
            else:
                p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]

    def p_expr(self, p):
        '''
        expr : arithmetic_expr
                | bool_expr
                | math_bool_expr
                | id_expr
                | LPAREN expr RPAREN
                | array_expr
                | VAL
                | bool_val
                | function_call
                | array_access
        '''
        if len(p) == 4:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_array_access(self, p):
        '''
        array_access : id_expr LBRACKET expr RBRACKET
        '''
        p[0] = {'Node': 'array_access', 'name': p[1], 'index': p[3]}

    def p_id_expr(self, p):
        '''
        id_expr : ID
        '''
        p[0] = {'Node': 'ID', 'value': p[1]}

    def p_arithmetic_expr(self, p):
        '''
        arithmetic_expr : arithmetic_or_M_VAL_expr PLUS arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr MINUS arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr TIMES arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr DIVIDE arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr MOD arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr POW arithmetic_or_M_VAL_expr
        '''
        p[0] = {'Node': 'arithmetic_expr', 'left': p[1], 'right': p[3], 'op': p[2]}

    def p_bool_val(self, p):
        '''
        bool_val : TRUE
                    | FALSE
        '''
        p[0] = {'Node': 'BOOL_LITERAL', 'value': p[1]}


    def p_arithmetic_or_M_VAL_expr(self, p):
        '''
        arithmetic_or_M_VAL_expr : arithmetic_expr
                                   | M_VAL
                                   | id_expr
                                   | function_call
                                   | math_bool_expr
                                   | array_access
        '''
        p[0] = p[1]

    def p_math_bool_expr(self, p):
        '''
        math_bool_expr : arithmetic_or_M_VAL_expr EQOP arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr NEQ arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr GREATER arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr GREATEREQ arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr LESS arithmetic_or_M_VAL_expr
            | arithmetic_or_M_VAL_expr LESSEQ arithmetic_or_M_VAL_expr
        '''

        p[0] = {'Node': 'math_bool_expr', 'left': p[1], 'right': p[3], 'op': p[2]}


    def p_bool_expr(self, p):
        '''
        bool_expr : expr AND expr
            | expr OR expr
            | NOT expr
        '''
        if len(p) == 4:
            p[0] = {'Node': 'bool_expr', 'left': p[1], 'right': p[3], 'op': p[2]}
        else:
            p[0] = {'Node': 'bool_expr', 'right': p[2], 'left': None, 'op': p[1]}

    def p_array_expr(self, p):
        '''
        array_expr : LBRACKET expr_list_or_empty RBRACKET
        '''
        p[0] = {'Node': 'array_expr', 'values': p[2]}

    def p_return_stmt(self, p):
        '''
        return_stmt : RETURN LPAREN expr_list_or_empty RPAREN
        '''
        p[0] = {'Node': 'return_stmt', 'values': p[3]}

    def p_function_call(self, p):
        '''
        function_call : id_expr LPAREN expr_list_or_empty RPAREN
        '''
        p[0] = {'Node': 'function_call', 'name': p[1], 'values': p[3]}

    def p_empty(self, p):
        '''
        empty :
        '''
        pass

    def parse(self, data):
        return self.parser.parse(data, lexer=self.lexer.lexer)

    def p_error(self, p):
        if p:
            # print("Syntax error at '%s' line %d" % (p.value, p.lineno))
            raise SyntaxError("Syntax error at '%s' line %d" % (p.value, p.lineno))
        else:
            # print("Syntax error at EOF")
            raise SyntaxError("Syntax error at EOF")

    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = Lexer()
        self.lexer.build()
        self.parser = yacc.yacc(module=self, **kwargs, debug=1)

    def test(self, data):
        result = self.parser.parse(data)
        print(json.dumps(result))
        # visitor = ast.NodeVisitor()
        # visitor.visit(result)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]

        with open(filename, 'r') as f:
            data = f.read()

        parser = Parser()
        parser.build()
        parser.test(data)
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
