#!/usr/bin/env python

import unittest
import headspace.simple.core as simple
import headspace.simple.translator as translator


class ForiegnTest(unittest.TestCase):

  def test_foreign_only(self):
    translated = translator.translate_string(foreign_only, 'c')
    self.assertEqual(translated, just_c)
    #print translated 
    


def suite():
  return unittest.TestSuite((unittest.makeSuite(ForiegnTest,'test'),
                             ))


foreign_only = """
foreign(language='c' code='
#include<stdio.h>

int main() {
  printf("Hello world.\\n");
}
')
foreign(language='Java' code='
class AllForeign {

  public static void main() {
    System.out.println("Hello world");
  }

}
')
foreign(language='Python' code='
print "Hello world"
')
"""

just_c = """
#include<stdio.h>

int main() {
  printf("Hello world.\\n");
}
"""

if __name__ == '__main__':
  unittest.TextTestRunner().run(suite())
