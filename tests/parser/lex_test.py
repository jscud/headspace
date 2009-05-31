#!/usr/bin/env python

import unittest
import headspace.parser.lex as lex

class LexFromStringTest(unittest.TestCase):

  def test_lex_string_literal(self):
    tokens = lex.lex_string('\'ok\'')
    self.assertEquals(tokens, ['\'ok\''])
    tokens = lex.lex_string('\'ok\'.')
    self.assertEquals(tokens, ['\'ok\'', '.'])
    tokens = lex.lex_string('\'ok.\'')
    self.assertEquals(tokens, ['\'ok.\''])
    tokens = lex.lex_string('.\'ok\'')
    self.assertEquals(tokens, ['.', '\'ok\''])

  def test_lex_escaped_string_literal(self):
    # Parses 'ok\''
    tokens = lex.lex_string('\'ok\\\'\'')
    self.assertEquals(tokens, ['\'ok\\\'\''])
    # Parses 'ok\.'
    tokens = lex.lex_string('\'ok\\.\'')
    self.assertEquals(tokens, ['\'ok\\.\''])
    # Parses 'ok\''.
    tokens = lex.lex_string("'ok\\''.")
    self.assertEquals(tokens, ["'ok\\''", '.'])
    tokens = lex.lex_string("@!'ok\\''.")
    self.assertEquals(tokens, ['@', '!', "'ok\\''", '.'])

  def test_lex_ignore_whitespace(self):
    tokens = lex.lex_string('test')
    self.assertEquals(tokens, ['test'])
    tokens = lex.lex_string('        test')
    self.assertEquals(tokens, ['test'])
    tokens = lex.lex_string('  \n\t test')
    self.assertEquals(tokens, ['test'])
    tokens = lex.lex_string('\rtest')
    self.assertEquals(tokens, ['test'])
    tokens = lex.lex_string('test      ')
    self.assertEquals(tokens, ['test'])

  def test_lex_identifier(self):
    tokens = lex.lex_string('a b 1 2 3')
    self.assertEquals(tokens, ['a', 'b', '1', '2', '3'])
    tokens = lex.lex_string('a b 1 2 3')
    self.assertEquals(tokens, ['a', 'b', '1', '2', '3'])

  def test_lex_member_lookup(self):
    tokens = lex.lex_string('\'a\'.b')
    self.assertEquals(tokens, ['\'a\'', '.', 'b'])
    tokens = lex.lex_string('a.b')
    self.assertEquals(tokens, ['a', '.', 'b'])

  def test_lex_comment(self):
    tokens = lex.lex_string('# Simple comment')
    self.assertEquals(tokens, ['# Simple comment'])
    tokens = lex.lex_string('# Simple comment\nx')
    self.assertEquals(tokens, ['# Simple comment', 'x'])

  def test_lex_sample_program(self):
    tokens = lex.lex_string("""
        # Sample program.

        Point:Struct {
          x:Int
          y:Int
        }

        dot:Point
        dot.1 = 5
        dot.y = 7

        print('Dot\\'s x and y are:' dot.x dot.2)""")
    self.assertEquals(tokens, ['# Sample program.', 'Point', ':', 'Struct', 
                               '{', 'x', ':', 'Int', 'y', ':', 'Int', '}', 
                               'dot', ':', 'Point', 'dot', '.', '1', '=', '5',
                               'dot', '.', 'y', '=', '7', 'print', '(', 
                               "'Dot\\'s x and y are:'", 'dot', '.', 'x',
                               'dot', '.', '2', ')'])


def suite():
  return unittest.TestSuite((unittest.makeSuite(LexFromStringTest,'test'),))


if __name__ == '__main__':
  unittest.TextTestRunner().run(suite())
