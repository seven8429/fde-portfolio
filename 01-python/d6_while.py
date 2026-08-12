#this is for loop example
names = ["Alice", "Bob", "Charlie", "David"]
for name in names:
    print(name)

sum = 0
for x in range(101):
    sum += x
print(sum)

total = 0
while total < 100:
    if total > 5:
        break
    total += 1
    print(total)

single = 0
while single < 10:
    single += 1
    if single % 2 == 0:
        continue
    print(single)