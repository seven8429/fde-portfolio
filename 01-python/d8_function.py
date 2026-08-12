#调用函数
print(abs(-9))
n1 = 255
n2 = 1000
print(hex(n1),hex(n2))

#定义函数
def my_func(n):
      if not isinstance(n,(int,float)):
            raise TypeError('Bad input type!')
            print('')
      if n > 0:
            return 'you input a positive number!'
      else:
            return 'you input a negative number!'

print(my_func(int('666')))

import math
#return more than one value
def circle_area_length(r):
      if not isinstance(r,(int,float)):
            raise TypeError('input bad args')
      if r > 0:
            return 'area is :' + str(math.pi*r*r) , 'length is :' + str(2*math.pi*r)
      else :
            raise TypeError('input a negetive number!!!')

print(circle_area_length(6))

#定义一个函数quadratic(a, b, c)，接收3个参数，返回一元二次方程 ax2+bx+c=0ax2+bx+c=0 的两个解
def quadratic(a,b,c):
      if not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not isinstance(c,(int,float)) or a<0 or b<0 or c<0:
            raise TypeError('please input pisitive number!')
      else:
            #result = (-b+math.sqrt((b*b-4*a*c)))/(2*a)
            return -b+math.sqrt((b*b-4*a*c))/(2*a) , -b-math.sqrt((b*b-4*a*c))/(2*a)

print(quadratic(1,3,2))

#5 type args function
def mul(x,y):
      return x*y
print('mul(5)=',mul(5,6))

#递归函数
def fact(n):
      if n == 1:
            return 1
      else:
            return n * fact(n - 1)

print(fact(5))

#练习，汉诺塔游戏
def tower_move(n,a,b,c):
      if n == 1:
            print(a,'-->',c)
      else:
            tower_move(n-1,a,c,b)
            print(a,'-->',c)
            tower_move(n-1,b,a,c)

print (tower_move(3,'A','B','C'))