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

"Review 1"
for n in range(2, 11):
    print('n = ', n)
print('Loop 1 finished')

"Review 2"
x = 2
while x < 11:
    print('x = ', x)
    x = x + 1
print('Loop 2 finished')

"Review 3"


def doubles(number):
    print('Doubles: ')
    for n in range(1, 4):
        number = number * 2
        print(number)

print(doubles(2))
