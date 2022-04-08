#!/usr/bin/env python

from ply import lex
from ply import yacc
import argparse
import re

# TODO : RENAME THIS FILE TO THE NAME OF OUR LANGUAGE
tokens = [
    'ID',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LESS',
    'LESSEQ',
    'GREATER',
    'GREATEREQ',
    'EQOP',
    'NEQ',
    # 'PERIOD',
    'COMMA',
    'EQ',
    'MINUSEQ',
    'PLUSEQ',
    'TIMESEQ',
    'DIVIDEEQ',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LBRACE',
    'RBRACE',
    'SEMI',
    # 'NEWLINE',
    'MOD',
    'POW',
    'INT',
    'DOUB',
    'BOOL',
    'STR',
]

reserved = {
    # 'class': 'CLASS',
    # 'public': 'PUBLIC',   # TODO decide if we should have this
    # 'static': 'STATIC',  # TODO decide if we should have this
    # 'extends': 'EXTENDS',
    'void': 'VOID',
    'main': 'MAIN',
    'pog': 'TRUE',
    'kappa': 'FALSE',
    # 'this': 'SELF',
    # 'new': 'NEW',
    'null': 'NULL',
    'or': 'OR',
    'and': 'AND',
    'oof': 'NOT',
    # 'in': 'IN',
    'words': 'STRING',
    'double': 'DOUBLE',
    'trigger': 'BOOLEAN',
    'DESTRUCTION': 'INTEGER',  # skyrim reference
    'whyAreYou': 'IF',
    'whoSaysIm': 'ELIF',
    'youAre': 'ELSE',
    'yearsStartComing': 'WHILE',
    'illBeBack': 'BREAK',
    "andTheyDontStopComing": 'CONTINUE',
    'NotALoop': 'FOR',
    'takeMyMoney': 'RETURN',
    'family': 'FUNCTION',
    'helloThere': 'PRINT',  # I kinda want to add our printing function as a reserved word
    #  '#': 'COMMENT'
}  # TODO change the reserved words to
# Winter is coming

tokens += reserved.values()


class Lexer(object):
    t_DIVIDE = r'/'
    t_LESS = r'\<'
    t_LESSEQ = r'\<='
    t_GREATER = r'\>'
    t_GREATEREQ = r'\>='
    t_EQOP = r'\=='
    t_NEQ = r'\!='
    t_SEMI = r';'
    # t_PERIOD = r'\.'
    t_COMMA = r','
    t_EQ = r'\='
    t_MINUS = r'\-'
    t_MINUSEQ = r'\-='
    t_PLUSEQ = r'\+='
    t_TIMESEQ = r'\*='
    t_DIVIDEEQ = r'/='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_PLUS = '\+'
    t_ignore = " \t"
    # t_AND = r'\&\&'
    t_OR = r'\|\|'
    t_TIMES = r'\*'
    t_MOD = r'\%'
    t_POW = r'\*\*'

    def t_DOUB(self, t):
        r'\d+\.\d+'
        try:
            t.value = float(t.value)
        except ValueError:
            print("ERROR CONVERSION NUMERO %d", t.value)
        return t

    def t_BOOL(self, t):
        r'True|False'
        t.type = reserved.get(t.value, 'BOOLEAN')
        return t

    def t_COMMENT(self, t):
        r'\#.*%&!'
        pass

    def t_INT(self, t):
        r'\d+'
        try:
            # set the token type to integer
            t.value = int(t.value)
        except ValueError:
            print("ERROR CONVERSION NUMERO %d", t.value)
        return t

    def t_STR(self, t):
        r'\"(\\.|[^\"])*\"'
        t.value = t.value[1:-1]
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'ID')  # Check for reserved words
        return t

    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")
        # t.type = 'NEWLINE'
        # return t

        # Error handling rule. DO NOT MODIFY
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)
    # Build the lexer. DO NOT MODIFY

    def build(self, **kwargs):
        self.tokens = tokens
        self.lexer = lex.lex(module=self, **kwargs)
    # Test the output. DO NOT MODIFY

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


# Main function. DO NOT MODIFY
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Take in the MemoGram source code and perform lexical analysis.')
    parser.add_argument('FILE', help="Input file with MemoGram source code")
    args = parser.parse_args()
    f = open(args.FILE, 'r')
    data = f.read()
    f.close()
    m = Lexer()
    m.build()
    m.test(data)
