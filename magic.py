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
    },
    'errno': {
        'flags': 'E2BIG EACCES EADDRINUSE EADDRNOTAVAIL EAFNOSUPPORT EAGAIN EALREADY EAUTH EBADARCH EBADEXEC EBADF EBADMACHO EBADMSG EBADRPC EBUSY ECANCELED ECHILD ECONNABORTED ECONNREFUSED ECONNRESET EDEADLK EDESTADDRREQ EDEVERR EDOM EDQUOT EEXIST EFAULT EFBIG EFTYPE EHOSTDOWN EHOSTUNREACH EIDRM EILSEQ EINPROGRESS EINTR EINVAL EIO EISCONN EISDIR ELOOP EMFILE EMLINK EMSGSIZE EMULTIHOP ENAMETOOLONG ENEEDAUTH ENETDOWN ENETRESET ENETUNREACH ENFILE ENOATTR ENOBUFS ENODATA ENODEV ENOENT ENOEXEC ENOLCK ENOLINK ENOMEM ENOMSG ENOPOLICY ENOPROTOOPT ENOSPC ENOSR ENOSTR ENOSYS ENOTBLK ENOTCONN ENOTDIR ENOTEMPTY ENOTRECOVERABLE ENOTSOCK ENOTSUP ENOTTY ENXIO EOPNOTSUPP EOVERFLOW EOWNERDEAD EPERM EPFNOSUPPORT EPIPE EPROCLIM EPROCUNAVAIL EPROGMISMATCH EPROGUNAVAIL EPROTO EPROTONOSUPPORT EPROTOTYPE EPWROFF ERANGE EREMOTE EROFS ERPCMISMATCH ESHLIBVERS ESHUTDOWN ESOCKTNOSUPPORT ESPIPE ESRCH ESTALE ETIME ETIMEDOUT ETOOMANYREFS ETXTBSY EUSERS EWOULDBLOCK EXDEV'.split(' '),
        'type': TYPE_EQUAL,
    }
}

magics = {
    'ascii': {
        'flags': [(0, 'nul'), (1, 'soh'), (2, 'stx'), (3, 'etx'), (4, 'eot'), (5, 'enq'), (6, 'ack'), (7, 'bel'), (8, 'bs'), (9, 'ht'), (10, 'nl'), (11, 'vt'), (12, 'np'), (13, 'carriage return'), (14, 'so'), (15, 'si'), (16, 'dle'), (17, 'dc1'), (18, 'dc2'), (19, 'dc3'), (20, 'dc4'), (21, 'nak'), (22, 'syn'), (23, 'etb'), (24, 'can'), (25, 'em'), (26, 'sub'), (27, 'esc'), (28, 'fs'), (29, 'gs'), (30, 'rs'), (31, 'us'), (32, 'space'), (127, 'delete')] + [(x, chr(x)) for x in range(33, 127)],
        'type': TYPE_EQUAL
    },
    'prctl': {
        'flags': [(23, 'PR_CAPBSET_READ'),  (24, 'PR_CAPBSET_DROP'),  (36, 'PR_SET_CHILD_SUBREAPER'),  (37, 'PR_GET_CHILD_SUBREAPER'),  (4, 'PR_SET_DUMPABLE'),  (3, 'PR_GET_DUMPABLE'),  (20, 'PR_SET_ENDIAN'),  (19, 'PR_GET_ENDIAN'),  (10, 'PR_SET_FPEMU'),  (9, 'PR_GET_FPEMU'),  (12, 'PR_SET_FPEXC'),  (11, 'PR_GET_FPEXC'),  (8, 'PR_SET_KEEPCAPS'),  (7, 'PR_GET_KEEPCAPS'),  (15, 'PR_SET_NAME'),  (16, 'PR_GET_NAME'),  (38, 'PR_SET_NO_NEW_PRIVS'),  (39, 'PR_GET_NO_NEW_PRIVS'),  (1, 'PR_SET_PDEATHSIG'),  (2, 'PR_GET_PDEATHSIG'),  (1499557217, 'PR_SET_PTRACER'),  (22, 'PR_SET_SECCOMP'),  (21, 'PR_GET_SECCOMP'),  (28, 'PR_SET_SECUREBITS'),  (27, 'PR_GET_SECUREBITS'),  (40, 'PR_GET_TID_ADDRESS'),  (29, 'PR_SET_TIMERSLACK'),  (30, 'PR_GET_TIMERSLACK'),  (14, 'PR_SET_TIMING'),  (13, 'PR_GET_TIMING'),  (31, 'PR_TASK_PERF_EVENTS_DISABLE'),  (32, 'PR_TASK_PERF_EVENTS_ENABLE'),  (26, 'PR_SET_TSC'),  (25, 'PR_GET_TSC'),  (6, 'PR_SET_UNALIGN'),  (5, 'PR_GET_UNALIGN'),  (33, 'PR_MCE_KILL'),  (34, 'PR_MCE_KILL_GET'),  (35, 'PR_SET_MM')],
        'type': TYPE_EQUAL
    },
    'ptrace': {
        'flags': [(0, 'PTRACE_TRACEME'), (1, 'PTRACE_PEEKTEXT'), (2, 'PTRACE_PEEKDATA'), (3, 'PTRACE_PEEKUSER'), (4, 'PTRACE_POKETEXT'), (5, 'PTRACE_POKEDATA'), (6, 'PTRACE_POKEUSER'), (12, 'PTRACE_GETREGS'), (14, 'PTRACE_GETFPREGS'), (16900, 'PTRACE_GETREGSET'), (16898, 'PTRACE_GETSIGINFO'), (13, 'PTRACE_SETREGS'), (15, 'PTRACE_SETFPREGS'), (16901, 'PTRACE_SETREGSET'), (16899, 'PTRACE_SETSIGINFO'), (16896, 'PTRACE_SETOPTIONS'), (1048576, 'PTRACE_O_EXITKILL'), (8, 'PTRACE_O_TRACECLONE'), (16, 'PTRACE_O_TRACEEXEC'), (64, 'PTRACE_O_TRACEEXIT'), (2, 'PTRACE_O_TRACEFORK'), (1, 'PTRACE_O_TRACESYSGOOD'), (4, 'PTRACE_O_TRACEVFORK'), (32, 'PTRACE_O_TRACEVFORKDONE'), (16897, 'PTRACE_GETEVENTMSG'), (7, 'PTRACE_CONT'), (24, 'PTRACE_SYSCALL'), (9, 'PTRACE_SINGLESTEP'), (16904, 'PTRACE_LISTEN'), (8, 'PTRACE_KILL'), (16903, 'PTRACE_INTERRUPT'), (16, 'PTRACE_ATTACH'), (16902, 'PTRACE_SEIZE'), (17, 'PTRACE_DETACH'), (31, 'PTRACE_SYSEMU'), (32, 'PTRACE_SYSEMU_SINGLESTEP')],
        'type': TYPE_EQUAL
    },
    'syscall': {
        'linux': {
            'i386': {
                'flags': [(0,"sys_setup"),(1,"sys_exit"),(2,"sys_fork"),(3,"sys_read"),(4,"sys_write"),(5,"sys_open"),(6,"sys_close"),(7,"sys_waitpid"),(8,"sys_creat"),(9,"sys_link"),(10,"sys_unlink"),(11,"sys_execve"),(12,"sys_chdir"),(13,"sys_time"),(14,"sys_mknod"),(15,"sys_chmod"),(16,"sys_lchown"),(17,"sys_break"),(18,"sys_oldstat"),(19,"sys_lseek"),(20,"sys_getpid"),(21,"sys_mount"),(22,"sys_umount"),(23,"sys_setuid"),(24,"sys_getuid"),(25,"sys_stime"),(26,"sys_ptrace"),(27,"sys_alarm"),(28,"sys_oldfstat"),(29,"sys_pause"),(30,"sys_utime"),(31,"sys_stty"),(32,"sys_gtty"),(33,"sys_access"),(34,"sys_nice"),(35,"sys_ftime"),(36,"sys_sync"),(37,"sys_kill"),(38,"sys_rename"),(39,"sys_mkdir"),(40,"sys_rmdir"),(41,"sys_dup"),(42,"sys_pipe"),(43,"sys_times"),(44,"sys_prof"),(45,"sys_brk"),(46,"sys_setgid"),(47,"sys_getgid"),(48,"sys_signal"),(49,"sys_geteuid"),(50,"sys_getegid"),(51,"sys_acct"),(52,"sys_umount2"),(53,"sys_lock"),(54,"sys_ioctl"),(55,"sys_fcntl"),(56,"sys_mpx"),(57,"sys_setpgid"),(58,"sys_ulimit"),(59,"sys_oldolduname"),(60,"sys_umask"),(61,"sys_chroot"),(62,"sys_ustat"),(63,"sys_dup2"),(64,"sys_getppid"),(65,"sys_getpgrp"),(66,"sys_setsid"),(67,"sys_sigaction"),(68,"sys_sgetmask"),(69,"sys_ssetmask"),(70,"sys_setreuid"),(71,"sys_setregid"),(72,"sys_sigsuspend"),(73,"sys_sigpending"),(74,"sys_sethostname"),(75,"sys_setrlimit"),(76,"sys_getrlimit"),(77,"sys_getrusage"),(78,"sys_gettimeofday"),(79,"sys_settimeofday"),(80,"sys_getgroups"),(81,"sys_setgroups"),(82,"sys_select"),(83,"sys_symlink"),(84,"sys_oldlstat"),(85,"sys_readlink"),(86,"sys_uselib"),(87,"sys_swapon"),(88,"sys_reboot"),(89,"sys_readdir"),(90,"sys_mmap"),(91,"sys_munmap"),(92,"sys_truncate"),(93,"sys_ftruncate"),(94,"sys_fchmod"),(95,"sys_fchown"),(96,"sys_getpriority"),(97,"sys_setpriority"),(98,"sys_profil"),(99,"sys_statfs"),(100,"sys_fstatfs"),(101,"sys_ioperm"),(102,"sys_socketcall"),(103,"sys_syslog"),(104,"sys_setitimer"),(105,"sys_getitimer"),(106,"sys_stat"),(107,"sys_lstat"),(108,"sys_fstat"),(109,"sys_olduname"),(110,"sys_iopl"),(111,"sys_vhangup"),(112,"sys_idle"),(113,"sys_vm86old"),(114,"sys_wait4"),(115,"sys_swapoff"),(116,"sys_sysinfo"),(117,"sys_ipc"),(118,"sys_fsync"),(119,"sys_sigreturn"),(120,"sys_clone"),(121,"sys_setdomainname"),(122,"sys_uname"),(123,"sys_modify_ldt"),(124,"sys_adjtimex"),(125,"sys_mprotect"),(126,"sys_sigprocmask"),(127,"sys_create_module"),(128,"sys_init_module"),(129,"sys_delete_module"),(130,"sys_get_kernel_syms"),(131,"sys_quotactl"),(132,"sys_getpgid"),(133,"sys_fchdir"),(134,"sys_bdflush"),(135,"sys_sysfs"),(136,"sys_personality"),(137,"sys_afs_syscall"),(138,"sys_setfsuid"),(139,"sys_setfsgid"),(140,"sys__llseek"),(141,"sys_getdents"),(142,"sys__newselect"),(143,"sys_flock"),(144,"sys_msync"),(145,"sys_readv"),(146,"sys_writev"),(147,"sys_getsid"),(148,"sys_fdatasync"),(149,"sys__sysctl"),(150,"sys_mlock"),(151,"sys_munlock"),(152,"sys_mlockall"),(153,"sys_munlockall"),(154,"sys_sched_setparam"),(155,"sys_sched_getparam"),(156,"sys_sched_setscheduler"),(157,"sys_sched_getscheduler"),(158,"sys_sched_yield"),(159,"sys_sched_get_priority_max"),(160,"sys_sched_get_priority_min"),(161,"sys_sched_rr_get_interval"),(162,"sys_nanosleep"),(163,"sys_mremap"),(164,"sys_setresuid"),(165,"sys_getresuid"),(166,"sys_vm86"),(167,"sys_query_module"),(168,"sys_poll"),(169,"sys_nfsservctl"),(170,"sys_setresgid"),(171,"sys_getresgid"),(172,"sys_prctl"),(173,"sys_rt_sigreturn"),(174,"sys_rt_sigaction"),(175,"sys_rt_sigprocmask"),(176,"sys_rt_sigpending"),(177,"sys_rt_sigtimedwait"),(178,"sys_rt_sigqueueinfo"),(179,"sys_rt_sigsuspend"),(180,"sys_pread"),(181,"sys_pwrite"),(182,"sys_chown"),(183,"sys_getcwd"),(184,"sys_capget"),(185,"sys_capset"),(186,"sys_sigaltstack"),(187,"sys_sendfile"),(188,"sys_getpmsg"),(189,"sys_putpmsg"),(190,"sys_vfork")],
                'type': TYPE_EQUAL
            },
            'x64': {
                'flags': [(0,"sys_read"),(1,"sys_write"),(2,"sys_open"),(3,"sys_close"),(4,"sys_stat"),(5,"sys_fstat"),(6,"sys_lstat"),(7,"sys_poll"),(8,"sys_lseek"),(9,"sys_mmap"),(10,"sys_mprotect"),(11,"sys_munmap"),(12,"sys_brk"),(13,"sys_rt_sigaction"),(14,"sys_rt_sigprocmask"),(15,"sys_rt_sigreturn"),(16,"sys_ioctl"),(17,"sys_pread64"),(18,"sys_pwrite64"),(19,"sys_readv"),(20,"sys_writev"),(21,"sys_access"),(22,"sys_pipe"),(23,"sys_select"),(24,"sys_sched_yield"),(25,"sys_mremap"),(26,"sys_msync"),(27,"sys_mincore"),(28,"sys_madvise"),(29,"sys_shmget"),(30,"sys_shmat"),(31,"sys_shmctl"),(32,"sys_dup"),(33,"sys_dup2"),(34,"sys_pause"),(35,"sys_nanosleep"),(36,"sys_getitimer"),(37,"sys_alarm"),(38,"sys_setitimer"),(39,"sys_getpid"),(40,"sys_sendfile"),(41,"sys_socket"),(42,"sys_connect"),(43,"sys_accept"),(44,"sys_sendto"),(45,"sys_recvfrom"),(46,"sys_sendmsg"),(47,"sys_recvmsg"),(48,"sys_shutdown"),(49,"sys_bind"),(50,"sys_listen"),(51,"sys_getsockname"),(52,"sys_getpeername"),(53,"sys_socketpair"),(54,"sys_setsockopt"),(55,"sys_getsockopt"),(56,"sys_clone"),(57,"sys_fork"),(58,"sys_vfork"),(59,"sys_execve"),(60,"sys_exit"),(61,"sys_wait4"),(62,"sys_kill"),(63,"sys_uname"),(64,"sys_semget"),(65,"sys_semop"),(66,"sys_semctl"),(67,"sys_shmdt"),(68,"sys_msgget"),(69,"sys_msgsnd"),(70,"sys_msgrcv"),(71,"sys_msgctl"),(72,"sys_fcntl"),(73,"sys_flock"),(74,"sys_fsync"),(75,"sys_fdatasync"),(76,"sys_truncate"),(77,"sys_ftruncate"),(78,"sys_getdents"),(79,"sys_getcwd"),(80,"sys_chdir"),(81,"sys_fchdir"),(82,"sys_rename"),(83,"sys_mkdir"),(84,"sys_rmdir"),(85,"sys_creat"),(86,"sys_link"),(87,"sys_unlink"),(88,"sys_symlink"),(89,"sys_readlink"),(90,"sys_chmod"),(91,"sys_fchmod"),(92,"sys_chown"),(93,"sys_fchown"),(94,"sys_lchown"),(95,"sys_umask"),(96,"sys_gettimeofday"),(97,"sys_getrlimit"),(98,"sys_getrusage"),(99,"sys_sysinfo"),(100,"sys_times"),(101,"sys_ptrace"),(102,"sys_getuid"),(103,"sys_syslog"),(104,"sys_getgid"),(105,"sys_setuid"),(106,"sys_setgid"),(107,"sys_geteuid"),(108,"sys_getegid"),(109,"sys_setpgid"),(110,"sys_getppid"),(111,"sys_getpgrp"),(112,"sys_setsid"),(113,"sys_setreuid"),(114,"sys_setregid"),(115,"sys_getgroups"),(116,"sys_setgroups"),(117,"sys_setresuid"),(118,"sys_getresuid"),(119,"sys_setresgid"),(120,"sys_getresgid"),(121,"sys_getpgid"),(122,"sys_setfsuid"),(123,"sys_setfsgid"),(124,"sys_getsid"),(125,"sys_capget"),(126,"sys_capset"),(127,"sys_rt_sigpending"),(128,"sys_rt_sigtimedwait"),(129,"sys_rt_sigqueueinfo"),(130,"sys_rt_sigsuspend"),(131,"sys_sigaltstack"),(132,"sys_utime"),(133,"sys_mknod"),(134,"sys_uselib"),(135,"sys_personality"),(136,"sys_ustat"),(137,"sys_statfs"),(138,"sys_fstatfs"),(139,"sys_sysfs"),(140,"sys_getpriority"),(141,"sys_setpriority"),(142,"sys_sched_setparam"),(143,"sys_sched_getparam"),(144,"sys_sched_setscheduler"),(145,"sys_sched_getscheduler"),(146,"sys_sched_get_priority_max"),(147,"sys_sched_get_priority_min"),(148,"sys_sched_rr_get_interval"),(149,"sys_mlock"),(150,"sys_munlock"),(151,"sys_mlockall"),(152,"sys_munlockall"),(153,"sys_vhangup"),(154,"sys_modify_ldt"),(155,"sys_pivot_root"),(156,"sys__sysctl"),(157,"sys_prctl"),(158,"sys_arch_prctl"),(159,"sys_adjtimex"),(160,"sys_setrlimit"),(161,"sys_chroot"),(162,"sys_sync"),(163,"sys_acct"),(164,"sys_settimeofday"),(165,"sys_mount"),(166,"sys_umount2"),(167,"sys_swapon"),(168,"sys_swapoff"),(169,"sys_reboot"),(170,"sys_sethostname"),(171,"sys_setdomainname"),(172,"sys_iopl"),(173,"sys_ioperm"),(174,"sys_create_module"),(175,"sys_init_module"),(176,"sys_delete_module"),(177,"sys_get_kernel_syms"),(178,"sys_query_module"),(179,"sys_quotactl"),(180,"sys_nfsservctl"),(181,"sys_getpmsg"),(182,"sys_putpmsg"),(183,"sys_afs_syscall"),(184,"sys_tuxcall"),(185,"sys_security"),(186,"sys_gettid"),(187,"sys_readahead"),(188,"sys_setxattr"),(189,"sys_lsetxattr"),(190,"sys_fsetxattr"),(191,"sys_getxattr"),(192,"sys_lgetxattr"),(193,"sys_fgetxattr"),(194,"sys_listxattr"),(195,"sys_llistxattr"),(196,"sys_flistxattr"),(197,"sys_removexattr"),(198,"sys_lremovexattr"),(199,"sys_fremovexattr"),(200,"sys_tkill"),(201,"sys_time"),(202,"sys_futex"),(203,"sys_sched_setaffinity"),(204,"sys_sched_getaffinity"),(205,"sys_set_thread_area"),(206,"sys_io_setup"),(207,"sys_io_destroy"),(208,"sys_io_getevents"),(209,"sys_io_submit"),(210,"sys_io_cancel"),(211,"sys_get_thread_area"),(212,"sys_lookup_dcookie"),(213,"sys_epoll_create"),(214,"sys_epoll_ctl_old"),(215,"sys_epoll_wait_old"),(216,"sys_remap_file_pages"),(217,"sys_getdents64"),(218,"sys_set_tid_address"),(219,"sys_restart_syscall"),(220,"sys_semtimedop"),(221,"sys_fadvise64"),(222,"sys_timer_create"),(223,"sys_timer_settime"),(224,"sys_timer_gettime"),(225,"sys_timer_getoverrun"),(226,"sys_timer_delete"),(227,"sys_clock_settime"),(228,"sys_clock_gettime"),(229,"sys_clock_getres"),(230,"sys_clock_nanosleep"),(231,"sys_exit_group"),(232,"sys_epoll_wait"),(233,"sys_epoll_ctl"),(234,"sys_tgkill"),(235,"sys_utimes"),(236,"sys_vserver"),(237,"sys_mbind"),(238,"sys_set_mempolicy"),(239,"sys_get_mempolicy"),(240,"sys_mq_open"),(241,"sys_mq_unlink"),(242,"sys_mq_timedsend"),(243,"sys_mq_timedreceive"),(244,"sys_mq_notify"),(245,"sys_mq_getsetattr"),(246,"sys_kexec_load"),(247,"sys_waitid"),(248,"sys_add_key"),(249,"sys_request_key"),(250,"sys_keyctl"),(251,"sys_ioprio_set"),(252,"sys_ioprio_get"),(253,"sys_inotify_init"),(254,"sys_inotify_add_watch"),(255,"sys_inotify_rm_watch"),(256,"sys_migrate_pages"),(257,"sys_openat"),(258,"sys_mkdirat"),(259,"sys_mknodat"),(260,"sys_fchownat"),(261,"sys_futimesat"),(262,"sys_newfstatat"),(263,"sys_unlinkat"),(264,"sys_renameat"),(265,"sys_linkat"),(266,"sys_symlinkat"),(267,"sys_readlinkat"),(268,"sys_fchmodat"),(269,"sys_faccessat"),(270,"sys_pselect6"),(271,"sys_ppoll"),(272,"sys_unshare"),(273,"sys_set_robust_list"),(274,"sys_get_robust_list"),(275,"sys_splice"),(276,"sys_tee"),(277,"sys_sync_file_range"),(278,"sys_vmsplice"),(279,"sys_move_pages"),(280,"sys_utimensat"),(281,"sys_epoll_pwait"),(282,"sys_signalfd"),(283,"sys_timerfd_create"),(284,"sys_eventfd"),(285,"sys_fallocate"),(286,"sys_timerfd_settime"),(287,"sys_timerfd_gettime"),(288,"sys_accept4"),(289,"sys_signalfd4"),(290,"sys_eventfd2"),(291,"sys_epoll_create1"),(292,"sys_dup3"),(293,"sys_pipe2"),(294,"sys_inotify_init1"),(295,"sys_preadv"),(296,"sys_pwritev"),(297,"sys_rt_tgsigqueueinfo"),(298,"sys_perf_event_open"),(299,"sys_recvmmsg"),(300,"sys_fanotify_init"),(301,"sys_fanotify_mark"),(302,"sys_prlimit64"),(303,"sys_name_to_handle_at"),(304,"sys_open_by_handle_at"),(305,"sys_clock_adjtime"),(306,"sys_syncfs"),(307,"sys_sendmmsg"),(308,"sys_setns"),(309,"sys_getcpu"),(310,"sys_process_vm_readv"),(311,"sys_process_vm_writev")],
                'type': TYPE_EQUAL
            }
        }
    }
}

def FIND(key, hint): return key.lower().find(hint.lower()) > -1

def magic(query, hints, match = FIND):
    ret = {}

    def match_all(keyword):
        if isinstance(hints, basestring):
            return match(keyword, hints)
        for hint in hints:
            if not match(keyword, hint):
                return False
        return True

    name = None
    number = None

    if isinstance(query, basestring):
        if query.startswith('0x'):
            try:
                number = int(query, 16)
            except:
                raise ValueError('bad magic number in hex')
        elif query.startswith('0b'):
            try:
                number = int(sys.argv[1], 2)
            except:
                raise ValueError('bad magic number in bin')
        else:
            try:
                number = int(query, 10)
            except:
                number = None
                name = query
    elif isinstance(query, (int, long)):
        number = query
    else:
        raise ValueError('query should be type number or string')

    def visit(obj, path):
        if 'flags' in obj and 'type' in obj:
            if not match_all(path): return
            bits = {}
            def get_one(f, value, tp):
                if name is not None:
                    if match(f, name):
                        bits[f] = value
                elif tp == TYPE_EQUAL:
                    if value == number:
                        bits[f] = value
                elif tp == TYPE_BITOR:
                    if value & number:
                        bits[f] = value

            if isinstance(obj['flags'][0], basestring):
                for f in obj['flags']:
                    try:
                        value = getattr(modules[module], f)
                        get_one(f, value, obj['type'])
                    except: pass
            else:       # tupple
                for value, f in obj['flags']:
                    get_one(f, value, obj['type'])
            if bits:
                ret[path] = bits
        else:
            for k in obj:
                visit(obj[k], path and path + '.' + k or k)
        
    # py magics
    modules = {}
    for module in py_magic:
        if module not in modules:
            modules[module] = __import__(module, globals())

        visit(py_magic[module], module)

    # magics

    visit(magics, '')

    return ret

def usage():
    print """
usage:
    $ magic.py (number|name) [keyword | [keyword] ...]

examples:
    $ magic.py 11 open
    $ magic.py 15 signal
    $ magic.py 10240 iflags
    $ magic.py SIGTERM signal
    $ magic.py creat open
    # list all consts in open
    $ magic.py '' open
"""
    
def main():
    number = 0
    if len(sys.argv) < 2:
        usage()
        sys.exit(0)
    try:
        rs = magic(sys.argv[1], sys.argv[2:])
    except ValueError as err:
        usage()
        sys.exit(10)
    if not rs:
        print '0ops, magic number not found :('
        return 0
    for k in rs:
        w = rs[k]
        sys.stdout.write(colored(k, 'yellow') + '\r\n')
        sys.stdout.write('    ' + colored(isinstance(w, (list, dict)) and ' | '.join(['%s = %d(0x%s)' % (k, w[k], format(w[k], 'x')) for k in w.keys()]) or ', '.join(w), 'cyan') + '\r\n')
        sys.stdout.flush()
    return 0

if __name__ == '__main__':
    sys.exit(main())

