#!/usr/bin/env python2
#-*- coding:utf-8 -*-

import os, sys, getopt
import termios
import signal
try:
    from termcolor import colored
except:
    def colored(text, color=None, on_color=None, attrs=None):
        return text

TYPE_EQUAL = 'equal'
TYPE_BITOR = 'bitor'

py_magic = {
    'os': {
        'open': {
            'flags': 'O_APPEND O_ASYNC O_CREAT O_DIRECTORY O_DSYNC O_EXCL O_EXLOCK O_NDELAY O_NOCTTY O_NOFOLLOW O_NONBLOCK O_RDONLY O_RDWR O_SHLOCK O_SYNC O_TRUNC O_WRONLY'.split(' '),
            'type': TYPE_BITOR
        },
        'seek': {
            'flags': 'SEEK_SET SEEK_CUR SEEK_END'.split(' '),
            'type': TYPE_EQUAL
        }
    },
    'termios': {
        'iflags': {
            'flags': 'IGNBRK BRKINT IGNPAR PARMRK INPCK ISTRIP INLCR IGNCR ICRNL IUCLC IXON IXANY IXOFF IMAXBEL IUTF8'.split(' '),
            'type': TYPE_BITOR
        },
        'oflags': {
            'flags': 'OPOST OLCUC ONLCR OCRNL ONOCR ONLRET OFILL OFDEL NLDLY CRDLY TABDLY BSDLY VTDLY FFDLY'.split(' '),
            'type': TYPE_BITOR,
        },
        'cflags': {
            'flags': 'CBAUD CBAUDEX CSIZE CSTOPB CREAD PARENB PARODD HUPCL CLOCAL LOBLK CIBAUD CMSPAR CRTSCTS'.split(' '),
            'type': TYPE_BITOR,
        },
        'lflags': {
            'flags': 'ISIG ICANON XCASE ECHO ECHOE ECHOK ECHONL ECHOCTL ECHOPRT ECHOKE DEFECHO FLUSHO NOFLSH TOSTOP PENDIN IEXTEN'.split(' '),
            'type': TYPE_BITOR,
        }
    },
    'signal': {
        'flags': 'NSIG SIGABRT SIGALRM SIGBUS SIGCHLD SIGCONT SIGEMT SIGFPE SIGHUP SIGILL SIGINFO SIGINT SIGIO SIGIOT SIGKILL SIGPIPE SIGPROF SIGQUIT SIGSEGV SIGSTOP SIGSYS SIGTERM SIGTRAP SIGTSTP SIGTTIN SIGTTOU SIGURG SIGUSR1 SIGUSR2 SIGVTALRM SIGWINCH SIGXCPU SIGXFSZ SIG_DFL SIG_IGN'.split(' '),
        'type': TYPE_EQUAL
    },
    'mmap': {
        'access': {
            'flags': 'ACCESS_COPY ACCESS_READ ACCESS_WRITE'.split(' '),
            'type': TYPE_BITOR,
        },
        'prot': {
            'flags': 'PROT_EXEC PROT_READ PROT_WRITE'.split(' '),
            'type': TYPE_BITOR,
        },
        'flags': {
            'flags': 'MAP_ANON MAP_ANONYMOUS MAP_DENYWRITE MAP_EXECUTABLE MAP_PRIVATE MAP_SHARED'.split(' '),
            'type': TYPE_BITOR,
        }
    }
}

magics = {
    'ascii': {
        'flags': [(0, 'nul'), (1, 'soh'), (2, 'stx'), (3, 'etx'), (4, 'eot'), (5, 'enq'), (6, 'ack'), (7, 'bel'), (8, 'bs'), (9, 'ht'), (10, 'nl'), (11, 'vt'), (12, 'np'), (13, 'carriage return'), (14, 'so'), (15, 'si'), (16, 'dle'), (17, 'dc1'), (18, 'dc2'), (19, 'dc3'), (20, 'dc4'), (21, 'nak'), (22, 'syn'), (23, 'etb'), (24, 'can'), (25, 'em'), (26, 'sub'), (27, 'esc'), (28, 'fs'), (29, 'gs'), (30, 'rs'), (31, 'us'), (32, 'space'), (127, 'delete')] + [(x, chr(x)) for x in range(33, 127)],
        'type': TYPE_EQUAL
    }
}

registry = {}

def register(*args, **kwargs):
    def decorator(func):
        def wrapper(*fargs, **fkwargs):
            return func(*fargs, **fkwargs)
        wrapper.func_name = func.func_name
        wrapper.__doc__ == func.__doc__
        if not args:
            registry[wrapper.func_name] = wrapper
        else:
            for k in args:
                registry[wrapper.func_name + '.' + k] = wrapper
    return decorator

def FIND(key, hint): return key.lower().find(hint.lower()) > -1

def magic(number, hints, match = FIND):
    ret = {}

    def match_all(keyword):
        if isinstance(hints, basestring):
            return match(keyword, hints)
        for hint in hints:
            if not match(keyword, hint):
                return False
        return True
        
    # py magics
    modules = {}
    for module in py_magic:
        if module not in modules:
            modules[module] = __import__(module, globals())

        def visit(obj, path):
            if 'flags' in obj and 'type' in obj:
                if not match_all(path): return
                if obj['type'] == TYPE_EQUAL:
                    bits = set()
                    for f in obj['flags']:
                        try:
                            if getattr(modules[module], f) == number:
                                bits.add(f)
                        except: pass
                    if bits:
                        ret[path] = bits
                elif obj['type'] == TYPE_BITOR:
                    bits = []
                    for f in obj['flags']:
                        try:
                            if getattr(modules[module], f) & number:
                                bits.append(f)
                        except: pass
                    if bits:
                        bits.sort()
                        ret[path] = bits
            else:
                for k in obj:
                    visit(obj[k], path + '.' + k)
        
        visit(py_magic[module], module)

    # magics

    for key in magics:
        if not match_all(key):
            continue
        if magics[key]['type'] == TYPE_EQUAL:
            bits = set()
            for n, s in magics[key]['flags']:
                if n == number:
                    bits.add(s)
            if bits:
                ret[key] = bits
        elif magics[key]['type'] == TYPE_BITOR:
            bits = []
            for n, s in magics[key]['flags']:
                if n & number:
                    bits.append(s)
            if bits:
                bits.sort()
                ret[key] = bits
                
    return ret

def usage():
    print """
usage:
    $ magic.py number [keyword | [keyword] ...]

examples:
    $ magic.py 11 open
    $ magic.py 15 signal
    $ magic.py 10240 iflags
"""
    
def main():
    number = 0
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)
    if sys.argv[1].startswith('0x'):
        try:
            number = int(sys.argv[1], 16)
        except:
            usage()
            sys.exit(10)
    else:
        try:
            number = int(sys.argv[1], 10)
        except:
            usage()
            sys.exit(11)
    rs = magic(number, sys.argv[2:])
    if not rs:
        print '0ops, magic number not found :('
        return 0
    for k in rs:
        w = rs[k]
        sys.stdout.write(colored(k, 'yellow') + '\r\n')
        sys.stdout.write('    ' + colored(isinstance(w, list) and ' | '.join(w) or ', '.join(w), 'cyan') + '\r\n')
        sys.stdout.flush()
    return 0

if __name__ == '__main__':
    sys.exit(main())

