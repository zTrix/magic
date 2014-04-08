#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import os, sys

if len(sys.argv) < 2:
    print 'genc.py macro-list-file'
    sys.exit()

cpp = []
cpp.append('#include <cstdio>')
cpp.append('int main() {')

for line in open(sys.argv[1]):
    line = line.strip()
    if not line: continue
    if line.startswith('#'):
        cpp.insert(0, line)
    elif line.startswith('//'):
        continue
    else:
        cpp.append('    printf("(%%d, \'%s\'), ", %s);' % (line, line))

cpp.append('    return 0;')
cpp.append('}')

for line in cpp:
    print line
