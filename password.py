from random import *

str1 = '0123456789'
str2 = 'qwertyuiopasdfghjklzxcvbnm'
str3 = str2.upper()

endStr = str1 + str2 + str3

paSd = list(endStr)

shuffle(paSd)

password1 = ''.join([choice(paSd) for _ in range(4)])
password2 = ''.join([choice(paSd) for _ in range(6)])
password3 = ''.join([choice(paSd) for _ in range(8)])
password4 = ''.join([choice(paSd) for _ in range(10)])
password5 = ''.join([choice(paSd) for _ in range(12)])
password6 = ''.join([choice(paSd) for _ in range(14)])
password7 = ''.join([choice(paSd) for _ in range(16)])
password8 = ''.join([choice(paSd) for _ in range(18)])
password9 = ''.join([choice(paSd) for _ in range(20)])
