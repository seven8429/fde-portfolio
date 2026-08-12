#python data types 
print('python data types:')

a=10_000_000_000
print('a:',a,'type:',type(a))
print('a is int:',isinstance(a,int))
print('--------------------')

b=5.18*10**-9
print('b:',b,'type:',type(b))
print('b is float:',isinstance(b,float))
print('--------------------')

c="hello everyone, welcome to python programming. I'm happy to see you all here. I\'m sure you wiil say \"OK\""
print('c:',c,'type:',type(c))
print('c is string:',isinstance(c,str))
print(r'\\\daho\\')
print('''line1
line2
line3''')
print(r'''hello ,\n world''')
print('--------------------')

d=True
print('d:',d,'type:',type(d))
print('d is bool:',isinstance(d,bool))
print('--------------------')

if d and a>b:
    print('a is greater than b is true')
else:
    print('a is greater than b is false')

e=None
print('e:',e,'type:',type(e))
print('e is None:',isinstance(e,type(None)))
print('--------------------')

f=1
f+=2
g='007'
g1=g
g='008'
h=True
PI=3.141592653
print(f,g,g1,h,PI,9/3,10//3,10%3,10**3)

n=123
f1=456.789
s1='Hello,world'
s2='Hello,\'Adam\''
s3=r'Hello,"bro"'
s4=r'''Hello,
world'''
print(n,f1,s1,s2,s3,s4)