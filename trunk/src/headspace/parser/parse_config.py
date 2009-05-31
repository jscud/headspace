#!/usr/bin/env python

STRING_START = ('\'',) # '
STRING_END = ('\'',) # '
ESCAPE_CHAR = ('\\',) # \

GET_MEMBER = ('.',) # .

TYPE_OPERATOR = (':',) # : 

ARGS_START = ('(',) # (
ARGS_END = (')',) # ) 

WHITESPACE = (' ', '\n', '\r', '\t')

COMMENT_START = ('#',)
COMMENT_END = ('\n',)

GROUP_START = ['[', '{']
GROUP_START.extend(ARGS_START)

GROUP_END = [']', '}']
GROUP_END.extend(ARGS_END)

# Other characters which are not valid in a token.
STOP_CHARS = ['!', '@', '$', '%%', '^', '&', '*',  
              '+', '=', '-', '/', '\\', '"', ';', '"']

STOP_CHARS.extend(STRING_START)
STOP_CHARS.extend(STRING_END)
STOP_CHARS.extend(GET_MEMBER)
STOP_CHARS.extend(TYPE_OPERATOR)
STOP_CHARS.extend(GROUP_START)
STOP_CHARS.extend(GROUP_END)
STOP_CHARS.extend(COMMENT_START)
STOP_CHARS.extend(COMMENT_END)
STOP_CHARS.extend(WHITESPACE)

