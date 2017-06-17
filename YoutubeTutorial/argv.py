import sys

print('Every arguments of the command line:', sys.argv)

print('The name of the script python which is executing now is:', sys.argv[0])

print('***Program to mult 2 numbers***\n\n')

number1 = sys.argv[1]
number2 = sys.argv[2]

try:
    number1 = float(number1)
    number2 = float(number2)
    total = number1 * number2
    print('The result is:', total)
except ValueError:
    print('Error. The arguments to mult must be numbers.')
