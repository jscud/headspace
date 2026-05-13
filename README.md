# Headspace

A programming language that fits in your head. Headspace is a simple yet
powerful programming language which compiles to multiple target programming
languages. Envisioned as a way to build cross language libraries, it's pretty
nifty.

## Examples

### Simple Hello World

A single function program that prints "Hello World" to the terminal.

    main:function:void(){
      os.print("Hello World\n")
    }

### Declaring and calling Functions

A simple standalone function to demonstrate using types and returning values.

    moduleName = "functions"
    
    addNumbers:function:int32(a:int32, b:int32){
      return a + b
    }
    
    main:function:void(){
      os.printInt(addNumbers(5, 5))
      os.print("\n")
    }

## Getting started

To run the unit tests for the Headspace parser and translator, run the script:

    cd v3
    ./run_tests

## Syntax

Define identifier/variable: `name: type`

Group/code block: `{ }`

Define function: `name: function: return_type (params) {statements}`

Define class: `name: class {members and methods}`


