#!/usr/bin/env python

import unittest
import headspace.simple.core as simple
import headspace.parser.lex as lex


class ParseStringTest(unittest.TestCase):

  def test_literals(self):
    items = simple.parse_string("'Hello' 'World'")
    self.assertEqual(len(items), 2)
    self.assertTrue(isinstance(items[0], simple.LiteralString))
    self.assertTrue(isinstance(items[1], simple.LiteralString))
    self.assertEqual(items[0].value, '\'Hello\'')
    self.assertEqual(items[1].value, '\'World\'')
    
    items = simple.parse_string('0 12 \'hi\' 3')
    self.assertEqual(len(items), 4)
    self.assertEqual(items[0].value, '0')
    self.assertTrue(isinstance(items[0], simple.LiteralNumber))
    self.assertEqual(items[1].value, '12')
    self.assertTrue(isinstance(items[1], simple.LiteralNumber))
    self.assertEqual(items[2].value, "'hi'")
    self.assertTrue(isinstance(items[2], simple.LiteralString))
    self.assertEqual(items[3].value, '3')
    self.assertTrue(isinstance(items[3], simple.LiteralNumber))


class ParseIdentifierTest(unittest.TestCase):

  def test_simple_identifier(self):
    items = simple.parse_string('x y z')
    self.assertEqual(len(items), 3)
    for item in items:
      self.assertTrue(isinstance(item, simple.Identifier))
    self.assertEqual(items[0].name_chain, ['x'])
    self.assertEqual(items[1].name_chain, ['y'])
    self.assertEqual(items[2].name_chain, ['z'])
    
    items = simple.parse_string("x12 'y' zed 9")
    self.assertEqual(len(items), 4)
    self.assertTrue(isinstance(items[0], simple.Identifier))
    self.assertEqual(items[0].name_chain, ['x12'])
    self.assertTrue(isinstance(items[1], simple.LiteralString))
    self.assertEqual(items[1].value, '\'y\'')
    self.assertTrue(isinstance(items[2], simple.Identifier))
    self.assertEqual(items[2].name_chain, ['zed'])
    self.assertTrue(isinstance(items[3], simple.LiteralNumber))
    self.assertEqual(items[3].value, '9')
    
    items = simple.parse_string("a/b/c d x/y")
    self.assertEqual(len(items), 3)
    for item in items:
      self.assertTrue(isinstance(item, simple.Identifier))
    self.assertEqual(items[0].name_chain, ['a', 'b', 'c'])
    self.assertEqual(items[1].name_chain, ['d'])
    self.assertEqual(items[2].name_chain, ['x', 'y'])


class ParseFunctionTest(unittest.TestCase):

  def test_simple_function(self):
    items = simple.parse_string("print(0='Hello World')")
    self.assertEqual(len(items), 1)
    self.assertTrue(isinstance(items[0], simple.FunctionCall))
    self.assertEqual(items[0].name_chain, ['print'])
    self.assertEqual(len(items[0].members.keys()), 1)
    self.assertEqual(items[0].members['0'].value, '\'Hello World\'')

  def test_nested_functions(self):
    items = simple.parse_string("test/print(x=test/foo/bar() y=(0=1 f=foo(0=temp))) x()")
    self.assertEqual(len(items), 2)
    self.assertTrue(isinstance(items[0], simple.FunctionCall))
    self.assertTrue(isinstance(items[1], simple.FunctionCall))
    self.assertEqual(items[0].name_chain, ['test', 'print'])
    self.assertEqual(items[1].name_chain, ['x'])
    self.assertEqual(items[1].members, {})
    self.assertTrue(isinstance(items[0].members['x'], simple.FunctionCall))
    self.assertEqual(items[0].members['x'].name_chain, ['test', 'foo', 'bar'])
    self.assertEqual(items[0].members['x'].members, {})
    self.assertTrue(isinstance(items[0].members['y'], simple.Group))
    self.assertEqual(items[0].members['y'].members['0'].value, '1')
    self.assertEqual(items[0].members['y'].members['f'].name_chain, ['foo'])
    self.assertEqual(items[0].members['y'].members['f'].members['0'].name_chain, ['temp'])
    
    

class ParseGroupTest(unittest.TestCase):
  
  def test_parse_group(self):
    items = simple.parse_string("(0='Hello' 1='World')")
    self.assertEqual(len(items), 1)
    self.assertTrue(isinstance(items[0], simple.Group))
    self.assertEqual(len(items[0].members.keys()), 2)
    self.assertTrue(isinstance(items[0].members['0'], simple.LiteralString))
    self.assertTrue(isinstance(items[0].members['1'], simple.LiteralString))
    self.assertEqual(items[0].members['0'].value, '\'Hello\'')
    self.assertEqual(items[0].members['1'].value, '\'World\'')

    items = simple.parse_string("(xyz=234 1='test' abc=def)(1 = 3)")
    self.assertEqual(len(items), 2)
    self.assertTrue(isinstance(items[0], simple.Group))
    self.assertTrue(isinstance(items[1], simple.Group))
    self.assertTrue(isinstance(items[0].members['xyz'], simple.LiteralNumber))
    self.assertTrue(isinstance(items[0].members['1'], simple.LiteralString))
    self.assertTrue(isinstance(items[1].members['1'], simple.LiteralNumber))
    self.assertTrue(isinstance(items[0].members['abc'], simple.Identifier))

  def test_nested_group(self):
    items = simple.parse_string("(i=5 x=(0=(j=2) a=() b=5))")
    self.assertEqual(len(items), 1)
    self.assertEqual(items[0].members['i'].value, '5')
    self.assertEqual(items[0].members['x'].members['0'].members['j'].value, '2')
    self.assertEqual(len(items[0].members['x'].members['a'].members.keys()), 0)
    self.assertEqual(items[0].members['x'].members['b'].value, '5')


def suite():
  return unittest.TestSuite((unittest.makeSuite(ParseStringTest,'test'),
                             unittest.makeSuite(ParseIdentifierTest, 'test'),
                             unittest.makeSuite(ParseFunctionTest, 'test'),
                             unittest.makeSuite(ParseGroupTest,'test')))


if __name__ == '__main__':
  unittest.TextTestRunner().run(suite())
