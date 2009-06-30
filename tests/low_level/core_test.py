#!/usr/bin/env python

import unittest
import headspace.low_level.core as low_level
import headspace.parser.lex as lex


class GroupTest(unittest.TestCase):

  def test_group_methods(self):
    g = low_level.Group()
    g.add('x')
    g.add('y', 'test')
    g.add('z')
    self.assertEquals(g.count, 3)
    self.assertEquals(g.getByIndex(1), 'x')
    self.assertEquals(g.getByIndex(2), 'y')
    self.assertEquals(g.getByIndex(3), 'z')
    self.assertEquals(g.getByName('test'), 'y')
    try:
      g.getByName('2')
      self.fail()
    except low_level.LookupFailed:
      pass
    g.set(3, 'z', '2')
    self.assertEquals(g.getByIndex(3), 'z')
    self.assertEquals(g.getByName('2'), 'z')
    self.assertEquals(g.get('2'), 'z')
    self.assertEquals(g.get(2), 'y')


class ParseGroupsTest(unittest.TestCase):

  def test_simple_groups(self):
    groups = low_level.parse_string('[a b c][1 2 3][x y z]')
    self.assertEquals(len(groups), 3)
    for group in groups:
      self.assertEquals(group.count, 3)
    self.assertEquals(groups[0].getByIndex(1), 'a')
    self.assertEquals(groups[0].getByIndex(2), 'b')
    self.assertEquals(groups[0].getByIndex(3), 'c')
    self.assertEquals(groups[1].get(1), '1')
    self.assertEquals(groups[1].get(2), '2')
    self.assertEquals(groups[1].get(3), '3')
    self.assertEquals(groups[2].get(1), 'x')
    self.assertEquals(groups[2].get(2), 'y')
    self.assertEquals(groups[2].get(3), 'z')

  def test_next_member(self):
    reader = low_level.TokenReader(lex.lex_string('one=a 2  = b c d x=e f'))
    self.assertEqual(low_level.next_member(reader), ('one', 'a'))
    self.assertEqual(low_level.next_member(reader), ('2', 'b'))
    self.assertEqual(low_level.next_member(reader), ('c',))
    self.assertEqual(low_level.next_member(reader), ('d',))
    self.assertEqual(low_level.next_member(reader), ('x','e'))
    self.assertEqual(low_level.next_member(reader), ('f',))
    self.assertEqual(low_level.next_member(reader), (None,))
    
  def test_name_groups(self):
    groups = low_level.parse_string(
        '[1 = a 2=b 3=c][first=1 second = 2 third=3][end=w x y one=z]')
    self.assertEquals(len(groups), 3)
    self.assertEquals(groups[0].get('1'), 'a')
    self.assertEquals(groups[0].get(1), 'a')
    self.assertEquals(groups[0].get('2'), 'b')
    self.assertEquals(groups[0].get(2), 'b')
    self.assertEquals(groups[0].get('3'), 'c')
    self.assertEquals(groups[0].get(3), 'c')
    self.assertEquals(groups[1].get('first'), '1')
    self.assertEquals(groups[1].get(1), '1')
    self.assertEquals(groups[1].get('second'), '2')
    self.assertEquals(groups[1].get(2), '2')
    self.assertEquals(groups[2].get('end'), 'w')
    self.assertEquals(groups[2].get(1), 'w')
    self.assertEquals(groups[2].get(2), 'x')
    self.assertEquals(groups[2].get(3), 'y')
    self.assertEquals(groups[2].get(4), 'z')
    self.assertEquals(groups[2].get('one'), 'z')

  def test_nested_groups(self):
    groups = low_level.parse_string('[x [y z]]')
    self.assertEqual(groups[0].get(1), 'x')
    sub = groups[0].get(2)
    self.assertTrue(isinstance(sub, low_level.Group))
    self.assertEqual(sub.get(1), 'y')
    self.assertEqual(sub.get(2), 'z')

    groups = low_level.parse_string('[f g=[[x y]] h]')
    g = groups[0].get('g')
    self.assertEqual(groups[0].count, 3)
    self.assertEqual(g.get(1).get(1), 'x')
    self.assertEqual(g.get(1).get(2), 'y')
    self.assertEqual(groups[0].get(1), 'f')
    self.assertEqual(groups[0].get(3), 'h')

    groups = low_level.parse_string('[g=[[x y=[1 2 3]]]]')
    g = groups[0].get('g')
    self.assertTrue(isinstance(g, low_level.Group))
    self.assertEqual(g.count, 1)
    self.assertEqual(g.get(1).get(1), 'x')
    self.assertEqual(g.get(1).get('y').get(1), '1')
    self.assertEqual(g.get(1).get('y').get(2), '2')
    self.assertEqual(g.get(1).get('y').get(3), '3')

  def test_alternate_start_and_end_markers(self):
    groups = low_level.parse_string('(1 2)[3 4]{5 6}')
    self.assertEqual(len(groups), 3)
    self.assertEqual(groups[0].count, 2)
    self.assertEqual(groups[1].count, 2)
    self.assertEqual(groups[2].count, 2)
    self.assertEqual(groups[0].get(1), '1')
    self.assertEqual(groups[0].get(2), '2')
    self.assertEqual(groups[1].get(1), '3')
    self.assertEqual(groups[2].get(1), '5')

  def test_string_escaping(self):
    groups = low_level.parse_string('(x y=\'a\\\'bc\')')
    self.assertEqual(len(groups), 1)
    self.assertEqual(groups[0].count, 2)
    self.assertEqual(groups[0].get(1), 'x')
    self.assertEqual(groups[0].get(2), "'a\\'bc'")
    self.assertTrue('y' in groups[0].members)

  def test_get_info(self):
    groups = low_level.parse_string('(a next=b 34 c=c)')
    self.assertEqual(len(groups), 1)
    self.assertEqual(groups[0].info(1).name, None)
    self.assertEqual(groups[0].info(1).position, 1)
    self.assertEqual(groups[0].info(pos=1).value, 'a')
    self.assertEqual(groups[0].info(2).name, 'next')
    self.assertEqual(groups[0].info(pos=2).position, 2)
    self.assertEqual(groups[0].info(2).value, 'b')
    self.assertEqual(groups[0].info(name='next').name, 'next')
    self.assertEqual(groups[0].info(name='next').position, 2)
    self.assertEqual(groups[0].info(name='next').value, 'b')

    

def suite():
  return unittest.TestSuite((unittest.makeSuite(ParseGroupsTest,'test'),
                             unittest.makeSuite(GroupTest,'test')))


if __name__ == '__main__':
  unittest.TextTestRunner().run(suite())
