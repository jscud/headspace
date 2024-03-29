#!/usr/bin/env python
#
# Copyright (C) 2009 Jeffrey William Scudder
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from distutils.core import setup


setup(
    name='headspace',
    version='0.0.1',
    description='Translator and interpreter for the Headspace language.',
    long_description = """\
""",
    author='Jeffrey William Scudder',
    author_email='me@jeffscudder.com',
    license='Apache 2.0',
    url='http://code.google.com/p/headspace/',
    packages=['headspace', 'headspace.parser', 'headspace.low_level'],
    package_dir = {'headspace':'src/headspace'}
)
