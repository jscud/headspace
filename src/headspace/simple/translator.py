#!/usr/bin/env python

import headspace.simple.core as core


class Error(Exception):
  pass


class Untranslatable(Error):
  pass


def translate_item(item, output_lang):
  # Translate a foreign block of code.
  if isinstance(item, core.FunctionCall) and item.name_chain == ['foreign']:
    if item.members['language'].value == "'%s'" % output_lang:
      return item.members['code'].value[1:-1] # Strip the quotes.
    else:
      return ''
  else:
    raise Untranslatable('Unable to translate %s' % '/'.join(item.name_chain))  
  

def translate_string(s, output_lang):
  items = core.parse_string(s)
  translated = []
  for item in items:
    translated.append(translate_item(item, output_lang))
  return ''.join(translated)
  
  
