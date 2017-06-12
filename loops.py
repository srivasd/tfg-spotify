n = 1
while n < 5:
    print('n =', n)
    n = n + 1
print('While loop finished')

for n in range(1, 5):
    print('n =', n)
print('For loop finished')

for n in range(1, 4):
    for j in ['a', 'b', 'c']:
        print('n =', n, 'and j =', j)
