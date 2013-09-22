# pysectools

A small Python library that contains various security things.

## Usage

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

## Resources

- [Secure programming in Python](http://sourceforge.net/apps/trac/flexpw/wiki/PySecure) -- this library implements things described there
- [Secure Programming for Linux and Unix HOWTO](http://www.dwheeler.com/secure-class/Secure-Programs-HOWTO/index.html) -- the classic book
- [PyNaCl](https://github.com/dstufft/pynacl) -- all the crypto you need
- [py-scrypt](https://bitbucket.org/mhallin/py-scrypt/src) -- derive crypto keys from passwords
- [passlib](http://pythonhosted.org/passlib/) -- general password hashing library
- [pyotp](https://github.com/nathforge/pyotp) -- two-factor auth is easy
- OWASP [Cheat Sheets](https://www.owasp.org/index.php/Cheat_Sheets) and [the Top Ten](https://www.owasp.org/index.php/Category:OWASP_Top_Ten_Project)
- [SSL/TLS Deployment Best Practices](https://www.ssllabs.com/downloads/SSL_TLS_Deployment_Best_Practices_1.3.pdf)

## License

Copyright © 2013 Greg V <floatboth@me.com>  
This work is free. You can redistribute it and/or modify it under the  
terms of the Do What The Fuck You Want To Public License, Version 2,  
as published by Sam Hocevar. See the COPYING file for more details.
