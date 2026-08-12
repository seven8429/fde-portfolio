print('你好，李铁')
print(ord('李'),chr(38081))
print('\u4e2d\u6587')
print(b'ABC'.decode('utf-8'),b'ABC'.decode('ascii'),b'ABC'.decode('latin-1'))
print(b'\xe4\xb8\xad\xe6\x96\x87'.decode('utf-8'),b'\xe4\xb8\xad\xe6\x96\x87'.decode('ascii',errors='ignore'),b'\xe4\xb8\xad\xe6\x96\x87'.decode('latin-1'))
print(len('你好'.encode('utf-8')))

print('hi, %s,you have $%d.'%('seven',10**9))
print('%2d-%03d'%(321,1))
print('%2f'% 3.1415926)
print('growth rate:%d %%' %(7))

print('Hello,{0},成绩提升了{1:.1f}%'.format('seven',68.25))

print('Hello,{name},成绩提升了{score}'.format(name='seven',score=25))

r=2.568
s=3.1415926*r**2
print('半径为：%.2f的圆面积为：%.2f'%(r,s))

s1=72
s2=85
r=(s2-s1)/s1*100
print('小明成绩提升了：%.1f%%'%(r))
print('小🌾成绩提升了：%.1f%%' % r)