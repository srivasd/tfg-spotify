def greeting():
    return 'Hello world'


print(greeting())


def write(string):
    return string


print(write(input('Type an string:')))


def multiply(num1, num2):
    total = num1 * num2
    return total


print(multiply(2, 5))


def add(num1, num2=0):
    total = num1 + num2
    return total


print(add(33))
print(add(22, 6))


def array(arr):
    result = ''
    for value in arr:
        result += str(value)
    return result


print(array([1, 2, 4, 5, '7']))


def arguments(*arg):
    for var in arg:
        print(var, end=' ')

arguments(1, 2, 'hello', 3.15, 'world', 'python\n')

subtract = lambda num, num2: num - num2

print(subtract(10, 5))

