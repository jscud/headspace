# Design #

Tokens are the following:

  * special characters like ., /, :, =, [, ], {, }, (, and )
  * number and string literals like 99, 'Hello' and 'It\'s good to see you again.\n'
  * identifiers which start with a non-number and do not contain any special characters.

# Examples #

## Simple assignment ##
```
x = 5
```

Has tokens:

```
identifier 'x', symbol '=', number '5'
```

## Simple function call ##

```
printLine('Hello World')
```

Has tokens:

```
identifier 'printLine', symbol '(', string literal 'Hello World', symbol ')'
```