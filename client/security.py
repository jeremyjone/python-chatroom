'''
@Author:jeremyjone
date:2018-5-4

Secure encryption,
a cryptographic operation for a password.
'''
from Crypto.Hash import MD5


def loop_encrypt(pwd, n=10):
    # Salt encrypt and recursion 10 times.
    salt = 'jeremyjone'
    md5_obj = MD5.new()
    md5_obj.update((pwd + salt).encode())
    # print(n, md5_obj.hexdigest())
    if n == 1:
        return md5_obj.hexdigest()
    return loop_encrypt(md5_obj.hexdigest(), n - 1)
