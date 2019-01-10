# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import getpass
import subprocess

try:
    # Python3 urllib
    from urllib.parse import unquote as urllib_unquote
except ImportError as err:
    # Python 2 urllib
    if str(err) != 'No module named parse':
        raise
    from urllib import unquote as urllib_unquote

def cmd_exists(cmd):
    return subprocess.call("type " + cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


class PinentryException(Exception): pass
class PinentryUnavailableException(PinentryException): pass
class PinentryClosedException(PinentryException): pass
class PinentryErrorException(PinentryException): pass


class Pinentry(object):

    def __init__(self, pinentry_path="pinentry", fallback_to_getpass=True):
        if not cmd_exists(pinentry_path):
            if fallback_to_getpass and os.isatty(sys.stdout.fileno()):
                self._ask = self._ask_with_getpass
                self._close = self._close_getpass
            else:
                raise PinentryUnavailableException()
        else:
            self.process = subprocess.Popen(pinentry_path,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT,
                                            close_fds=True)
            self._ask = self._ask_with_pinentry
            self._close = self._close_pinentry
        self._closed = False

    def ask(self, prompt="Enter the password: ", description=None,
            error="Wrong password!",
            validator=lambda x: x is not None):
        if self._closed:
            raise PinentryClosedException()
        return self._ask(prompt, description, error, validator)

    def close(self):
        self._closed = True
        return self._close()

    def _ask_with_getpass(self, prompt, description, error, validator):
        if description:
            print(description)
        password = None
        while not validator(password):
            if password is not None:
                print(error)
            password = getpass.getpass(prompt)
        return password

    def _close_getpass(self): pass

    def _ask_with_pinentry(self, prompt, description, error, validator):
        self._waitfor("OK")
        env = os.environ.get
        self._comm("OPTION lc-ctype=%s" % env("LC_CTYPE", env("LC_ALL", "en_US.UTF-8")))
        try:
            self._comm("OPTION ttyname=%s" % env("TTY", os.ttyname(sys.stdout.fileno())))
        except:
            pass
        if env('TERM'):
            self._comm("OPTION ttytype=%s" % env("TERM"))
        if prompt:
            self._comm("SETPROMPT %s" % self._esc(prompt))
        if description:
            self._comm("SETDESC %s" % self._esc(description))
        password = None
        while not validator(password):
            if password is not None:
                self._comm("SETERROR %s" % self._esc(error))
            password = self._comm_getpin()

        # Passphrase may contain percent-encoded entities
        # gpg/pinentry: pinentry/pinentry.c#L392 copy_and_escape
        # https://github.com/gpg/pinentry/blob/master/pinentry/pinentry.c#L392
        password = urllib_unquote(password)

        return password

    def _close_pinentry(self):
        return self.process.kill()

    def _waitfor(self, what):
        out = ""
        while not out.startswith(what):
            if out.startswith('ERR '):
                raise PinentryErrorException(out)
            out = self.process.stdout.readline().decode()
        return out

    def _comm(self, x):
        output = (x + "\n").encode()
        self.process.stdin.write(output)
        self.process.stdin.flush()
        self._waitfor("OK")

    def _comm_getpin(self):
        self.process.stdin.write("GETPIN\n".encode())
        self.process.stdin.flush()
        out = ""
        password = None
        while True:
            if out.startswith('ERR '):
                raise PinentryErrorException(out)
            out = self.process.stdout.readline().decode()
            if out.startswith('D '):
                password = out[2:].replace("\n", "")
            if out.startswith('OK'):
                break
        return password

    def _esc(self, x):
        return x.replace("%", "%25").replace("\n", "%0A")
