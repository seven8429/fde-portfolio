family = ['father','mother','son','daughter']
print(family,len(family),family[3])
family.append('grandfather')
print(family)
family.insert(0,'grandmother')
print(family)
family.pop()
print(family)
family.insert(0,'grandfather')
print(family)
family.pop(0)
print(family)
family[0]='grandfather'
print(family)
family[3]=['big son','little son']
family[4]=['big daughter','little daughter']
print(family,len(family),family[3][0])

neighbors = ('women','cat','dog')
print(neighbors,len(neighbors),neighbors[2])
neighbors = list(neighbors)
neighbors.append('bird')
print(neighbors)
family.append(neighbors)
print(family)

L = [
    ['Apple', 'Google', 'Microsoft'],
    ['Java', 'Python', 'Ruby', 'PHP'],
    ['Adam', 'Bart', 'Bob']
]

#打印Apple
print(L[0][0])
#打印Python
print(L[1][1])
#打印Bob
print(L[2][2])