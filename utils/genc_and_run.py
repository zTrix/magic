#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import os, sys, tempfile, subprocess

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

cpp.append('%s')
cpp.append('    return 0;')
cpp.append('}')

for line in open(sys.argv[1]):
    if not line.startswith('#') and not line.startswith('//'):
        line = line.split()[0]
        s = '    printf("(%%d, \'%s\'), ", %s);' % (line, line)
        tmp = tempfile.NamedTemporaryFile(suffix='.cpp')
        tmp.write('\n'.join(cpp) % s)
        tmp.flush()
        try:
            # don't pwn yourself!
            subprocess.check_call(['g++', tmp.name, '-o', '/tmp/genc.out', '-O0'], stderr=open('/dev/null', 'w'))
            print subprocess.check_output(['/tmp/genc.out']) 
        except Exception, e:
            print >> sys.stderr, e
            pass
        tmp.close()


