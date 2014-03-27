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

py_magic = {
    'os': {
        'open': {
            'flags': 'O_APPEND O_ASYNC O_CREAT O_DIRECTORY O_DSYNC O_EXCL O_EXLOCK O_NDELAY O_NOCTTY O_NOFOLLOW O_NONBLOCK O_RDONLY O_RDWR O_SHLOCK O_SYNC O_TRUNC O_WRONLY'.split(' '),
            'type': 'bitor'
        },
        'seek': {
            'flags': 'SEEK_SET SEEK_CUR SEEK_END'.split(' '),
            'type': 'equal'
        }
    },
    'termios': {
        'iflags': {
            'flags': 'IGNBRK BRKINT IGNPAR PARMRK INPCK ISTRIP INLCR IGNCR ICRNL IUCLC IXON IXANY IXOFF IMAXBEL IUTF8'.split(' '),
            'type': 'bitor'
        },
        'oflags': {
            'flags': 'OPOST OLCUC ONLCR OCRNL ONOCR ONLRET OFILL OFDEL NLDLY CRDLY TABDLY BSDLY VTDLY FFDLY'.split(' '),
            'type': 'bitor',
        },
        'cflags': {
            'flags': 'CBAUD CBAUDEX CSIZE CSTOPB CREAD PARENB PARODD HUPCL CLOCAL LOBLK CIBAUD CMSPAR CRTSCTS'.split(' '),
            'type': 'bitor',
        },
        'lflags': {
            'flags': 'ISIG ICANON XCASE ECHO ECHOE ECHOK ECHONL ECHOCTL ECHOPRT ECHOKE DEFECHO FLUSHO NOFLSH TOSTOP PENDIN IEXTEN'.split(' '),
            'type': 'bitor',
        }
    },
    'signal': {
        'flags': 'NSIG SIGABRT SIGALRM SIGBUS SIGCHLD SIGCONT SIGEMT SIGFPE SIGHUP SIGILL SIGINFO SIGINT SIGIO SIGIOT SIGKILL SIGPIPE SIGPROF SIGQUIT SIGSEGV SIGSTOP SIGSYS SIGTERM SIGTRAP SIGTSTP SIGTTIN SIGTTOU SIGURG SIGUSR1 SIGUSR2 SIGVTALRM SIGWINCH SIGXCPU SIGXFSZ SIG_DFL SIG_IGN'.split(' '),
        'type': 'equal'
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
                if obj['type'] == 'equal':
                    for f in obj['flags']:
                        try:
                            if getattr(modules[module], f) == number:
                                ret[path] = f
                                break
                        except: pass
                elif obj['type'] == 'bitor':
                    bits = []
                    for f in obj['flags']:
                        try:
                            if getattr(modules[module], f) & number:
                                bits.append(f)
                        except: pass
                    if bits:
                        ret[path] = bits
            else:
                for k in obj:
                    visit(obj[k], path + '.' + k)
        
        visit(py_magic[module], module)
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
    for k in rs:
        w = rs[k]
        sys.stdout.write(colored(k, 'yellow') + '\r\n')
        sys.stdout.write('    ' + colored(isinstance(w, list) and ' | '.join(w) or w, 'cyan') + '\r\n')
        sys.stdout.flush()
    if len(rs) == 0:
        print '0ops, magic number not found :('

if __name__ == '__main__':
    main()

