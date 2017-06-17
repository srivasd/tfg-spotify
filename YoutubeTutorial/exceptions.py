
integer = input('Introduce an int number:')

try:
    integer = int(integer)
    print('Congratulations you have introduced an in number:', integer)
except ValueError:
    print('Error, you have not introduced an int number')
