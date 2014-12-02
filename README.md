# pysectools

A small Python library that contains various security things.

## Usage

```python
import pysectools
```

Prevent secrets from leaking out of your process's memory:

```python
pysectools.disallow_swap()
pysectools.disallow_core_dumps()
```

Drop privileges:

```python
pysectools.drop_privileges('username', 'groupname')
```

Securely erase a secret from memory (only on CPython):

```python
password = 'correct horse battery staple'
pysectools.zero(password)
# password == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
# \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
```

Enter a [Capsicum](http://www.cl.cam.ac.uk/research/security/capsicum/) sandbox (works out of the box on FreeBSD 10.0 and newer):

```python
b = open('before.txt', 'w')
pysectools.cap_enter()
b.write('hello from the sandbox!') # ok
open('after.txt', 'w').write('new file!') # IOError: [Errno 94] Not permitted in capability mode: 'after.txt'
```

Get a password safely using pinentry (usually comes with [GnuPG](https://www.gnupg.org/)) or [getpass](https://docs.python.org/2/library/getpass.html) if there's no pinentry:

```python
# all parameters are optional
pass = pysectools.pinentry(pinentry_path="/usr/local/bin/pinentry",
                           prompt="Enter your passphrase: ",
                           description="Launching the nuclear rocket",
                           validator=lambda x: x.startswith("correct horse"))
rocket.authorize(pass)
pysectools.zero(pass)
rocket.launch()
```

## Resources

- [Secure programming in Python](http://sourceforge.net/apps/trac/flexpw/wiki/PySecure) -- this library implements things described there
- [Secure Programming for Linux and Unix HOWTO](http://www.dwheeler.com/secure-class/Secure-Programs-HOWTO/index.html) -- the classic book
- [PyNaCl](https://github.com/pyca/pynacl) -- all the crypto you need
- [py-scrypt](https://bitbucket.org/mhallin/py-scrypt/src) -- derive crypto keys from passwords
- [passlib](http://pythonhosted.org/passlib/) -- general password hashing library
- [pyotp](https://github.com/nathforge/pyotp) -- two-factor auth is easy
- OWASP [Cheat Sheets](https://www.owasp.org/index.php/Cheat_Sheets) and [the Top Ten](https://www.owasp.org/index.php/Category:OWASP_Top_Ten_Project)
- [SSL/TLS Deployment Best Practices](https://www.ssllabs.com/downloads/SSL_TLS_Deployment_Best_Practices_1.3.pdf)

## License

Copyright © 2013-2014 Greg V <greg@unrelenting.technology>  
This work is free. You can redistribute it and/or modify it under the  
terms of the Do What The Fuck You Want To Public License, Version 2,  
as published by Sam Hocevar. See the COPYING file for more details.
