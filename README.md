# Headspace

A programming language that fits in your head. Headspace is a simple yet
powerful programming language which compiles to multiple target programming
languages. Envisioned as a way to build cross language libraries, it's pretty
nifty.

## Syntax

Define identifier/variable: `name:type`

Group/code block: `[ ]`

## Examples

### Simple Hello World

A single function program that prints "Hello World" to the terminal.

    main: function[][
      os.write["Hello World\n"]
    ]

## Getting started

To run the unit tests for the Headspace parser and translator, run the script:

    cd v2
    ./run_tests
