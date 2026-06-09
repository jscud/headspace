A simpler headspace...

# Declaring a module

```
module "jeffscudder.com/tests/modules_classes/module_a"
```

Inside the module, it's always referred to a `module_a`

# Importing a module

```
import "jeffscudder.com/tests/modules_classes/module_b"
```

Inside the current module, the imported module is always refered to as the final element in the path, `module_b`.

# Describing a type

Here's a simple type that uses a built in type like int or str.

```
type.int
```

Certain markers can be chained, like reference to create a pointer, to a pointer, to a list, of ints.

```
type.ref.ref.list.int
```

Using a built in type, whether the type is local or imported, it should always include the module marker.

```
type.module_a.LocalType
type.module_b.ImportedType
```

When working with references, lists, etc. with module, they can be combined as follows.

```
type.list.ref.module_a.SomeClass
```

# Declaring a variable

```
var variableName type.int
```

# Accessing a value

We can access a chain of members.
```
someInstace.memberLayer1.memberLayer2
```

Accessing members of lists can be done with an index number.
```
someList[0]
```

# Declaring a function

```
function functionName type.ReturnType (param parameterA type.int, param parameterB type.str) {
  code execution statements
}
```

# Declaring a class

```
class ClassName {

  member memberName type.int
  member anotherMember type.module_a.SomeClass

  method methodName type.ReturnType (param parameterA type.int) {
    code execution statements
  }
}
```

Declarations for classes and methods cannot be nested.

# Calling a function.

A function call is indicated by using the function name with groups of parameters.

```
module_a.someFunction(parameterA, instance.parameterB, 5, "some string literal")
```

Function calls can also be nested and the return value used as the parameter value.
```
module_a.differentFunction(module_b.anotherFunction(12, 30))
```


# Design principles

To keep things simpler, there are generally no infix or postfix operations.
Most things looks like a function call. The only infix operator is the . which
establishes a chain of member access. When it comes to parsing, a chain of .
operators is always treated as a group, an atomic unit for processing.

Other key elements include grouping markers like () for function calls, [] for
list/hash-map member access, and {} for blocks of code.
