def square(number):
    """Return the square of number."""
    sqr_num = number ** 2
    return sqr_num


input_num = 5
output_num = square(input_num)

print('Square result: ', output_num)


def return_difference(num1, num2):
    """Return the difference between two numbers.
        Subtracts n2 from n1."""
    return num1 - num2


print('Return difference result: ', return_difference(3, 5))


def add_two_numbers(num1, num2):
    """Return the add of two numbers (num1 and num2)."""
    res = num1 + num2
    return res

print('Return add two numbers: ', add_two_numbers(1, 5))


def cube(number):
    """Return the cube of number."""
    res = number ** 3
    return res

print('Return cube: ', cube(3))


def multiply(num1, num2):
    """Return the multiplication of two numbers (num1 and num2)."""
    res = num1 * num2
    return res

print('Return multiply', multiply(2, 9))






