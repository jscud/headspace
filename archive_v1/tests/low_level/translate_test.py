#!/usr/bin/env python

import unittest
import headspace.low_level.translate as simple_translate
import headspace.low_level.core as low_level


class ForignCodeToModuleTest(unittest.TestCase):

  def test_add_statements(self):
    module = simple_translate.string_to_module(
        '[foreign C run \'printf("Hello World!\\n");\']', 'C')
    self.assertEqual(len(module.imports), 0)
    self.assertEqual(len(module.declarations), 0)
    self.assertEqual(len(module.statements), 1)
    self.assertEqual(module.statements[0], 'printf("Hello World!\\n");')

class LangBlockTest(unittest.TestCase):
  
  def test_keep_literal_string(self):
    translated = simple_translate.translate_string(
        '(foreign python \'print "hello world"\')', 'python')
    self.assertEqual(translated, "print \"hello world\"")


class AssignmentTest(unittest.TestCase):
  
  def test_translate_var_to_int_literal(self):
    assignment = simple_translate.Assignment('number', '7')
    self.assertEqual(assignment.translate(simple_translate.PYTHON), 
                     'number = 7')
    self.assertEqual(assignment.translate(simple_translate.JS), 
                     'number = 7;')
    self.assertEqual(assignment.translate(simple_translate.JAVA), 
                     'number = 7;')
    self.assertEqual(assignment.translate(simple_translate.C), 
                     'number = 7;')
    self.assertEqual(assignment.translate(simple_translate.PHP), 
                     '$number = 7;')

class VarDeclarationTest(unittest.TestCase):

  def test_translate_int_declaration(self):
    declaration = simple_translate.VariableDeclaration('number', 'int')
    self.assertEqual(declaration.translate(simple_translate.PYTHON), '')
    self.assertEqual(declaration.translate(simple_translate.JS), '')
    self.assertEqual(declaration.translate(simple_translate.PHP), '')
    self.assertEqual(declaration.translate(simple_translate.C), 
                     'int number;')
    self.assertEqual(declaration.translate(simple_translate.JAVA), 
                     'int number;')

class GroupTest(unittest.TestCase):

  def test_translate_simple(self):
    program = '[var number int][set number 7]'
    self.assertEqual(
        simple_translate.translate_string(program, simple_translate.JAVA),
        'int number;\nnumber = 7;')
    self.assertEqual(
        simple_translate.translate_string(program, simple_translate.C),
        'int number;\nnumber = 7;')
    self.assertEqual(
        simple_translate.translate_string(program, simple_translate.JS),
        'number = 7;')
    self.assertEqual(
        simple_translate.translate_string(program, simple_translate.PYTHON),
        'number = 7')
    self.assertEqual(
        simple_translate.translate_string(program, simple_translate.PHP),
        '$number = 7;')

class HelloWorldTest(unittest.TestCase):
 
  def test_print_hello_world(self):
    program = '(main (print \'Hello World!\'))'
    self.assertEqual(simple_translate.translate_string(program, 
        simple_translate.PYTHON), 'if __name__ == \'__main__\':\n...')
        #TODO: left off here.


def suite():
  return unittest.TestSuite(
      (unittest.makeSuite(ForignCodeToModuleTest, 'test')))


if __name__ == '__main__':
  unittest.TextTestRunner().run(suite())
