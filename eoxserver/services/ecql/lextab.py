# lextab.py. This file automatically created by PLY (version 3.11). Don't edit!
_tabversion   = '3.10'
_lextokens    = set(('AFTER', 'AND', 'ATTRIBUTE', 'BBOX', 'BEFORE', 'BETWEEN', 'BEYOND', 'COMMA', 'CONTAINS', 'CROSSES', 'DISJOINT', 'DIVIDE', 'DURATION', 'DURING', 'DWITHIN', 'ENVELOPE', 'EQ', 'EQUALS', 'FLOAT', 'GE', 'GEOMETRY', 'GT', 'ILIKE', 'IN', 'INTEGER', 'INTERSECTS', 'IS', 'LBRACKET', 'LE', 'LIKE', 'LPAREN', 'LT', 'MINUS', 'NE', 'NOT', 'NULL', 'OR', 'OVERLAPS', 'PLUS', 'QUOTED', 'RBRACKET', 'RELATE', 'RPAREN', 'TIME', 'TIMES', 'TOUCHES', 'UNITS', 'WITHIN', 'feet', 'kilometers', 'meters', 'nautical miles', 'statute miles'))
_lexreflags   = 64
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_GEOMETRY>(POINT\\s*\\(((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))\\))|((MULTIPOINT|LINESTRING)\\s*\\(((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))(\\s*,\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)))*\\))|((MULTIPOINT|MULTILINESTRING|POLYGON)\\s*\\(\\(\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))(\\s*,\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)))*\\s*\\)(\\s*,\\s*\\(\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))(\\s*,\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)))*\\s*\\))*\\))|(MULTIPOLYGON\\s*\\(\\(\\s*\\(\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))(\\s*,\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)))*\\s*\\)(\\s*,\\s*\\(\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))(\\s*,\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)))*\\s*\\))*\\s*\\)(\\s*,\\s*\\(\\s*\\(\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))(\\s*,\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)))*\\s*\\)(\\s*,\\s*\\(\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*))(\\s*,\\s*((-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)|(-?[0-9]*\\.?[0-9]+\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*\\s+-?[0-9]*\\.?[0-9]+\\s*)))*\\s*\\))*\\s*\\))*\\)))|(?P<t_ENVELOPE>ENVELOPE\\s*\\((\\s*-?[0-9]*\\.?[0-9]+\\s*){4}\\))|(?P<t_UNITS>(feet)|(meters)|(statute miles)|(nautical miles)|(kilometers))|(?P<t_TIME>\\d{4}-\\d{2}-\\d{2}T[0-2][0-9]:[0-5][0-9]:[0-5][0-9]Z)|(?P<t_DURATION>P((\\d+Y)?(\\d+M)?(\\d+D)?)?(T(\\d+H)?(\\d+M)?(\\d+S)?)?)|(?P<t_FLOAT>[0-9]*\\.?[0-9]+([eE][-+]?[0-9]+)?)', [None, ('t_GEOMETRY', 'GEOMETRY'), None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, ('t_ENVELOPE', 'ENVELOPE'), None, ('t_UNITS', 'UNITS'), None, None, None, None, None, ('t_TIME', 'TIME'), ('t_DURATION', 'DURATION'), None, None, None, None, None, None, None, None, ('t_FLOAT', 'FLOAT')]), ('(?P<t_INTEGER>[0-9]+)|(?P<t_QUOTED>(\\"[^"]*\\")|(\\\'[^\\\']*\\\'))|(?P<t_ATTRIBUTE>[a-zA-Z_$][0-9a-zA-Z_$]*)|(?P<t_newline>\\n+)|(?P<t_AND>AND)|(?P<t_GE>>=)|(?P<t_LE><=)', [None, ('t_INTEGER', 'INTEGER'), ('t_QUOTED', 'QUOTED'), None, None, ('t_ATTRIBUTE', 'ATTRIBUTE'), ('t_newline', 'newline'), (None, 'AND'), (None, 'GE'), (None, 'LE')]), ('(?P<t_RPAREN>\\))|(?P<t_LPAREN>\\()|(?P<t_NE><>)|(?P<t_OR>OR)|(?P<t_TIMES>\\*)|(?P<t_RBRACKET>\\])|(?P<t_LBRACKET>\\[)|(?P<t_PLUS>\\+)|(?P<t_COMMA>,)|(?P<t_LT><)|(?P<t_EQ>=)|(?P<t_DIVIDE>/)|(?P<t_MINUS>-)|(?P<t_GT>>)', [None, (None, 'RPAREN'), (None, 'LPAREN'), (None, 'NE'), (None, 'OR'), (None, 'TIMES'), (None, 'RBRACKET'), (None, 'LBRACKET'), (None, 'PLUS'), (None, 'COMMA'), (None, 'LT'), (None, 'EQ'), (None, 'DIVIDE'), (None, 'MINUS'), (None, 'GT')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
