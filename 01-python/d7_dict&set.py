#dic

dic = {'name': 'John', 'age': 30, 'city': 'New York'}
print(dic['name'])  # Output: John
dic['age'] = 31  # Update age
dic['country'] = 'USA'  # Add new key-value pair
print(dic)  # Output: {'name': 'John', 'age': 31, 'city': 'New York', 'country': 'USA'}

#set

s = {1,2,3}
print(s)
s = set([1,2,3,3,2,1])
print(s)
s.add(666)
print(s)
s.remove(2)
print(s)

s1 = {168,157,1}
print(s & s1)
print(s | s1)

a = 'abc'
print(a.replace('a','666'))
print(a)